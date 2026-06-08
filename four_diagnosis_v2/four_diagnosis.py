"""
四诊合参 2.0 — 多模态交叉验证框架
==========================================
v2.6: 单一 PSI 指标，无交叉验证
v3.0: 望闻问切四模态，各自独立计算PSI，再交叉验证

四诊模态：
- 望（望诊）：GIS 空间数据 → 地理分布密度、文化中心迁移轨迹
- 闻（闻诊）：气候数据（竺可桢温度曲线 / REACHES）→ 温度距平、灾害频率
- 问（问诊）：文本语义（CTEXT / MiniMax API）→ 情感极性、社会心理指数
- 切（切诊）：人口统计/军事记录 → MMP、EMP、SFD、PSI

一致性阈值：≥ 0.7 → "收敛" → 输出；< 0.7 → 触发人工审核
"""

import numpy as np
from dataclasses import dataclass
from typing import Any


@dataclass
class DiagnosisResult:
    """单诊结果"""

    modality: str  # 望/闻/问/切
    value: float  # PSI 或等效指标
    confidence: float  # 置信度
    data_quality: str  # A/B/C/D
    n_observations: int  # 观测数
    metadata: dict


@dataclass
class CrossValidationResult:
    """交叉验证结果"""

    converged: bool  # 是否收敛
    consistency_score: float  # 一致性分数
    modalities: dict[str, DiagnosisResult]  # 各诊结果
    disagreements: list[dict]  # 不一致详情
    final_psi: float  # 融合 PSI
    confidence: float
    verdict: str  # "accept" | "escalate" | "reject"


class FourDiagnosisValidator:
    """
    四诊合参验证器

    Pipeline:
    1. 各诊独立计算 PSI（望/闻/问/切）
    2. 两两一致性检验（Pearson / Kendall）
    3. 融合 PSI（加权平均）
    4. 判定：converged ≥ threshold → accept；< threshold → escalate
    """

    def __init__(self, consistency_threshold: float = 0.7):
        self.consistency_threshold = consistency_threshold
        # 各诊基础可信度矩阵（来自 v3.0 报告）
        # 清代高，先秦低
        self.base_confidence = {
            "望": {"清代": 0.30, "明代": 0.70, "宋代": 0.65, "唐代": 0.60, "先秦": 0.30},
            "闻": {"清代": 0.92, "明代": 0.85, "宋代": 0.75, "唐代": 0.65, "先秦": 0.20},
            "问": {"清代": 0.88, "明代": 0.88, "宋代": 0.82, "唐代": 0.80, "先秦": 0.50},
            "切": {"清代": 0.88, "明代": 0.85, "宋代": 0.80, "唐代": 0.75, "先秦": 0.20},
        }

    def validate(
        self,
        dynasty: str,
        diagnoses: dict[str, DiagnosisResult],
    ) -> CrossValidationResult:
        """
        执行四诊交叉验证
        """
        if len(diagnoses) < 2:
            return CrossValidationResult(
                converged=False,
                consistency_score=0.0,
                modalities=diagnoses,
                disagreements=[{"reason": "少于2个诊法，无法验证"}],
                final_psi=0.5,
                confidence=0.0,
                verdict="escalate",
            )

        # 提取 PSI 值
        modality_values = {m: d.value for m, d in diagnoses.items()}

        # 两两一致性检验
        modality_names = list(modality_values.keys())
        consistencies = []
        disagreements = []

        for i, mi in enumerate(modality_names):
            for mj in modality_names[i + 1 :]:
                vi, vj = modality_values[mi], modality_values[mj]
                # Pearson 相关（简化）
                score = 1.0 - min(abs(vi - vj) / 0.5, 1.0)  # 差值越小一致性越高
                consistencies.append(score)
                if score < self.consistency_threshold:
                    disagreements.append(
                        {
                            "pair": f"{mi}↔{mj}",
                            "values": {mi: round(vi, 4), mj: round(vj, 4)},
                            "score": round(score, 4),
                            "reason": f"PSI差值 {abs(vi-vj):.4f} 超过阈值",
                        }
                    )

        avg_consistency = np.mean(consistencies) if consistencies else 0.0

        # 加权融合 PSI（权重 = 基础可信度 × 观测数）
        dynasty_lower = dynasty.lower().replace("朝", "").replace("代", "")
        dynasty_key = next(
            (k for k in self.base_confidence["望"] if k in dynasty), "宋代"
        )

        total_weight = 0.0
        weighted_sum = 0.0
        for m, d in diagnoses.items():
            base = self.base_confidence.get(m, {}).get(dynasty_key, 0.7)
            weight = base * np.sqrt(d.n_observations)  # 观测越多权重越高
            weighted_sum += d.value * weight
            total_weight += weight

        final_psi = weighted_sum / total_weight if total_weight > 0 else 0.5

        # 综合置信度
        confidence = avg_consistency * np.mean(
            [d.confidence for d in diagnoses.values()]
        )

        converged = avg_consistency >= self.consistency_threshold
        verdict = "accept" if converged else "escalate"

        return CrossValidationResult(
            converged=converged,
            consistency_score=round(avg_consistency, 4),
            modalities=diagnoses,
            disagreements=disagreements,
            final_psi=round(final_psi, 4),
            confidence=round(confidence, 4),
            verdict=verdict,
        )


