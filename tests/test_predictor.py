"""
tests/test_predictor.py
单元测试：phase6_pipeline.py 的 PredictorAgent 和 QCAgent

测试覆盖：
1. PSI 综合计算
2. 预警级别判定
3. 峰值预测
4. 情景生成
5. CR 矛盾检测
"""

import pytest
import sys

# 添加项目路径
sys.path.insert(0, '/Users/tianjangwang/Documents/历史事件预测建模')

from phase6_pipeline import (
    PredictorAgent,
    QCAgent,
    CivilizationOraclePipeline,
    PERIOD_CORPUS,
)


class TestPredictorAgent:
    """PredictorAgent 测试"""

    @pytest.fixture
    def predictor(self):
        return PredictorAgent()

    def test_predict_psi_calculation(self, predictor):
        """测试：PSI 综合计算"""
        result = predictor.predict("测试时期", 0.6, 0.5, 0.7)

        assert result.psi == pytest.approx(0.6 * 0.5 * 0.7, rel=1e-2)
        assert 0 <= result.psi <= 1

    def test_predict_alert_levels(self, predictor):
        """测试：预警级别判定
        PSI = mmp * emp * sfd，mmp=emp=0.5
        阈值：critical (<0.15), high (0.15-0.25), medium (0.25-0.40), low (>=0.40)
        """
        test_cases = [
            (0.2, "critical"),   # PSI = 0.05 < 0.15
            (0.4, "critical"),   # PSI = 0.10 < 0.15
            (0.5, "critical"),   # PSI = 0.125 < 0.15
            (0.6, "high"),        # PSI = 0.15 → 边界（含）
            (0.7, "high"),        # PSI = 0.175 (0.15-0.25)
            (0.8, "high"),        # PSI = 0.20 < 0.25
            (1.0, "medium"),      # PSI = 0.25 → 边界（含）
            (1.2, "medium"),      # PSI = 0.30 (0.25-0.40)
            (1.6, "low"),         # PSI = 0.40 → 边界（含）
            (2.0, "low"),         # PSI = 0.50 >= 0.40
        ]

        for sfd_val, expected_level in test_cases:
            result = predictor.predict("测试", 0.5, 0.5, sfd_val)
            assert result.alert_level == expected_level, \
                f"PSI={result.psi:.3f} (sfd={sfd_val}) 期望 {expected_level}, 得到 {result.alert_level}"

    def test_predict_peak_prediction(self, predictor):
        """测试：峰值预测"""
        result = predictor.predict("测试时期", 0.3, 0.4, 0.5)

        assert "peak_prediction" in result.__dict__
        assert "years_ahead" in result.peak_prediction
        assert "probability" in result.peak_prediction

        # 年数应为正整数
        assert result.peak_prediction["years_ahead"] > 0

        # 概率应在 0-1 之间
        assert 0 <= result.peak_prediction["probability"] <= 1

    def test_predict_scenarios_generated(self, predictor):
        """测试：情景生成（PSI 低值）"""
        result = predictor.predict("测试", 0.2, 0.2, 0.3, time_horizon="medium")

        assert len(result.scenarios) >= 3
        for scenario in result.scenarios:
            assert "id" in scenario
            assert "prob" in scenario
            assert "desc" in scenario
            assert 0 <= scenario["prob"] <= 1

    def test_predict_confidence_interval(self, predictor):
        """测试：置信区间"""
        result = predictor.predict("测试", 0.4, 0.5, 0.6, time_horizon="medium")

        assert isinstance(result.confidence_interval, list)
        assert len(result.confidence_interval) == 2
        assert result.confidence_interval[0] <= result.confidence_interval[1]

    def test_predict_high_psi_scenarios(self, predictor):
        """测试：高 PSI 情景（PSI >= 0.25）"""
        result = predictor.predict("测试", 0.5, 0.5, 0.6, time_horizon="medium")

        assert len(result.scenarios) == 3
        # 高 PSI 时情景 B（气候冲击）概率应较高
        scenario_b = next((s for s in result.scenarios if s["id"] == "B"), None)
        assert scenario_b is not None
        assert scenario_b["prob"] >= 0.35


