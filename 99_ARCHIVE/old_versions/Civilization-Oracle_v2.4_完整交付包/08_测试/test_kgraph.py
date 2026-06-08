"""
tests/test_kgraph.py
单元测试：phase5_kgraph.py 的 KGraphAgent

测试覆盖：
1. 时序知识图谱构建
2. MGKGR 两阶段融合
3. 图统计计算
4. PSI 从 TKG 计算
"""

import pytest
import sys

# 添加项目路径
sys.path.insert(0, '/Users/tianjangwang/Documents/历史事件预测建模')

from phase5_kgraph import (
    KGraphAgent,
    KGraphInput,
    KGCoordinator,
    MGKGRFusion,
    InMemoryGraph,
    get_song_dynasty_events,
)


class TestInMemoryGraph:
    """内存图谱测试"""

    @pytest.fixture
    def graph(self):
        """创建空图谱"""
        return InMemoryGraph()

    def test_add_node(self, graph):
        """测试：添加节点"""
        node_id = graph.add_node("王安石", "person")
        assert node_id is not None
        assert node_id in graph.nodes

    def test_add_edge(self, graph):
        """测试：添加边"""
        node1 = graph.add_node("王安石", "person")
        node2 = graph.add_node("新法", "policy")
        graph.add_edge(node1, "推行", node2, 1070)

        assert len(graph.edges) == 1
        assert graph.edges[0]["predicate"] == "推行"

    def test_query_time_range(self, graph):
        """测试：时序范围查询"""
        node1 = graph.add_node("赵匡胤", "person")
        node2 = graph.add_node("北宋", "dynasty")

        graph.add_edge(node1, "建立", node2, 960)
        graph.add_edge(node1, "迁都", node2, 963)

        results = graph.query_time_range(958, 965)
        assert len(results) == 2

        results = graph.query_time_range(970, 1000)
        assert len(results) == 0

    def test_compute_stats(self, graph):
        """测试：图统计计算"""
        node1 = graph.add_node("王安石", "person")
        node2 = graph.add_node("宋神宗", "person")
        node3 = graph.add_node("新法", "policy")

        graph.add_edge(node2, "启用", node1, 1069)
        graph.add_edge(node1, "推行", node3, 1070)

        stats = graph.compute_stats()
        assert stats["nodes"] == 3
        assert stats["edges"] == 2
        assert stats["avg_degree"] > 0

    def test_traverse(self, graph):
        """测试：图遍历"""
        n1 = graph.add_node("岳飞", "person")
        n2 = graph.add_node("抗金", "event")
        n3 = graph.add_node("中原", "place")

        graph.add_edge(n1, "进行", n2, 1130)
        graph.add_edge(n2, "指向", n3, 1130)

        results = graph.traverse(n1, depth=1)
        assert len(results) >= 1


class TestMGKGRFusion:
    """MGKGR 两阶段融合测试"""

    @pytest.fixture
    def fusion(self):
        return MGKGRFusion()

    def test_stage1_text_fusion(self, fusion):
        """测试：Stage 1 文本融合"""
        events = [
            {"subject": "王安石", "predicate": "推行", "object": "新法", "time": 1070},
            {"subject": "司马光", "predicate": "反对", "object": "新法", "time": 1070},
        ]

        embeddings = fusion.stage1_text_fusion(events)
        assert isinstance(embeddings, dict)
        assert len(embeddings) == 2

        for key, emb in embeddings.items():
            assert isinstance(emb, list)
            assert len(emb) == 32

    def test_stage2_temporal_fusion(self, fusion):
        """测试：Stage 2 时序融合"""
        events = [
            {"subject": "赵匡胤", "predicate": "建立", "object": "北宋", "time": 960},
            {"subject": "宋太宗", "predicate": "继位", "object": "北宋", "time": 976},
            {"subject": "宋真宗", "predicate": "签订", "object": "澶渊之盟", "time": 1005},
        ]

        text_embeddings = fusion.stage1_text_fusion(events)
        fused = fusion.stage2_temporal_fusion(events, text_embeddings)

        assert isinstance(fused, dict)
        assert len(fused) == 3

        for key, emb in fused.items():
            assert isinstance(emb, list)
            assert len(emb) == 32

    def test_fuse_complete(self, fusion):
        """测试：完整融合流程"""
        events = [
            {"subject": "岳飞", "predicate": "抗金", "object": "中原", "time": 1130},
            {"subject": "岳飞", "predicate": "收复", "object": "建康", "time": 1130},
        ]

        embeddings = fusion.fuse(events)
        assert isinstance(embeddings, dict)
        assert len(embeddings) == 2


