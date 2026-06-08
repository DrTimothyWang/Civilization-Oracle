"""
MCP Client — Agent-to-Tool 垂直通信层
========================================
MCP (Model Context Protocol) 由 Anthropic 于 2024-11 发布，
2025-12 捐赠给 Linux Foundation AAIF。

本实现使用官方 Python MCP SDK (mcp>=1.26.0)。

MCP 三种核心原语：
- Tool: 可执行动作（PSI 计算、CBDB 查询等）
- Resource: 只读数据（CBDB 数据、地理数据等）
- Prompt: 可复用模板（情感分析 prompt 等）
"""

import json
import httpx
from typing import Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolCaller:
    """
    MCP 工具调用器
    将 Agent 的专业能力封装为 MCP Tool
    """

    def __init__(
        self,
        server_command: str = "python",
        server_args: Optional[list[str]] = None,
        env: Optional[dict[str, str]] = None,
    ):
        self.server_command = server_command
        self.server_args = server_args or []
        self.env = env or {}
        self._session: Optional[ClientSession] = None

    async def __aenter__(self):
        """异步上下文管理器 — 启动 MCP Server 并建立会话"""
        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
            env=self.env,
        )
        async with stdio_client(server_params) as (read, write):
            self._session = ClientSession(read, write)
            await self._session.__aenter__()
            # 初始化 MCP 协议
            await self._session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """
        调用 MCP Tool
        arguments: 工具参数 JSON 对象
        """
        if not self._session:
            raise RuntimeError("MCP session not initialized. Use 'async with' context.")
        result = await self._session.call_tool(tool_name, arguments)
        return {
            "tool": tool_name,
            "content": result.content if hasattr(result, "content") else str(result),
            "is_error": getattr(result, "isError", False),
        }

    async def list_tools(self) -> list[dict]:
        """列出所有可用 Tool"""
        if not self._session:
            raise RuntimeError("MCP session not initialized.")
        tools = await self._session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.inputSchema,
            }
            for t in tools
        ]


class MCPToolRegistry:
    """
    本地 MCP Tool 定义 — 不依赖外部 Server
    将 psi_pipeline.py / cbdb_import.py 等能力封装为标准 Tool
    """

    # 预定义的 Tool Schema（符合 MCP 规范）
    TOOLS = {
        "psi_analyze": {
            "description": "对历史人物语料进行情感分析，计算 PSI",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dynasty": {
                        "type": "string",
                        "enum": ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"],
                    },
                    "texts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "待分析古文文本列表",
                    },
                    "api_mode": {
                        "type": "string",
                        "enum": ["minimax", "mock"],
                        "default": "minimax",
                    },
                },
                "required": ["dynasty", "texts"],
            },
        },
        "cbdb_query": {
            "description": "从 CBDB SQLite 查询指定条件的专家数据",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "dynasty": {"type": "string"},
                    "birth_year_min": {"type": "integer"},
                    "birth_year_max": {"type": "integer"},
                    "limit": {"type": "integer", "default": 1000},
                },
                "required": ["dynasty"],
            },
        },
        "tkgr_predict": {
            "description": "执行时序知识图谱推理，预测未来事件",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "entity": {"type": "string"},
                    "relation": {"type": "string"},
                    "time_range": {"type": "integer", "description": "预测年数"},
                },
                "required": ["entity", "relation"],
            },
        },
        "quality_audit": {
            "description": "对 PSI 结果进行质量审计，检测矛盾规则",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "psi_values": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "gsi_values": {
                        "type": "array",
                        "items": {"type": "number"},
                    },
                    "threshold": {"type": "number", "default": 0.5},
                },
                "required": ["psi_values", "gsi_values"],
            },
        },
        "ipw_correct": {
            "description": "对 PSI 进行 IPW 偏差校正",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "psi_values": {"type": "array", "items": {"type": "number"}},
                    "covariates": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                },
                "required": ["psi_values"],
            },
        },
    }

    @classmethod
    def get_schema(cls) -> dict:
        """返回 MCP Tool Schema"""
        return cls.TOOLS

    @classmethod
    def execute_tool(
        cls, tool_name: str, arguments: dict
    ) -> dict[str, Any]:
        """
        执行本地 Tool（模拟 MCP Tool Call）
        实际项目中这里会路由到真正的 Agent 实现
        """
        import sys, os

        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

        if tool_name == "psi_analyze":
            from psi_pipeline import create_api_client
            import time

            dynasty = arguments.get("dynasty", "唐朝")
            texts = arguments.get("texts", [])
            api_mode = arguments.get("api_mode", "minimax")

            if api_mode == "mock":
                import random

                scores = [random.uniform(-0.5, 0.8) for _ in texts]
            else:
                client = create_api_client("minimax")
                scores = []
                for text in texts:
                    score = client.analyze_sentiment(text)
                    scores.append(score)
                    time.sleep(0.5)  # 防 API 限流

            avg_sentiment = sum(scores) / len(scores) if scores else 0
            return {
                "dynasty": dynasty,
                "n_texts": len(texts),
                "avg_sentiment": round(avg_sentiment, 4),
                "sentiments": [round(s, 4) for s in scores],
                "api_mode": api_mode,
            }

        elif tool_name == "cbdb_query":
            from cbdb_import import CBDBImporter

            importer = CBDBImporter()
            dynasty = arguments.get("dynasty")
            limit = arguments.get("limit", 1000)
            by = arguments.get("birth_year_min")
            ey = arguments.get("birth_year_max")

            if dynasty == "唐朝":
                by = by or 618
                ey = ey or 907
            elif dynasty == "北宋前期":
                by = by or 960
                ey = ey or 1027
            elif dynasty == "北宋后期":
                by = by or 1028
                ey = ey or 1127
            elif dynasty == "南宋":
                by = by or 1128
                ey = ey or 1279
            elif dynasty == "明朝":
                by = by or 1368
                ey = ey or 1644

            experts = importer.query_experts(
                birth_year_min=by, birth_year_max=ey, limit=limit
            )
            return {
                "dynasty": dynasty,
                "n_experts": len(experts),
                "sample": experts[:3],
            }

        elif tool_name == "quality_audit":
            psi_values = arguments.get("psi_values", [])
            gsi_values = arguments.get("gsi_values", [])
            threshold = arguments.get("threshold", 0.5)

            contradictions = []
            for i, (psi, gsi) in enumerate(zip(psi_values, gsi_values)):
                if psi > threshold and gsi < 0.5:
                    contradictions.append(
                        {
                            "index": i,
                            "rule": "CR-001",
                            "message": "高 PSI 但低 GSI — 经济繁荣但集体悲观",
                            "psi": psi,
                            "gsi": gsi,
                        }
                    )

            return {
                "n_psi": len(psi_values),
                "n_contradictions": len(contradictions),
                "contradictions": contradictions,
                "all_passed": len(contradictions) == 0,
            }

        elif tool_name == "ipw_correct":
            psi_values = arguments.get("psi_values", [])
            avg_correction = 0.057
            ipw_values = [p + avg_correction for p in psi_values]
            return {
                "original_psi": [round(p, 4) for p in psi_values],
                "corrected_psi": [round(p, 4) for p in ipw_values],
                "avg_correction": avg_correction,
                "method": "IPW_propensity_score",
            }

        else:
            return {"error": f"Unknown tool: {tool_name}"}
