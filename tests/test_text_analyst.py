"""
tests/test_text_analyst.py
单元测试：phase3_text_analyst.py 的 TextAnalystAgent

测试覆盖：
1. 情感分析 (sentiment analysis)
2. 隐喻识别 (metaphor detection)
3. PSI 文本代理计算
4. 叙事比率计算
"""

import pytest
import sys

# 添加项目路径
sys.path.insert(0, '/Users/tianjangwang/Documents/历史事件预测建模')

from phase3_text_analyst import (
    TextAnalystAgent,
    TextAnalystInput,
    CPM_KB,
)


class TestTextAnalystAgent:
    """TextAnalystAgent 测试类"""

    @pytest.fixture
    def agent(self):
        """创建 TextAnalystAgent 实例"""
        return TextAnalystAgent()

    @pytest.fixture
    def sample_docs(self):
        """示例文档数据"""
        return [
            {
                "id": "test_001",
                "text": "盛世太平，百姓安乐，朝廷清明，百官尽职。",
                "source": "测试",
                "year": 1069,
            },
            {
                "id": "test_002",
                "text": "党争激烈，民不聊生，大厦将倾，天下思乱。",
                "source": "测试",
                "year": 1120,
            },
            {
                "id": "test_003",
                "text": "改革图强，除旧布新，天命在我，必将中兴。",
                "source": "测试",
                "year": 1070,
            },
            {
                "id": "test_004",
                "text": "灾荒频仍，赋税沉重，流民四起，哀鸿遍野。",
                "source": "测试",
                "year": 1125,
            },
        ]

    # ── 情感分析测试 ──────────────────────────────────────

    def test_sentiment_positive_text(self, agent):
        """测试：正面情感文本分析"""
        text = "盛世太平，百姓安乐，朝廷清明，百官尽职。"
        result = agent._analyze_sentiment(text)

        assert "polarity" in result
        assert isinstance(result["polarity"], (int, float))
        assert result["polarity"] > 0  # 正面情感应为正值
        assert "dominant_emotion" in result
        assert result["dominant_emotion"] in ["乐观/积极", "希望/平和", "中性/客观"]

    def test_sentiment_negative_text(self, agent):
        """测试：负面情感文本分析"""
        text = "党争激烈，民不聊生，大厦将倾，天下思乱。"
        result = agent._analyze_sentiment(text)

        assert "polarity" in result
        assert isinstance(result["polarity"], (int, float))
        assert result["polarity"] < 0  # 负面情感应为负值
        assert "dominant_emotion" in result

    def test_sentiment_neutral_text(self, agent):
        """测试：中性情感文本分析"""
        text = "今日无事，天气晴朗。"
        result = agent._analyze_sentiment(text)

        assert "polarity" in result
        assert isinstance(result["polarity"], (int, float))
        # 中性文本的极性应该接近 0
        assert -0.3 <= result["polarity"] <= 0.3

    def test_sentiment_returns_required_fields(self, agent):
        """测试：情感分析返回所有必需字段"""
        text = "改革图强，除旧布新，天命在我，必将中兴。"
        result = agent._analyze_sentiment(text)

        required_fields = ["polarity", "positive_score", "negative_score", "dominant_emotion", "intensity"]
        for field in required_fields:
            assert field in result, f"缺少字段: {field}"

    # ── 隐喻识别测试 ──────────────────────────────────────

    def test_detect_metaphors_positive(self, agent):
        """测试：检测正面隐喻"""
        text = "心为水，静水深流，心如止水，清心寡欲。"
        result = agent._detect_metaphors(text)

        assert isinstance(result, list)
        # 应该检测到 "心为水" 隐喻
        metaphor_patterns = [m["pattern"] for m in result]
        assert "心为水" in metaphor_patterns

    def test_detect_metaphors_negative(self, agent):
        """测试：检测负面隐喻"""
        text = "心火焚烧，怒火中烧，焦心如焚，难以自持。"
        result = agent._detect_metaphors(text)

        assert isinstance(result, list)
        # 应该检测到 "心为火" 隐喻
        metaphor_patterns = [m["pattern"] for m in result]
        assert "心为火" in metaphor_patterns

    def test_detect_metaphors_context_dependent(self, agent):
        """测试：检测语境依赖隐喻"""
        text = "家国如舟，同舟共济，覆舟之祸，危在旦夕。"
        result = agent._detect_metaphors(text)

        assert isinstance(result, list)
        # 应该检测到 "家国为舟" 隐喻
        metaphor_patterns = [m["pattern"] for m in result]
        assert "家国为舟" in metaphor_patterns

    def test_detect_metaphors_returns_structure(self, agent):
        """测试：隐喻识别返回正确结构"""
        text = "春风得意，马蹄轻快，金榜题名，前途光明。"
        result = agent._detect_metaphors(text)

        for m in result:
            assert "pattern" in m
            assert "keyword" in m
            assert "psychological_state" in m
            assert "base_polarity" in m
            assert "adjusted_polarity" in m

    # ── PSI 文本代理测试 ──────────────────────────────────

    def test_compute_psi_mmp(self, agent):
        """测试：PSI MMP 子指标计算"""
        text = "科举兴盛，士人踊跃，朝堂之上，文官济济。"
        result = agent._compute_psi_from_text(text)

        assert "MMP" in result
        assert isinstance(result["MMP"], (int, float))
        assert 0 <= result["MMP"] <= 1

    def test_compute_psi_emp(self, agent):
        """测试：PSI EMP 子指标计算"""
        text = "百姓困苦，万民疾苦，苍生涂炭，社会动荡。"
        result = agent._compute_psi_from_text(text)

        assert "EMP" in result
        assert isinstance(result["EMP"], (int, float))
        assert 0 <= result["EMP"] <= 1

    def test_compute_psi_sfd(self, agent):
        """测试：PSI SFD 子指标计算"""
        text = "财政赤字，债台高筑，战费浩繁，赔款沉重。"
        result = agent._compute_psi_from_text(text)

        assert "SFD" in result
        assert isinstance(result["SFD"], (int, float))
        assert 0 <= result["SFD"] <= 1

    def test_compute_psi_proxy(self, agent):
        """测试：PSI 综合代理值计算"""
        text = "党争内斗，赋税沉重，民变蜂起，天下大乱。"
        result = agent._compute_psi_from_text(text)

        assert "PSI_proxy" in result
        assert isinstance(result["PSI_proxy"], (int, float))
        assert 0 <= result["PSI_proxy"] <= 1

    # ── 叙事分析测试 ──────────────────────────────────────

    def test_hope_ratio_calculation(self, agent):
        """测试：希望叙事比率计算"""
        text = "改革图强，励精图治，盛世有望，必将中兴。"
        result = agent._compute_hope_ratio(text)

        assert isinstance(result, (int, float))
        assert 0 <= result <= 1
        assert result > 0.5  # 希望叙事占优势

    def test_disaster_narrative_calculation(self, agent):
        """测试：灾难叙事比率计算"""
        text = "灾荒连连，生灵涂炭，大厦将倾，哀鸿遍野。"
        result = agent._compute_disaster_narrative(text)

        assert isinstance(result, (int, float))
        assert 0 <= result <= 1
        assert result > 0.5  # 灾难叙事占优势

    # ── 端到端测试 ──────────────────────────────────────

    def test_agent_run_complete_analysis(self, agent, sample_docs):
        """测试：Agent 完整分析流程"""
        input_data = TextAnalystInput(
            documents=sample_docs,
            analysis_types=["sentiment", "metaphor", "psi_index"],
        )

        output = agent.run(input_data)

        assert output.status == "success"
        assert len(output.results) == len(sample_docs)
        assert output.metadata["docs_analyzed"] == len(sample_docs)

    def test_agent_run_returns_all_result_fields(self, agent, sample_docs):
        """测试：Agent 返回结果包含所有必需字段"""
        input_data = TextAnalystInput(
            documents=[sample_docs[0]],
            analysis_types=["sentiment", "metaphor", "psi_index"],
        )

        output = agent.run(input_data)
        result = output.results[0]

        # 验证所有字段存在
        assert "doc_id" in result
        assert "sentiment" in result
        assert "metaphors" in result
        assert "psi_inputs" in result
        assert "hope_ratio" in result
        assert "disaster_narrative" in result