class TestKGraphAgent:
    """KGraphAgent 测试"""

    @pytest.fixture
    def agent(self):
        return KGraphAgent()

    @pytest.fixture
    def sample_events(self):
        return [
            {"subject": "赵匡胤", "predicate": "建立", "object": "北宋", "time": 960, "type": "politics"},
            {"subject": "赵匡胤", "predicate": "杯酒释兵权", "object": "藩镇", "time": 961, "type": "politics"},
            {"subject": "宋神宗", "predicate": "启用", "object": "王安石", "time": 1069, "type": "politics"},
            {"subject": "王安石", "predicate": "推行", "object": "新法", "time": 1070, "type": "politics"},
            {"subject": "金军", "predicate": "攻破", "object": "开封", "time": 1127, "type": "conflict"},
        ]

    def test_build_graph_accepts_list(self, agent, sample_events):
        """测试：构建图谱接受列表输入"""
        input_data = KGraphInput(
            events=sample_events,
            fusion_method="MGKGR",
            use_neo4j=False
        )

        result = agent.process(input_data)
        assert result.status == "success"
        assert result.nodes_added > 0
        assert result.edges_added > 0

    def test_mgkgr_fusion_embeddings(self, agent, sample_events):
        """测试：MGKGR 融合生成嵌入"""
        input_data = KGraphInput(
            events=sample_events,
            fusion_method="MGKGR",
            use_neo4j=False
        )

        result = agent.process(input_data)
        assert isinstance(result.fusion_embeddings, dict)
        assert len(result.fusion_embeddings) > 0

    def test_graph_stats(self, agent, sample_events):
        """测试：图统计信息"""
        input_data = KGraphInput(
            events=sample_events,
            fusion_method="MGKGR",
            use_neo4j=False
        )

        result = agent.process(input_data)
        stats = result.graph_stats

        assert "nodes" in stats or "avg_degree" in stats
        assert "edges" in stats or "time_range" in stats
        assert "MRR" in stats
        assert "Hit@10" in stats

    def test_in_memory_mode(self, agent, sample_events):
        """测试：内存图谱模式"""
        input_data = KGraphInput(
            events=sample_events,
            fusion_method="MGKGR",
            use_neo4j=False  # 强制使用内存模式
        )

        result = agent.process(input_data)
        assert result.mode == "in_memory"

    def test_empty_events_processing(self, agent):
        """测试：空事件列表处理（正常返回结果）"""
        input_data = KGraphInput(events=[], fusion_method="MGKGR", use_neo4j=False)
        result = agent.process(input_data)
        # 空事件返回成功但无节点/边
        assert result.status == "success"
        assert result.nodes_added == 0
        assert result.edges_added == 0


class TestKGCoordinator:
    """知识协调器测试"""

    @pytest.fixture
    def coordinator(self):
        return KGCoordinator()

    def test_build_tkg_from_events(self, coordinator):
        """测试：从事件列表构建 TKG"""
        events = get_song_dynasty_events()[:5]
        result = coordinator.build_tkg_from_events(events)

        assert result.status == "success"
        assert result.nodes_added > 0
        assert result.edges_added > 0

    def test_compute_psi_from_tkg(self, coordinator):
        """测试：从 TKG 计算 PSI"""
        events = get_song_dynasty_events()
        psi = coordinator.compute_psi_from_tkg(events)

        assert "MMP" in psi
        assert "EMP" in psi
        assert "SFD" in psi

        for key in ["MMP", "EMP", "SFD"]:
            assert isinstance(psi[key], (int, float))
            assert 0 <= psi[key] <= 1

    def test_coordinator_multiple_periods(self, coordinator):
        """测试：多时期 TKG 对比"""
        song_events = get_song_dynasty_events()
        song_psi = coordinator.compute_psi_from_tkg(song_events)

        assert isinstance(song_psi, dict)
        assert all(0 <= v <= 1 for v in song_psi.values())


class TestWorkflowC:
    """工作流 C 测试"""

    @pytest.fixture
    def coordinator(self):
        return KGCoordinator()

    def test_workflow_c_short_horizon(self, coordinator):
        """测试：工作流 C 短期预警"""
        from phase5_kgraph import workflow_C

        events = get_song_dynasty_events()
        kg_result = coordinator.build_tkg_from_events(events)
        psi_inputs = coordinator.compute_psi_from_tkg(events)

        prediction = workflow_C(kg_result, psi_inputs, time_horizon="short")

        assert prediction["type"] == "alert"
        assert "alert_level" in prediction
        assert "peak_prediction" in prediction

    def test_workflow_c_medium_horizon(self, coordinator):
        """测试：工作流 C 中期情景"""
        from phase5_kgraph import workflow_C

        events = get_song_dynasty_events()
        kg_result = coordinator.build_tkg_from_events(events)
        psi_inputs = coordinator.compute_psi_from_tkg(events)

        prediction = workflow_C(kg_result, psi_inputs, time_horizon="medium")

        assert prediction["type"] == "scenario"
        assert "scenarios" in prediction
        assert len(prediction["scenarios"]) >= 3


# ── 测试运行入口 ──────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])