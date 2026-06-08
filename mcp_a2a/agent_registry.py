"""
Agent Registry & Agent Card (A2A v1.0 规范)
==============================================
Agent Card 是 A2A 协议的核心发现机制：
- URI: /.well-known/agent.json
- JSON 格式的机器可读"数字名片"
- 支持动态服务发现，无需硬编码地址

v3.0 变更：
- v2.6: 各 Agent 信息硬编码在 orchestrator
- v3.0: 各 Agent 通过 Agent Card 动态注册/发现
"""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class AgentCard:
    """
    A2A Agent Card — 符合 A2A v1.0 规范
    https://developers.google.com/a2a
    """

    def __init__(
        self,
        name: str,
        description: str,
        version: str,
        capabilities: dict,
        skills: list[dict],
        authentication: dict,
        endpoint: str,
        metadata: Optional[dict] = None,
    ):
        self.name = name
        self.description = description
        self.version = version
        self.capabilities = capabilities  # streaming, pushNotifications, stateDiff, ...
        self.skills = skills  # [{id, name, description, tags, inputModes, outputModes}]
        self.authentication = authentication  # {type: "oauth2"|"api_key"|"none"}
        self.endpoint = endpoint
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "skills": self.skills,
            "authentication": self.authentication,
            "endpoint": self.endpoint,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                **self.metadata,
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        print(f"[✓] Agent Card saved: {path}")

    @classmethod
    def from_dict(cls, data: dict) -> "AgentCard":
        return cls(
            name=data["name"],
            description=data["description"],
            version=data["version"],
            capabilities=data["capabilities"],
            skills=data["skills"],
            authentication=data["authentication"],
            endpoint=data["endpoint"],
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def load(cls, path: Path | str) -> "AgentCard":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


class AgentRegistry:
    """
    Agent 注册中心 — 管理所有 Agent Card
    支持：
    - 本地注册（文件系统）
    - 远程发现（HTTP GET .well-known/agent.json）
    - 动态订阅（A2A push notifications）
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".well-known")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cards: dict[str, AgentCard] = {}

    def register(self, card: AgentCard) -> None:
        """注册一个 Agent Card"""
        self._cards[card.name] = card
        card_path = self.storage_dir / card.name / ".well-known" / "agent.json"
        card.save(card_path)
        print(f"[✓] Agent registered: {card.name} → {card_path}")

    def discover(self, agent_name: str) -> Optional[AgentCard]:
        """发现指定 Agent（本地优先，远程兜底）"""
        if agent_name in self._cards:
            return self._cards[agent_name]
        # 尝试从文件系统加载
        card_path = self.storage_dir / agent_name / ".well-known" / "agent.json"
        if card_path.exists():
            card = AgentCard.load(card_path)
            self._cards[agent_name] = card
            return card
        return None

    def discover_all(self) -> list[AgentCard]:
        """发现所有已注册的 Agent"""
        return list(self._cards.values())

    def list_agents(self) -> list[str]:
        """列出所有已注册 Agent 名称"""
        return list(self._cards.keys())


def build_agent_cards() -> dict[str, AgentCard]:
    """
    构建 Civilization-Oracle v3.0 全部 Agent Card
    共 7 个专业 Agent + 1 个元认知 Agent
    """

    CARDS = {
        "DataIngestAgent": AgentCard(
            name="DataIngestAgent",
            description="多源异构数据统一入口。负责从 CBDB/CHGIS/CTEXT 采集数据，清洗并输出标准 JSON。",
            version="3.0.0",
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateDiff": False,
            },
            skills=[
                {
                    "id": "cbdb_ingest",
                    "name": "CBDB数据导入",
                    "description": "从 CBDB SQLite 导出指定朝代人物数据，关联地理坐标",
                    "tags": ["cbdb", "sqlite", "historical_data"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
                {
                    "id": "ctext_fetch",
                    "name": "CTEXT语料获取",
                    "description": "从 CTEXT API 获取指定朝代的古典文献文本",
                    "tags": ["ctext", "corpus", "classical_chinese"],
                    "inputModes": ["application/json"],
                    "outputModes": ["text/plain"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8001/a2a",
            metadata={"four_diagnosis": "闻", "role": "data"},
        ),
        "GeoEncoderAgent": AgentCard(
            name="GeoEncoderAgent",
            description="古今地名映射与空间数据标准化。将历史地名编码为现代地理坐标，支持 CHGIS/CNHGIS。",
            version="3.0.0",
            capabilities={"streaming": False, "pushNotifications": False, "stateDiff": False},
            skills=[
                {
                    "id": "place_standardization",
                    "name": "古今地名标准化",
                    "description": "将古地名映射为现代经纬度坐标",
                    "tags": ["geocoding", "chgis", "cnhgis", "historical_gis"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8002/a2a",
            metadata={"four_diagnosis": "望", "role": "geo"},
        ),
        "TextAnalystAgent": AgentCard(
            name="TextAnalystAgent",
            description="古籍 NLP、情感分析、隐喻识别。基于 MiniMax API 进行古文语义分析。",
            version="3.0.0",
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateDiff": False,
            },
            skills=[
                {
                    "id": "sentiment_analysis",
                    "name": "古文情感分析",
                    "description": "对古文文本进行情感极性分析，返回 -1 到 1 的分数",
                    "tags": ["sentiment", "classical_chinese", "nlp", "minimax"],
                    "inputModes": ["text/plain"],
                    "outputModes": ["application/json"],
                },
                {
                    "id": "metaphor_detection",
                    "name": "隐喻识别",
                    "description": "基于 CPM-KB 知识库识别文本中的概念隐喻，输出心理状态映射",
                    "tags": ["metaphor", "cpm-kb", "psychology", "classical_chinese"],
                    "inputModes": ["text/plain"],
                    "outputModes": ["application/json"],
                },
            ],
            authentication={"type": "api_key", "header": "X-API-Key"},
            endpoint="http://localhost:8003/a2a",
            metadata={"four_diagnosis": "问", "role": "nlp"},
        ),
        "KGraphAgent": AgentCard(
            name="KGraphAgent",
            description="时序知识图谱构建与多模态融合。管理 TKG 四元组，执行 MGKGR 推理查询。",
            version="3.0.0",
            capabilities={"streaming": False, "pushNotifications": False, "stateDiff": False},
            skills=[
                {
                    "id": "tkgr_query",
                    "name": "TKG 推理查询",
                    "description": "对时序知识图谱执行未来事实预测推理",
                    "tags": ["tkg", "knowledge_graph", "reasoning", "mrr"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8004/a2a",
            metadata={"four_diagnosis": "切", "role": "graph"},
        ),
        "PredictorAgent": AgentCard(
            name="PredictorAgent",
            description="ST-GNN 预测与情景生成。输出短/中/长期 PSI 预警与多路径情景。",
            version="3.0.0",
            capabilities={
                "streaming": False,
                "pushNotifications": True,
                "stateDiff": False,
            },
            skills=[
                {
                    "id": "psi_forecast",
                    "name": "PSI 预测",
                    "description": "基于 ST-GNN 和 Goldstone 模型输出 PSI 预测值与置信区间",
                    "tags": ["psi", "forecast", "st-gnn", "goldstone"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
                {
                    "id": "scenario_generation",
                    "name": "情景生成",
                    "description": "生成多条演化路径及其概率分布（MCTS 驱动）",
                    "tags": ["scenario", "mcts", "simulation", "long-term"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8005/a2a",
            metadata={"four_diagnosis": "切", "role": "prediction"},
        ),
        "VizAgent": AgentCard(
            name="VizAgent",
            description="时空热力图与场景还原。将 PSI 时序和预测结果渲染为 ECharts/Deck.gl 可视化。",
            version="3.0.0",
            capabilities={"streaming": False, "pushNotifications": False, "stateDiff": False},
            skills=[
                {
                    "id": "timeline_viz",
                    "name": "时序可视化",
                    "description": "生成 PSI 时间线折线图和危机散点图",
                    "tags": ["echarts", "visualization", "timeline", "psi"],
                    "inputModes": ["application/json"],
                    "outputModes": ["text/html"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8006/a2a",
            metadata={"role": "visualization"},
        ),
        "QCAgent": AgentCard(
            name="QCAgent",
            description="数据偏见检测与质量审计。执行 A/B/C/D 分级和 CR 矛盾检测，守护全流程质量。",
            version="3.0.0",
            capabilities={"streaming": False, "pushNotifications": False, "stateDiff": True},
            skills=[
                {
                    "id": "quality_audit",
                    "name": "质量审计",
                    "description": "对数据质量分级、IPW 权重合理性、PSI 阈值合规性进行检测",
                    "tags": ["quality", "audit", "cbdb", "ipw", "psi"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
                {
                    "id": "contradiction_detection",
                    "name": "矛盾检测",
                    "description": "执行 CR-001 至 CR-004 矛盾规则，检测跨模态异常",
                    "tags": ["contradiction", "cross-validation", "four-diagnosis"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8007/a2a",
            metadata={"role": "quality_control"},
        ),
        "MetaCogAgent": AgentCard(
            name="MetaCogAgent",
            description="元认知层 Agent。评估各 Agent 输出置信度，检测冲突，触发重试或升级人工审核。",
            version="3.0.0",
            capabilities={
                "streaming": False,
                "pushNotifications": False,
                "stateDiff": True,
            },
            skills=[
                {
                    "id": "confidence评估",
                    "name": "复合信心评估",
                    "description": "对各 Agent 输出进行复合信心评估，输出 0-1 置信度",
                    "tags": ["metacognition", "confidence", "self-reflection"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
                {
                    "id": "conflict_detection",
                    "name": "冲突检测",
                    "description": "检测四诊模态间的一致性，低于阈值触发人工审核",
                    "tags": ["conflict", "consistency", "four-diagnosis"],
                    "inputModes": ["application/json"],
                    "outputModes": ["application/json"],
                },
            ],
            authentication={"type": "none"},
            endpoint="http://localhost:8008/a2a",
            metadata={"role": "metacognition"},
        ),
    }
    return CARDS


def register_all_agents(storage_dir: Optional[Path] = None) -> AgentRegistry:
    """将全部 Agent Card 注册到指定目录"""
    registry = AgentRegistry(storage_dir)
    for card in build_agent_cards().values():
        registry.register(card)
    return registry
