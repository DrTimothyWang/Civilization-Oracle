"""
Hub-and-Spoke Orchestrator + 迭代闭环反馈机制
==============================================
v2.6: 纯层级 DAG，无反馈，单点故障风险高
v3.0: Hub-and-Spoke + 迭代闭环

核心设计：
1. MasterOrchestrator 作为 Hub，所有 Agent 通过它协调
2. MetaCogAgent 注入反馈回路：置信度 < threshold 时触发重试
3. 迭代闭环可中和 40%+ 故障（MAS-FIRE 研究）
4. 支持动态 Agent 拓扑（运行时根据任务复杂度调整）
"""

import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional
from .mcp_client import MCPToolRegistry
from .a2a_client import TaskStatus


class OrchestrationMode(str, Enum):
    """编排模式"""

    LINEAR = "linear"  # v2.6 模式，固定 DAG
    ITERATIVE = "iterative"  # v3.0 模式，带反馈循环
    ADAPTIVE = "adaptive"  # v3.0 模式，根据任务复杂度动态选择


@dataclass
class PipelineStep:
    """Pipeline 步骤定义"""

    step_id: str
    agent_name: str
    skill_id: str
    input_map: dict[str, str]  # {local_var: upstream_step.output_key}
    output_key: str
    confidence_threshold: float = 0.7
    max_retries: int = 3
    dependencies: list[str] = field(default_factory=list)


@dataclass
class StepResult:
    """步骤执行结果"""

    step_id: str
    agent_name: str
    status: str  # "success" | "retry" | "failed" | "escalated"
    output: Any
    confidence: float
    attempts: int
    latency_ms: float
    error: Optional[str] = None


class HubAndSpokeOrchestrator:
    """
    Hub-and-Spoke 编排器
    所有 Agent 通过 Master Orchestrator（Hub）协调

    v3.0 新机制：
    - 迭代闭环：MetaCogAgent 评估置信度 → 不合格则重试
    - 冲突升级：三次重试仍不合格 → 升级人工审核
    - 自适应模式：根据任务复杂度选择 LINEAR / ITERATIVE / ADAPTIVE
    """

    def __init__(self, mode: OrchestrationMode = OrchestrationMode.ITERATIVE):
        self.mode = mode
        self._results: dict[str, Any] = {}
        self._step_results: dict[str, StepResult] = {}

    def define_pipeline(self, steps: list[PipelineStep]) -> list[PipelineStep]:
        """定义 Pipeline 步骤序列"""
        self._steps = steps
        return steps

    def resolve_inputs(self, step: PipelineStep) -> dict[str, Any]:
        """根据 input_map 解析步骤输入"""
        inputs = {}
        for local_var, upstream_ref in step.input_map.items():
            if ":" in upstream_ref:
                src_step, output_key = upstream_ref.split(":", 1)
                if src_step in self._results:
                    inputs[local_var] = self._results[src_step].get(output_key)
                else:
                    inputs[local_var] = None
            else:
                # 全局常量
                inputs[local_var] = self._results.get(upstream_ref)
        return inputs

    def run(self, initial_input: dict[str, Any]) -> dict[str, Any]:
        """
        执行 Pipeline

        v3.0 迭代闭环逻辑：
        for each step in pipeline:
            for attempt in range(max_retries):
                result = execute_step(step)
                confidence = metacog_evaluate(result)
                if confidence >= threshold:
                    store_result; break
                else:
                    retry with feedback
            if all retries failed:
                escalate to human review
        """
        self._results = {"__input": initial_input}
        print(f"\n[HubAndSpoke] Starting pipeline in {self.mode.value} mode")
        print(f"[HubAndSpoke] Steps: {len(self._steps)}")
        print("=" * 60)

        for step in self._steps:
            print(f"\n[→] Step: {step.step_id} ({step.agent_name})")
            t0 = time.time()

            inputs = self.resolve_inputs(step)
            attempts = 0
            final_result: Optional[StepResult] = None

            while attempts < step.max_retries:
                attempts += 1
                output, status = self._execute_step(step, inputs, attempts)

                # 计算置信度（简化版，实际走 MetaCogAgent）
                confidence = self._assess_confidence(output, status, attempts)
                print(f"  Attempt {attempts}: {status} (confidence={confidence:.2f})")

                if confidence >= step.confidence_threshold:
                    final_result = StepResult(
                        step_id=step.step_id,
                        agent_name=step.agent_name,
                        status="success",
                        output=output,
                        confidence=confidence,
                        attempts=attempts,
                        latency_ms=(time.time() - t0) * 1000,
                    )
                    break
                elif attempts < step.max_retries:
                    print(f"  ⚠ Confidence {confidence:.2f} < {step.confidence_threshold}, retrying...")
                    # 注入反馈：增加一些随机性模拟 MetaCogAgent 建议
                    inputs = self._apply_feedback(inputs, output)
                else:
                    final_result = StepResult(
                        step_id=step.step_id,
                        agent_name=step.agent_name,
                        status="escalated",
                        output=output,
                        confidence=confidence,
                        attempts=attempts,
                        latency_ms=(time.time() - t0) * 1000,
                        error="Confidence threshold not met after max retries",
                    )

            if final_result is None:
                final_result = StepResult(
                    step_id=step.step_id,
                    agent_name=step.agent_name,
                    status="failed",
                    output=None,
                    confidence=0.0,
                    attempts=attempts,
                    latency_ms=(time.time() - t0) * 1000,
                    error="Max retries exceeded",
                )

            self._results[step.step_id] = (
                final_result.output if final_result.output else {}
            )
            self._step_results[step.step_id] = final_result

            elapsed = (time.time() - t0) * 1000
            status_icon = "✅" if final_result.status == "success" else "⚠" if final_result.status == "escalated" else "❌"
            print(f"  {status_icon} {step.step_id} done in {elapsed:.0f}ms (attempts={final_result.attempts})")

        print("\n" + "=" * 60)
        print(f"[HubAndSpoke] Pipeline complete")
        self._print_summary()
        return self._results

    def _execute_step(
        self, step: PipelineStep, inputs: dict, attempt: int
    ) -> tuple[Any, str]:
        """执行单个步骤"""
        try:
            # 构造 Tool 参数
            tool_args = {k: v for k, v in inputs.items() if v is not None}
            output = MCPToolRegistry.execute_tool(step.skill_id, tool_args)
            return output, "success"
        except Exception as e:
            return {"error": str(e)}, "failed"

    def _assess_confidence(
        self, output: Any, status: str, attempt: int
    ) -> float:
        """
        评估输出置信度（简化版）
        完整实现应路由到 MetaCogAgent
        """
        if status == "failed":
            return 0.0
        if isinstance(output, dict) and "error" in output:
            return 0.3
        # 重试次数越多，置信度越低（压力退化）
        base = 0.85
        penalty = (attempt - 1) * 0.15
        return max(0.0, base - penalty)

    def _apply_feedback(
        self, inputs: dict, failed_output: Any
    ) -> dict[str, Any]:
        """
        应用 MetaCogAgent 反馈，生成调整后的输入
        简化版：增加一些随机扰动
        """
        import random

        adjusted = dict(inputs)
        # 模拟 MetaCogAgent 发现问题后建议调整输入
        if isinstance(failed_output, dict) and "avg_sentiment" in failed_output:
            # 情感分析失败 → 增加样本量
            adjusted["n_samples"] = adjusted.get("n_samples", 10) + 5
        return adjusted

    def _print_summary(self) -> None:
        """打印 Pipeline 执行摘要"""
        total = len(self._step_results)
        succeeded = sum(
            1 for r in self._step_results.values() if r.status == "success"
        )
        escalated = sum(
            1 for r in self._step_results.values() if r.status == "escalated"
        )
        total_ms = sum(r.latency_ms for r in self._step_results.values())

        print(f"  成功: {succeeded}/{total}")
        if escalated:
            print(f"  ⚠ 升级人工审核: {escalated} 个步骤")
        print(f"  总耗时: {total_ms/1000:.1f}s")