class TestCPMKB:
    """CPM-KB 知识库测试"""

    def test_cpm_kb_structure(self):
        """测试：CPM-KB 结构完整性"""
        assert isinstance(CPM_KB, dict)
        assert len(CPM_KB) > 0

        for pattern, info in CPM_KB.items():
            assert "psychological_state" in info
            assert "polarity" in info
            assert "domain" in info
            assert "keywords" in info
            assert isinstance(info["polarity"], (int, float))
            assert -1 <= info["polarity"] <= 1

    def test_cpm_kb_coverage(self):
        """测试：CPM-KB 覆盖多种情绪域"""
        domains = set(info["domain"] for info in CPM_KB.values())
        assert len(domains) >= 3  # 至少覆盖 3 个域


class TestEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def agent(self):
        return TextAnalystAgent()

    def test_empty_text_sentiment(self, agent):
        """测试：空文本情感分析"""
        result = agent._analyze_sentiment("")
        assert isinstance(result["polarity"], (int, float))

    def test_empty_text_metaphor(self, agent):
        """测试：空文本隐喻识别"""
        result = agent._detect_metaphors("")
        assert isinstance(result, list)

    def test_no_matching_metaphors(self, agent):
        """测试：无匹配的隐喻识别"""
        text = "今天天气很好，我们去散步。"
        result = agent._detect_metaphors(text)
        assert isinstance(result, list)
        assert len(result) == 0  # 不应检测到任何隐喻


# ── 测试运行入口 ──────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])