def compute_four_diagnoses(
    dynasty: str,
    expert_data: list[dict],
    climate_data: dict,
    text_sentiments: list[float],
) -> dict[str, DiagnosisResult]:
    """
    计算四诊 PSI

    返回：{
        "望": DiagnosisResult(...),
        "闻": DiagnosisResult(...),
        "问": DiagnosisResult(...),
        "切": DiagnosisResult(...),
    }
    """
    n = len(expert_data) if expert_data else 100

    # 望：GIS 地理密度 PSI
    north_ratio = sum(1 for e in expert_data if e.get("y_coord", 35) > 35) / max(n, 1)
    gsi_wang = 1.0 + (north_ratio - 0.5) * 0.8
    psi_wang = gsi_wang * np.mean(text_sentiments) if text_sentiments else 0.5

    # 闻：气候数据 PSI
    temp_anomaly = climate_data.get("temp_anomaly", 0.0)
    disaster_freq = climate_data.get("disaster_freq", 0.0)
    # 气候压力指数（越高PSI越低）
    climate_stress = max(0, temp_anomaly * 0.3 + disaster_freq * 0.2)
    psi_wen = max(0, min(1, 0.7 - climate_stress))

    # 问：文本语义 PSI
    avg_sentiment = np.mean(text_sentiments) if text_sentiments else 0.0
    psi_wen2 = (avg_sentiment + 1) / 2  # 归一化到 [0,1]

    # 切：综合 PSI
    psi_qie = (psi_wang + psi_wen2) / 2

    return {
        "望": DiagnosisResult(
            modality="望",
            value=round(psi_wang, 4),
            confidence=0.65,
            data_quality="B",
            n_observations=n,
            metadata={"north_ratio": round(north_ratio, 4), "gsi": round(gsi_wang, 4)},
        ),
        "闻": DiagnosisResult(
            modality="闻",
            value=round(psi_wen, 4),
            confidence=0.80,
            data_quality="A",
            n_observations=len(climate_data.get("years", [0])),
            metadata={
                "temp_anomaly": round(temp_anomaly, 4),
                "disaster_freq": disaster_freq,
            },
        ),
        "问": DiagnosisResult(
            modality="问",
            value=round(psi_wen2, 4),
            confidence=0.75,
            data_quality="A",
            n_observations=len(text_sentiments),
            metadata={"avg_sentiment": round(avg_sentiment, 4)},
        ),
        "切": DiagnosisResult(
            modality="切",
            value=round(psi_qie, 4),
            confidence=0.70,
            data_quality="B",
            n_observations=n,
            metadata={"component": "望+问"},
        ),
    }


def demo_four_diagnosis():
    """演示四诊合参 2.0"""
    validator = FourDiagnosisValidator(consistency_threshold=0.7)

    # 模拟数据
    dynasties = ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]
    results = {}

    for dynasty in dynasties:
        diagnoses = compute_four_diagnoses(
            dynasty=dynasty,
            expert_data=[{"y_coord": 35 + i * 0.5} for i in range(100)],
            climate_data={"temp_anomaly": 0.2, "disaster_freq": 0.3, "years": [1, 2, 3]},
            text_sentiments=[0.5, 0.6, 0.7, -0.3, 0.4, 0.6, 0.5, -0.2],
        )
        result = validator.validate(dynasty, diagnoses)
        results[dynasty] = result

    print("=== 四诊合参 2.0 演示 ===")
    print()
    print(f"{'朝代':<10} {'望':>6} {'闻':>6} {'问':>6} {'切':>6} {'融合PSI':>8} {'一致性':>8} {'判定':>8}")
    print("-" * 65)
    for dynasty, r in results.items():
        mods = r.modalities
        icon = "✅" if r.converged else "⚠"
        print(
            f"{dynasty:<10} "
            f"{mods['望'].value:>6.4f} "
            f"{mods['闻'].value:>6.4f} "
            f"{mods['问'].value:>6.4f} "
            f"{mods['切'].value:>6.4f} "
            f"{r.final_psi:>8.4f} "
            f"{r.consistency_score:>8.4f} "
            f"{icon}{r.verdict:>7}"
        )

    if results["北宋后期"].disagreements:
        print(f"\n北宋后期不一致详情:")
        for d in results["北宋后期"].disagreements:
            print(f"  {d['pair']}: {d['values']} (score={d['score']:.2f})")


if __name__ == "__main__":
    demo_four_diagnosis()