def demo_psi_pipeline() -> None:
    """
    演示：运行 v3.0 PSI 分析 Pipeline
    覆盖 DataIngest → TextAnalyst → QC → IPW 四个步骤
    """

    orchestrator = HubAndSpokeOrchestrator(mode=OrchestrationMode.ITERATIVE)

    steps = [
        PipelineStep(
            step_id="data_ingest",
            agent_name="DataIngestAgent",
            skill_id="cbdb_query",
            input_map={},
            output_key="experts",
            confidence_threshold=0.7,
            dependencies=[],
        ),
        PipelineStep(
            step_id="text_analysis",
            agent_name="TextAnalystAgent",
            skill_id="psi_analyze",
            input_map={
                "dynasty": "data_ingest:dynasty",
                "texts": "data_ingest:texts",
                "api_mode": "__input:api_mode",
            },
            output_key="avg_sentiment",
            confidence_threshold=0.75,
            dependencies=["data_ingest"],
        ),
        PipelineStep(
            step_id="quality_audit",
            agent_name="QCAgent",
            skill_id="quality_audit",
            input_map={
                "psi_values": "text_analysis:psi_values",
                "gsi_values": "data_ingest:gsi_values",
            },
            output_key="all_passed",
            confidence_threshold=0.8,
            dependencies=["text_analysis", "data_ingest"],
        ),
        PipelineStep(
            step_id="ipw_correction",
            agent_name="KGraphAgent",
            skill_id="ipw_correct",
            input_map={"psi_values": "text_analysis:sentiments"},
            output_key="corrected_psi",
            confidence_threshold=0.7,
            dependencies=["text_analysis"],
        ),
    ]

    orchestrator.define_pipeline(steps)

    # 构造初始输入
    initial = {
        "dynasty": "明朝",
        "api_mode": "mock",  # mock 模式快速演示
    }

    results = orchestrator.run(initial)
    return results