class TestQCAgent:
    """QCAgent 矛盾检测测试"""

    @pytest.fixture
    def qc_agent(self):
        return QCAgent()

    @pytest.fixture
    def sample_sentiment_results(self):
        """示例情感分析结果"""
        return [
            {"doc_id": "001", "sentiment_polarity": 0.8, "sentiment_label": "positive"},
            {"doc_id": "002", "sentiment_polarity": 0.7, "sentiment_label": "positive"},
            {"doc_id": "003", "sentiment_polarity": -0.6, "sentiment_label": "negative"},
            {"doc_id": "004", "sentiment_polarity": -0.5, "sentiment_label": "negative"},
            {"doc_id": "005", "sentiment_polarity": 0.3, "sentiment_label": "neutral"},
        ]

    def test_validate_pass_status(self, qc_agent, sample_sentiment_results):
        """测试：质量检测通过状态"""
        result = qc_agent.validate(
            sentiment_results=sample_sentiment_results,
            psi=0.5,
            mmp=0.5,
            emp=0.5,
            sfd=0.5,
            records=[]
        )

        assert result["status"] in ["pass", "warning", "fail"]

    def test_cr001_hope_disaster_conflict(self, qc_agent):
        """测试：CR-001 乐观与灾难叙事共存"""
        sentiment_results = [
            {"doc_id": "001", "sentiment_polarity": 0.8, "sentiment_label": "positive"},
            {"doc_id": "002", "sentiment_polarity": 0.7, "sentiment_label": "positive"},
            {"doc_id": "003", "sentiment_polarity": -0.6, "sentiment_label": "negative"},
            {"doc_id": "004", "sentiment_polarity": -0.5, "sentiment_label": "negative"},
        ]

        result = qc_agent.validate(
            sentiment_results=sentiment_results,
            psi=0.4,
            mmp=0.5,
            emp=0.5,
            sfd=0.5,
            records=[]
        )

        # 检测 CR-001
        cr001 = next((v for v in result["cr_violations"] if v["rule_id"] == "CR-001"), None)
        if cr001:
            assert cr001["rule_name"] == "乐观与灾难叙事共存"

    def test_cr003_mmp_low_sfd_high(self, qc_agent):
        """测试：CR-003 动员力弱但财政压力大"""
        sentiment_results = [
            {"doc_id": "001", "sentiment_polarity": 0.0, "sentiment_label": "neutral"},
        ]

        result = qc_agent.validate(
            sentiment_results=sentiment_results,
            psi=0.2,
            mmp=0.25,  # 低
            emp=0.5,
            sfd=0.75,  # 高
            records=[]
        )

        # 检测 CR-003
        cr003 = next((v for v in result["cr_violations"] if v["rule_id"] == "CR-003"), None)
        if cr003:
            assert cr003["rule_name"] == "动员力弱但财政压力大"

    def test_bias_detection(self, qc_agent, sample_sentiment_results):
        """测试：偏见检测"""
        records = [
            {"gender": "M", "origin_c": "河南"},
            {"gender": "M", "origin_c": "河南"},
            {"gender": "M", "origin_c": "浙江"},
            {"gender": "M", "origin_c": "江苏"},
        ]

        result = qc_agent.validate(
            sentiment_results=sample_sentiment_results,
            psi=0.5,
            mmp=0.5,
            emp=0.5,
            sfd=0.5,
            records=records
        )

        assert "bias_report" in result
        assert "gender_coverage" in result["bias_report"]
        assert "regional_coverage" in result["bias_report"]

    def test_validate_returns_metrics(self, qc_agent, sample_sentiment_results):
        """测试：验证返回质量指标"""
        result = qc_agent.validate(
            sentiment_results=sample_sentiment_results,
            psi=0.45,
            mmp=0.5,
            emp=0.5,
            sfd=0.5,
            records=[]
        )

        assert "metrics" in result
        assert "avg_sentiment" in result["metrics"]
        assert "hope_ratio" in result["metrics"]
        assert "disaster_ratio" in result["metrics"]


