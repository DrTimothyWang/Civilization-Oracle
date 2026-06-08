"""
MetaCogAgent — 元认知层
=========================
v2.6: 无元认知，QCAgent 事后检测
v3.0: MetaCogAgent 实时自省，提前预警

核心能力：
1. 复合信心评估（Composite Confidence Scoring）
2. 实时冲突检测（Consistency Threshold < 0.7 → 人工审核）
3. 自我校准（输出不确定时主动请求上游 Agent 补充信息）

参考：MetaMind (NeurIPS 2025) 三阶段元认知多智能体协作
"""

from dataclasses import dataclass
from typing import Any, Optional
import numpy as np


@dataclass
class ConfidenceReport:
    """置信度报告"""

    score: float  # 0-1
    factors: dict[str, float]  # 各维度得分
    verdict: str  # "accept" | "retry" | "escalate"
    reason: str
    suggestions: list[str]


class MetaCogAgent:
    """
    元认知 Agent
    对各 Agent 输出进行复合信心评估
    """

    # 各维度权重
    WEIGHTS = {
        "consistency": 0.25,  # 跨模态一致性
        "coverage": 0.20,  # 数据覆盖率
        "calibration": 0.25,  # 校准度（PSI 在合理范围）
        "freshness": 0.15,  # 数据新鲜度
        "diversity": 0.15,  # 样本多样性
    }

    def __init__(self, consistency_threshold: float = 0.7):
        self.consistency_threshold = consistency_threshold

    def evaluate(self, agent_name: str, output: Any) -> ConfidenceReport:
        """
        评估 Agent 输出置信度

        输出结构：
        {
            "score": 0.0-1.0,
            "factors": {维度: 得分},
            "verdict": "accept"|"retry"|"escalate",
            "reason": str,
            "suggestions": [str]
        }
        """
        if agent_name == "TextAnalystAgent":
            return self._evaluate_sentiment(output)
        elif agent_name == "DataIngestAgent":
            return self._evaluate_data(output)
        elif agent_name == "QCAgent":
            return self._evaluate_quality(output)
        elif agent_name == "PredictorAgent":
            return self._evaluate_prediction(output)
        else:
            return self._default_evaluate(output)

    def _evaluate_sentiment(self, output: Any) -> ConfidenceReport:
        """评估情感分析输出"""
        factors = {}

        # 校准度：PSI 在 [-1, 1] 范围内
        if isinstance(output, dict) and "avg_sentiment" in output:
            sent = output["avg_sentiment"]
            if -1 <= sent <= 1:
                factors["calibration"] = 1.0 - abs(sent) * 0.1
            else:
                factors["calibration"] = 0.0
        else:
            factors["calibration"] = 0.5

        # 覆盖率
        if isinstance(output, dict) and "n_texts" in output:
            n = output["n_texts"]
            factors["coverage"] = min(1.0, n / 50)
        else:
            factors["coverage"] = 0.5

        # 一致性
        if isinstance(output, dict) and "sentiments" in output:
            sents = output["sentiments"]
            if len(sents) > 1:
                variance = np.std(sents)
                factors["consistency"] = max(0.0, 1.0 - variance)
            else:
                factors["consistency"] = 0.8
        else:
            factors["consistency"] = 0.6

        # 多样性
        if isinstance(output, dict) and "sentiments" in output:
            sents = output["sentiments"]
            factors["diversity"] = (
                min(1.0, len(set(round(s, 1) for s in sents)) / 5)
                if sents
                else 0.0
            )
        else:
            factors["diversity"] = 0.5

        factors["freshness"] = 0.8  # 默认值，简化

        # 加权总分
        score = sum(self.WEIGHTS[k] * factors.get(k, 0.5) for k in self.WEIGHTS)

        # 判断
        if score >= self.consistency_threshold:
            verdict = "accept"
            reason = f"置信度 {score:.2f} ≥ 阈值 {self.consistency_threshold}"
            suggestions = []
        else:
            verdict = "retry"
            reason = f"置信度 {score:.2f} < 阈值 {self.consistency_threshold}"
            suggestions = [
                "增加样本量",
                "检查异常值",
                "确认 API 调用是否成功",
            ]

        return ConfidenceReport(
            score=round(score, 4),
            factors={k: round(v, 4) for k, v in factors.items()},
            verdict=verdict,
            reason=reason,
            suggestions=suggestions,
        )

    def _evaluate_data(self, output: Any) -> ConfidenceReport:
        """评估数据导入输出"""
        factors = {}

        if isinstance(output, dict):
            n = output.get("n_experts", 0)
            factors["coverage"] = min(1.0, n / 1000)
            factors["calibration"] = 1.0 if n > 0 else 0.0
            factors["consistency"] = 0.8 if n > 100 else 0.4
            factors["diversity"] = 0.7
            factors["freshness"] = 0.8
        else:
            factors = {k: 0.5 for k in self.WEIGHTS}

        score = sum(self.WEIGHTS[k] * factors.get(k, 0.5) for k in self.WEIGHTS)
        verdict = "accept" if score >= self.consistency_threshold else "retry"
        return ConfidenceReport(
            score=round(score, 4),
            factors={k: round(v, 4) for k, v in factors.items()},
            verdict=verdict,
            reason=f"数据质量置信度: {score:.2f}",
            suggestions=["扩大时间窗口"] if verdict == "retry" else [],
        )

    def _evaluate_quality(self, output: Any) -> ConfidenceReport:
        """评估质量审计输出"""
        factors = {}

        if isinstance(output, dict):
            all_passed = output.get("all_passed", False)
            n_contradictions = output.get("n_contradictions", 0)
            factors["calibration"] = 1.0 if all_passed else max(0.0, 1.0 - n_contradictions * 0.2)
            factors["consistency"] = 1.0 if n_contradictions == 0 else 0.5
            factors["coverage"] = 0.8
            factors["diversity"] = 0.7
            factors["freshness"] = 0.8
        else:
            factors = {k: 0.5 for k in self.WEIGHTS}

        score = sum(self.WEIGHTS[k] * factors.get(k, 0.5) for k in self.WEIGHTS)
        verdict = "accept" if score >= self.consistency_threshold else "escalate"
        return ConfidenceReport(
            score=round(score, 4),
            factors={k: round(v, 4) for k, v in factors.items()},
            verdict=verdict,
            reason=f"质量审计置信度: {score:.2f}" + ("（全部通过）" if verdict == "accept" else "（需人工审核）"),
            suggestions=["检查矛盾规则触发原因"] if verdict == "escalate" else [],
        )

    def _evaluate_prediction(self, output: Any) -> ConfidenceReport:
        """评估预测输出"""
        factors = {}

        if isinstance(output, dict):
            has_confidence = "confidence" in output or "ci" in output
            factors["calibration"] = 1.0 if has_confidence else 0.5
            factors["consistency"] = 0.7
            factors["coverage"] = 0.7
            factors["diversity"] = 0.8  # 情景多样性
            factors["freshness"] = 0.8
        else:
            factors = {k: 0.5 for k in self.WEIGHTS}

        score = sum(self.WEIGHTS[k] * factors.get(k, 0.5) for k in self.WEIGHTS)
        verdict = "accept" if score >= self.consistency_threshold else "retry"
        return ConfidenceReport(
            score=round(score, 4),
            factors={k: round(v, 4) for k, v in factors.items()},
            verdict=verdict,
            reason=f"预测置信度: {score:.2f}",
            suggestions=["扩大训练数据"] if verdict == "retry" else [],
        )

    def _default_evaluate(self, output: Any) -> ConfidenceReport:
        """默认评估（未知 Agent 类型）"""
        score = 0.6 if output is not None else 0.0
        return ConfidenceReport(
            score=score,
            factors={k: 0.6 for k in self.WEIGHTS},
            verdict="retry" if score < self.consistency_threshold else "accept",
            reason="默认评估",
            suggestions=[],
        )


def demo_metacognition():
    """演示 MetaCogAgent 评估各 Agent 输出"""
    agent = MetaCogAgent(consistency_threshold=0.7)

    test_outputs = [
        (
            "TextAnalystAgent",
            {
                "dynasty": "明朝",
                "n_texts": 50,
                "avg_sentiment": 0.62,
                "sentiments": [0.5, 0.7, 0.8, 0.6, 0.65],
            },
        ),
        (
            "QCAgent",
            {"all_passed": True, "n_contradictions": 0},
        ),
        (
            "QCAgent",
            {"all_passed": False, "n_contradictions": 3},
        ),
    ]

    print("=" * 60)
    print("MetaCogAgent 置信度评估演示")
    print("=" * 60)

    for agent_name, output in test_outputs:
        report = agent.evaluate(agent_name, output)
        icon = "✅" if report.verdict == "accept" else "⚠" if report.verdict == "retry" else "🚨"
        print(f"\n{icon} {agent_name}: score={report.score:.2f} ({report.verdict})")
        print(f"  原因: {report.reason}")
        print(f"  维度: {report.factors}")
        if report.suggestions:
            print(f"  建议: {report.suggestions}")
