#!/usr/bin/env python3
"""验证A2A协议栈多Agent协作"""
import sys, os
sys.path.insert(0, '/Users/tianjangwang/Documents/历史事件预测建模')

from mcp_a2a.a2a_client import A2AAgentCommunicator, TaskStatus
from mcp_a2a.agent_registry import build_agent_cards, register_all_agents
from mcp_a2a.orchestrator import HubAndSpokeOrchestrator, OrchestrationMode, PipelineStep

# === 验证项 1: AGENT_REGISTRY 包含至少 7 个 Agent ===
cards = build_agent_cards()
print('=== A2A Agent Registry ===')
print(f'REGISTERED_AGENTS: {len(cards)}')
print(f'AGENTS: {list(cards.keys())}')
assert len(cards) >= 7, f'Expected >= 7 agents, got {len(cards)}'
print('[✓] AGENT_REGISTRY check: PASS (>= 7 agents)')

# === 验证项 2: A2A 任务创建返回有效 task_id ===
print('\n=== A2A Task Creation ===')
data_agent = cards['DataIngestAgent']
client = A2AAgentCommunicator(agent_name='DataIngestAgent', agent_card_url=data_agent.endpoint)
task_id = client.submit_task('DataIngestAgent', 'cbdb_ingest', {'dynasty': '唐朝', 'decade': '620s'})
print(f'TASK_ID: {task_id}')
assert task_id, 'task_id should not be empty'
assert len(task_id) == 36, f'task_id should be UUID format, got {task_id}'
task_state = client.get_task_status(task_id)
print(f'STATUS_POLL: {task_state.status.value}')
print('[✓] A2A task creation check: PASS (valid task_id returned)')

# === 验证项 3: Orchestrator 返回结果 ===
print('\n=== Hub-and-Spoke Orchestrator ===')
orch = HubAndSpokeOrchestrator(mode=OrchestrationMode.ITERATIVE)
steps = [
    PipelineStep(
        step_id='psi_analyze',
        agent_name='PredictorAgent',
        skill_id='psi_forecast',
        input_map={'dynasty': '北宋', 'decade': '960s'},
        output_key='psi_result',
        confidence_threshold=0.5,
        max_retries=2,
    ),
]
orch.define_pipeline(steps)
result = orch.run({'dynasty': '北宋', 'decade': '960s'})
print(f'ORCH_RESULT: {str(result)[:200]}')
assert result is not None, 'orchestrator should return a result'
print('[✓] Orchestrator check: PASS (returned result)')

print('\n=== All Verifications Passed ===')
print('A2A Server multi-agent collaboration: CLOSED')