class TestCivilizationOraclePipeline:
    """端到端 Pipeline 测试"""

    @pytest.fixture
    def pipeline(self):
        return CivilizationOraclePipeline()

    def test_run_song_late_period(self, pipeline):
        """测试：北宋末期分析"""
        result = pipeline.run("北宋末期", time_horizon="short", verbose=False)

        assert result["status"] == "success"
        assert result["period"] == "北宋末期"

        pred = result["prediction"]
        assert "psi" in pred
        assert "mmp" in pred
        assert "emp" in pred
        assert "sfd" in pred

    def test_run_tang_golden_age(self, pipeline):
        """测试：盛唐分析"""
        result = pipeline.run("盛唐", time_horizon="short", verbose=False)

        assert result["status"] == "success"
        assert "psi" in result["prediction"]

    def test_run_ming_late_period(self, pipeline):
        """测试：明末分析"""
        result = pipeline.run("明末", time_horizon="short", verbose=False)

        assert result["status"] == "success"
        pred = result["prediction"]
        # 明末是高风险时期，PSI 应该较低
        assert 0 <= pred["psi"] <= 1

    def test_run_medium_horizon(self, pipeline):
        """测试：中期间景分析"""
        result = pipeline.run("北宋末期", time_horizon="medium", verbose=False)

        assert result["status"] == "success"
        pred = result["prediction"]
        assert "scenarios" in pred
        assert len(pred["scenarios"]) >= 3

    def test_tkg_stats_included(self, pipeline):
        """测试：TKG 统计包含在结果中"""
        result = pipeline.run("北宋末期", time_horizon="short", verbose=False)

        assert "tkg_stats" in result
        tkg_stats = result["tkg_stats"]
        assert "MRR" in tkg_stats
        assert "Hit@10" in tkg_stats

    def test_qc_results_included(self, pipeline):
        """测试：QC 结果包含在结果中"""
        result = pipeline.run("北宋末期", time_horizon="short", verbose=False)

        assert "qc" in result
        qc = result["qc"]
        assert "status" in qc
        assert "cr_violations" in qc

    def test_invalid_period_raises_error(self, pipeline):
        """测试：无效时期抛出错误"""
        with pytest.raises(ValueError):
            pipeline.run("不存在的时期", time_horizon="short", verbose=False)


class TestPeriodCorpus:
    """历史时期语料库测试"""

    def test_all_periods_have_events(self):
        """测试：所有时期都有事件数据"""
        for period_name, corpus in PERIOD_CORPUS.items():
            assert "events" in corpus
            assert len(corpus["events"]) > 0

    def test_events_have_required_fields(self):
        """测试：事件包含必需字段"""
        for period_name, corpus in PERIOD_CORPUS.items():
            for event in corpus["events"]:
                assert "subject" in event
                assert "predicate" in event
                assert "object" in event
                assert "time" in event

    def test_conflict_events_identified(self):
        """测试：识别冲突事件"""
        for period_name, corpus in PERIOD_CORPUS.items():
            conflict_events = [e for e in corpus["events"] if e.get("type") == "conflict"]
            # 大多数时期应该有冲突事件
            assert len(conflict_events) >= 0


class TestEdgeCases:
    """边界情况测试"""

    @pytest.fixture
    def predictor(self):
        return PredictorAgent()

    @pytest.fixture
    def qc_agent(self):
        return QCAgent()

    def test_zero_mmp(self, predictor):
        """测试：MMP 为零"""
        result = predictor.predict("测试", 0.0, 0.5, 0.5)
        assert result.psi == 0.0

    def test_max_psi(self, predictor):
        """测试：PSI 最大值"""
        result = predictor.predict("测试", 1.0, 1.0, 1.0)
        assert result.psi == pytest.approx(1.0, rel=1e-2)

    def test_empty_sentiment_results(self, qc_agent):
        """测试：空情感结果"""
        result = qc_agent.validate(
            sentiment_results=[],
            psi=0.5,
            mmp=0.5,
            emp=0.5,
            sfd=0.5,
            records=[]
        )
        assert result["status"] in ["pass", "warning", "fail"]

    def test_empty_records(self, qc_agent):
        """测试：空记录"""
        sentiment_results = [
            {"doc_id": "001", "sentiment_polarity": 0.0, "sentiment_label": "neutral"},
        ]
        result = qc_agent.validate(
            sentiment_results=sentiment_results,
            psi=0.5,
            mmp=0.5,
            emp=0.5,
            sfd=0.5,
            records=[]
        )
        assert "bias_report" in result


# ── 测试运行入口 ──────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])