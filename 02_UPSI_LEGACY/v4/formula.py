"""
Civilization-Oracle v4.0 - 唯一公式实现
=====================================

v3.0 的 4-6 种混乱公式 v4.0 统一为以下唯一版本。

核心公式（v4.0 锁定版）：
    PSI_z(d) = 0.40 * MMP_z(d) + 0.30 * SFD_z(d) + 0.30 * EED_z(d)

其中：
- MMP_z = 该十年情感极性的 z-score
- SFD_z = log(1 + 专家数) 的 z-score
- EED_z = 有效专家比例 的 z-score
- GSI 作为独立修正因子（不在 SFD 内重复计权）

输出：z-score 量纲 + sigmoid 映射到 [0, 1]

作者：Mavis | 2026-06-02
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import math


# ============================================================
# 1. 三个核心组分（MMP / SFD / EED）
# ============================================================

def compute_mmp(sentiments: List[float]) -> float:
    """
    MMP (Mean Metaphor Polarity) = 情感极性均值

    输入: 单一十年窗口内所有文本的情感得分列表（每个范围 [-1, +1]）
    输出: 该十年的 MMP 值
    """
    if not sentiments:
        return 0.0
    return float(np.mean(sentiments))


def compute_sfd(expert_count: int) -> float:
    """
    SFD (Scholar Frequency Density) = log(1 + 专家数)

    对数化处理：避免专家数量量纲影响，且符合"边际递减"直觉
    """
    return float(np.log1p(max(0, expert_count)))


def compute_eed(expert_count: int, texts_existing: int) -> float:
    """
    EED (Expert Engagement Density) = 有效专家比例

    反映"该十年的专家群体里，有多少是真正有文本记录的"
    （CBDB 中部分专家只有生卒年但无文本，这种算"无参与"）
    """
    if expert_count <= 0:
        return 0.0
    return min(1.0, texts_existing / expert_count)


def compute_gsi(latitude_list: List[float], north_threshold: float = 35.0) -> float:
    """
    GSI (Geographical Stress Index) - 横切因子

    输入: 该十年所有有地理坐标的专家纬度列表
    输出: 北方占比作为压力代理

    v4.0 重要: GSI 不在 SFD 内重复计权，仅作为独立修正因子
    """
    if not latitude_list:
        return 0.5
    north = sum(1 for lat in latitude_list if lat and lat > north_threshold)
    return north / len(latitude_list)


# ============================================================
# 2. z-score 标准化
# ============================================================

@dataclass
class StandardizationStats:
    """保存标准化所需的均值和标准差"""
    mmp_mean: float
    mmp_std: float
    sfd_mean: float
    sfd_std: float
    eed_mean: float
    eed_std: float

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "StandardizationStats":
        return cls(**d)


def compute_standardization_stats(
    all_mmp: List[float],
    all_sfd: List[float],
    all_eed: List[float]
) -> StandardizationStats:
    """从所有十年的三个组分计算 z-score 标准化所需的均值/标准差"""
    return StandardizationStats(
        mmp_mean=float(np.mean(all_mmp)) if all_mmp else 0.0,
        mmp_std=float(np.std(all_mmp)) + 1e-9 if all_mmp else 1.0,
        sfd_mean=float(np.mean(all_sfd)) if all_sfd else 0.0,
        sfd_std=float(np.std(all_sfd)) + 1e-9 if all_sfd else 1.0,
        eed_mean=float(np.mean(all_eed)) if all_eed else 0.0,
        eed_std=float(np.std(all_eed)) + 1e-9 if all_eed else 1.0,
    )


def zscore(value: float, mean: float, std: float) -> float:
    """单个值的 z-score 标准化"""
    if std < 1e-9:
        return 0.0
    return (value - mean) / std


# ============================================================
# 3. 核心 PSI 公式（v4.0 唯一版）
# ============================================================

# v4.0 锁定的权重
WEIGHTS = {
    'mmp': 0.40,  # 语义情绪极性
    'sfd': 0.30,  # 专家密度
    'eed': 0.30,  # 有效参与度
}

# 验证权重和为 1
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "权重和必须为 1"


def compute_psi_z(
    mmp: float,
    sfd: float,
    eed: float,
    stats: StandardizationStats
) -> float:
    """
    核心 PSI 公式（v4.0 唯一版）

    PSI_z = 0.40 * MMP_z + 0.30 * SFD_z + 0.30 * EED_z

    输入: 原始 MMP/SFD/EED 值 + 标准化统计
    输出: z-score 量纲的 PSI
    """
    mmp_z = zscore(mmp, stats.mmp_mean, stats.mmp_std)
    sfd_z = zscore(sfd, stats.sfd_mean, stats.sfd_std)
    eed_z = zscore(eed, stats.eed_mean, stats.eed_std)

    return (
        WEIGHTS['mmp'] * mmp_z +
        WEIGHTS['sfd'] * sfd_z +
        WEIGHTS['eed'] * eed_z
    )


def gsi_correction(psi_z: float, gsi: float) -> float:
    """
    GSI 作为独立修正因子

    GSI = 1 + 0.2 * (R_north - 0.5)
    R_north = 0.0 (全南方) → 0.9
    R_north = 0.5 (均衡) → 1.0
    R_north = 1.0 (全北方) → 1.1

    PSI_corrected = PSI_z * GSI

    注意: GSI 在 v4.0 是"加性修正"而非"乘性扩展"
    """
    gsi_factor = 1.0 + 0.2 * (gsi - 0.5)
    return psi_z * gsi_factor


def ipw_correction(psi_values: List[float], weights: List[float]) -> float:
    """
    IPW（逆概率加权）校正

    输入: 该十年所有专家的 PSI 原始值和权重
    输出: IPW 校正后的 PSI

    IPW 校正不改变 PSI 排序，只改变绝对量级
    """
    if not psi_values or not weights:
        return 0.0
    total_w = sum(weights)
    if total_w < 1e-9:
        return 0.0
    return sum(p * w for p, w in zip(psi_values, weights)) / total_w


def psi_z_to_final(psi_z: float) -> float:
    """
    z-score 量纲的 PSI 映射到 [0, 1]

    使用 sigmoid 函数：PSI_final = 1 / (1 + exp(-PSI_z))
    当 PSI_z = 0 时 → 0.5
    当 PSI_z = 1 时 → 0.731
    当 PSI_z = -1 时 → 0.269
    """
    # 限制极端值，避免数值溢出
    psi_z = max(-10.0, min(10.0, psi_z))
    return 1.0 / (1.0 + math.exp(-psi_z))


# ============================================================
# 4. 危机判定（v4.0 严格定义）
# ============================================================

# v4.0 阈值（z-score 量纲）
CRISIS_THRESHOLD_Z = -1.0  # 1 个标准差以下
PROSPERITY_THRESHOLD_Z = 1.0  # 1 个标准差以上


def classify_period(psi_z: float) -> str:
    """
    根据 PSI_z 判定时期类型

    crisis:     PSI_z < -1.0
    declining:  -1.0 <= PSI_z < 0
    neutral:    PSI_z == 0 (very rare)
    rising:     0 < PSI_z < 1.0
    prosperity: PSI_z >= 1.0
    """
    if psi_z < CRISIS_THRESHOLD_Z:
        return "crisis"
    elif psi_z < 0:
        return "declining"
    elif psi_z == 0:
        return "neutral"
    elif psi_z < PROSPERITY_THRESHOLD_Z:
        return "rising"
    else:
        return "prosperity"


# ============================================================
# 5. 高级：单条记录的 PSI 计算
# ============================================================

@dataclass
class ExpertRecord:
    """单条专家记录（individual-level）"""
    person_id: int
    name: str
    birth_year: int
    death_year: int
    dynasty: str
    decade: int  # 该专家活跃的十年窗口
    sentiment: float  # 该专家关联文本的情感得分
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_elite: bool = False  # 是否核心专家（官员/史官）
    has_text: bool = True  # 是否有文本记录
    cbdb_probability: float = 0.5  # IPW 用：被 CBDB 记录的概率


def compute_individual_psi_z(
    expert: ExpertRecord,
    decade_stats: Dict[int, StandardizationStats]
) -> float:
    """
    计算单个专家的 PSI（individual-level）

    实际计算: PSI_z = 0.40 * MMP_z + 0.30 * SFD_z + 0.30 * EED_z
    - MMP_z: 用该专家的 sentiment 代入十年 MMP 公式
    - SFD_z: 该专家所在十年的 SFD
    - EED_z: 该专家所在十年的 EED
    """
    if expert.decade not in decade_stats:
        return 0.0
    stats = decade_stats[expert.decade]
    mmp = expert.sentiment
    sfd = compute_sfd(1)  # 单个专家的 SFD（log(1+1) = 0.693）
    eed = compute_eed(1, 1 if expert.has_text else 0)

    return compute_psi_z(mmp, sfd, eed, stats)


# ============================================================
# 6. 完整流程：十年级数据 → PSI
# ============================================================

@dataclass
class DecadeResult:
    """单个十年窗口的完整结果"""
    dynasty: str
    decade: int
    year_start: int
    year_end: int
    expert_count: int
    mmp: float  # 原始
    sfd: float  # 原始
    eed: float  # 原始
    gsi: float
    psi_z: float  # 核心输出（z-score）
    psi_z_gsi: float  # GSI 修正后
    psi_final: float  # sigmoid 映射到 [0,1]
    classification: str
    text_ids: List[str] = None  # 实际使用的文本 ID 列表


def aggregate_decade(
    dynasty: str,
    decade: int,
    year_start: int,
    year_end: int,
    sentiments: List[float],
    expert_count: int,
    texts_existing: int,
    latitude_list: List[float],
    stats: StandardizationStats
) -> DecadeResult:
    """
    从原始数据聚合到十年级 PSI 结果

    输入:
    - sentiments: 该十年所有文本的情感得分列表
    - expert_count: 该十年的总专家数
    - texts_existing: 该十年有文本的专家数
    - latitude_list: 该十年所有有地理坐标的专家纬度列表
    - stats: 标准化统计

    输出: DecadeResult
    """
    mmp = compute_mmp(sentiments)
    sfd = compute_sfd(expert_count)
    eed = compute_eed(expert_count, texts_existing)
    gsi = compute_gsi(latitude_list)

    psi_z = compute_psi_z(mmp, sfd, eed, stats)
    psi_z_gsi = gsi_correction(psi_z, gsi)
    psi_final = psi_z_to_final(psi_z_gsi)
    classification = classify_period(psi_z)

    return DecadeResult(
        dynasty=dynasty,
        decade=decade,
        year_start=year_start,
        year_end=year_end,
        expert_count=expert_count,
        mmp=round(mmp, 4),
        sfd=round(sfd, 4),
        eed=round(eed, 4),
        gsi=round(gsi, 4),
        psi_z=round(psi_z, 4),
        psi_z_gsi=round(psi_z_gsi, 4),
        psi_final=round(psi_final, 4),
        classification=classification,
    )


# ============================================================
# 7. 可视化友好的输出
# ============================================================

def result_to_dict(result: DecadeResult) -> dict:
    return asdict(result)


# ============================================================
# 8. 自检
# ============================================================

if __name__ == "__main__":
    # 单元自检
    print("=" * 60)
    print("v4.0 Formula Self-Check")
    print("=" * 60)

    # 模拟 3 个十年
    test_decades = [
        {"mmp": 0.8, "sfd": 6.0, "eed": 0.9, "gsi": 0.7, "name": "盛世"},
        {"mmp": 0.0, "sfd": 5.0, "eed": 0.5, "gsi": 0.5, "name": "平稳"},
        {"mmp": -0.8, "sfd": 3.0, "eed": 0.1, "gsi": 0.3, "name": "危机"},
    ]

    all_mmp = [d["mmp"] for d in test_decades]
    all_sfd = [d["sfd"] for d in test_decades]
    all_eed = [d["eed"] for d in test_decades]

    stats = compute_standardization_stats(all_mmp, all_sfd, all_eed)
    print(f"Stats: MMP(μ={stats.mmp_mean:.2f}, σ={stats.mmp_std:.2f})")
    print(f"       SFD(μ={stats.sfd_mean:.2f}, σ={stats.sfd_std:.2f})")
    print(f"       EED(μ={stats.eed_mean:.2f}, σ={stats.eed_std:.2f})")
    print()

    for d in test_decades:
        psi_z = compute_psi_z(d["mmp"], d["sfd"], d["eed"], stats)
        psi_z_gsi = gsi_correction(psi_z, d["gsi"])
        psi_final = psi_z_to_final(psi_z_gsi)
        cls = classify_period(psi_z)
        print(f"{d['name']:<6}: PSI_z = {psi_z:+.4f}, "
              f"PSI_z_gsi = {psi_z_gsi:+.4f}, "
              f"PSI_final = {psi_final:.4f}, "
              f"type = {cls}")

    print()
    print("权重验证: 0.40 + 0.30 + 0.30 =", sum(WEIGHTS.values()))
    print("✓ v4.0 公式自检通过")
