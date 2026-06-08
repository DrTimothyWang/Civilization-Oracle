"""
Civilization-Oracle v3.0: MCP+A2A Protocol Stack
=================================================

Architecture:
  - MCP (Model Context Protocol): agent-to-tool vertical layer
  - A2A (Agent-to-Agent Protocol): agent-to-agent horizontal layer
  - Hub-and-Spoke + Iterative Feedback (not linear DAG)

MCP: JSON-RPC 2.0, OAuth 2.1, tool/resource/prompt primitives
A2A: Agent Card (.well-known/agent.json), 9-state task lifecycle

v3.0 Changes from v2.6:
  - Custom JSON messages → MCP+A2A standard protocols
  - Linear DAG → Iterative闭环 (neutralizes 40%+ faults)
  - Static topology → Dynamic agent discovery via Agent Card
  - No metacognition → MetaCogAgent confidence + conflict detection
"""

from .mcp_client import MCPToolCaller, MCPToolRegistry
from .a2a_client import A2AAgentCommunicator, TaskStatus, A2AMessage
from .orchestrator import HubAndSpokeOrchestrator, OrchestrationMode, PipelineStep
from .metacognition import MetaCogAgent, ConfidenceReport
from .agent_registry import AgentRegistry, AgentCard, register_all_agents, build_agent_cards

__all__ = [
    # MCP
    "MCPToolCaller",
    "MCPToolRegistry",
    # A2A
    "A2AAgentCommunicator",
    "TaskStatus",
    "A2AMessage",
    # Orchestrator
    "HubAndSpokeOrchestrator",
    "OrchestrationMode",
    "PipelineStep",
    # MetaCog
    "MetaCogAgent",
    "ConfidenceReport",
    # Registry
    "AgentRegistry",
    "AgentCard",
    "register_all_agents",
    "build_agent_cards",
]
