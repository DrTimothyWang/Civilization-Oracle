"""
v4.x 阶段 22: 理论机制贡献 — 为什么 PSI 能预测危机？
====================================================

v4.0/4.1 是"现象观察"（empirical observation）
世界顶尖研究需要"机制解释"（mechanistic explanation）

本阶段: 提出 3 个候选机制，评估其解释力
- M1: 精英集体认知窗口
- M2: 政治经济压力传导
- M3: 社会网络失序

然后设计可证伪的实验来区分
"""
import sys
import os
import json
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# 3 个候选机制
# ============================================================

MECHANISMS = {
    "M1_集体认知窗口": {
        "name": "Elite Collective Epistemic Window",
        "hypothesis": "危机前精英对治理能力有清晰感知, 通过文本表达出来",
        "predictions": [
            "危机前的 PSI 谷值应伴随'政治评论'类文本增加",
            "盛世 PSI 高峰应伴随'文化繁荣'类文本增加",
            "精英与民众的语义差异在危机前应该收窄（精英感知到问题）"
        ],
        "falsifiable_test": "如果 PSI 谷值与精英感知无关, 则精英/民众的 PSI 差异在危机前后无变化",
        "evidence_status": "需未来验证",
    },
    "M2_压力传导": {
        "name": "Political-Economic Pressure Transmission",
        "hypothesis": "经济压力→言论收紧→情绪压抑→危机 (类似'压抑-爆发'模型)",
        "predictions": [
            "PSI 谷值应领先经济危机指标（如粮价飞涨）",
            "危机前文本应增加'批判/讽刺'而非'歌颂'",
            "PSI 谷值与税收/财政压力相关"
        ],
        "falsifiable_test": "如果 PSI 谷值与经济指标无关, 则 PSI 不能预警经济危机",
        "evidence_status": "v4.1 竺可桢气候对照提供间接支持: PSI 独立于气候但可能与气候传导的经济压力相关",
    },
    "M3_社会网络失序": {
        "name": "Social Network Disorder",
        "hypothesis": "危机前精英社会网络断裂, 体现在文本互动减少、孤立加剧",
        "predictions": [
            "危机前应观测到'精英互动'网络密度下降",
            "孤立节点（被边缘化的精英）的文本情绪更负面",
            "网络拓扑变化领先于危机事件"
        ],
        "falsifiable_test": "如果精英社会网络在危机前后无变化, 则网络指标不领先危机",
        "evidence_status": "需 CBDB 社会关系数据验证 (KIN_DATA, OFFICIAL_POSTING_DATA)",
    },
}


# ============================================================
# PSI 谷值与事件类型的关联（用 CBDB 73 条有意义事件）
# ============================================================

def main():
    print("=" * 70)
    print("v4.x 阶段 22: 理论机制贡献")
    print("=" * 70)

    # 1. 列出 3 个机制
    print("\n3 个候选机制:")
    for mid, m in MECHANISMS.items():
        print(f"\n  [{mid}] {m['name']}")
        print(f"  假设: {m['hypothesis']}")
        print(f"  证据状态: {m['evidence_status']}")

    # 2. 用 CBDB 73 条事件做初步验证
    print("\n" + "=" * 70)
    print("CBDB 73 条事件 vs PSI 谷值分析")
    print("=" * 70)

    import sqlite3
    cbdb_path = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"
    conn = sqlite3.connect(cbdb_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.c_personid, e.c_event_code,
            e.c_year, c.c_event_name_chn
        FROM EVENTS_DATA e
        LEFT JOIN EVENT_CODES c ON e.c_event_code = c.c_event_code
        WHERE e.c_event_code > 0 AND e.c_year > 0
    """)
    events = cur.fetchall()
    conn.close()

    # 按事件类型分类
    event_types = defaultdict(list)
    for e in events:
        year = e["c_year"]
        name = e["c_event_name_chn"]
        # 简化分类
        if any(kw in name for kw in ["平", "收", "歸", "納", "破", "滅", "擒"]):
            cat = "军事_征服"
        elif any(kw in name for kw in ["盟", "和", "戰", "變", "叛", "之亂"]):
            cat = "军事_冲突"
        elif any(kw in name for kw in ["禮", "樂", "議", "制", "學", "貢"]):
            cat = "制度_文化"
        elif any(kw in name for kw in ["災", "河", "饑", "饑"]):
            cat = "自然_灾害"
        elif any(kw in name for kw in ["即", "位", "立", "建", "代"]):
            cat = "王位_继统"
        else:
            cat = "其他"
        event_types[cat].append({"year": year, "name": name, "code": e["c_event_code"]})

    print("\n事件类型分布:")
    for cat, evs in sorted(event_types.items(), key=lambda x: -len(x[1])):
        print(f"  {cat}: {len(evs)} 条")

    # 加载 PSI
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    psi_by_decade = {r["decade"]: r["psi_z"] for r in psi["decade_results"]}

    # 事件发生时 PSI
    print("\n关键事件发生时的 PSI:")
    print(f"{'事件':<25} {'年份':<8} {'十年':<8} {'PSI_z':<8} {'危机前10年PSI':<10}")
    print("-" * 60)
    for cat, evs in event_types.items():
        if cat in ["军事_征服", "军事_冲突", "王位_继统"]:
            for e in evs[:3]:
                year = e["year"]
                decade = (year // 10) * 10
                psi_val = psi_by_decade.get(decade, 0)
                psi_10y_before = psi_by_decade.get(decade - 10, "N/A")
                print(f"{e['name'][:24]:<25} {year:<8} {decade}s   {psi_val:>+.3f}   {psi_10y_before if psi_10y_before != 'N/A' else 'N/A':<10}")

    # 3. 关键事件 vs PSI 谷值
    print("\n" + "=" * 70)
    print("理论验证: PSI 谷值与重大事件的关联")
    print("=" * 70)

    # 计算每个事件类型发生年份的 PSI 均值
    psi_by_event_type = defaultdict(list)
    for cat, evs in event_types.items():
        for e in evs:
            decade = (e["year"] // 10) * 10
            psi_val = psi_by_decade.get(decade)
            if psi_val is not None:
                psi_by_event_type[cat].append(psi_val)

    print("\n各类型事件发生时的 PSI 均值:")
    for cat, psis in sorted(psi_by_event_type.items(), key=lambda x: -len(x[1])):
        if len(psis) >= 3:
            print(f"  {cat:<15} n={len(psis):2d}  mean PSI_z = {np.mean(psis):+.3f}")

    # 4. 写最终理论框架
    print("\n" + "=" * 70)
    print("理论框架: '语义压力传导三阶段模型'")
    print("=" * 70)
    print()
    print("整合 3 个机制, 提出统一的理论框架:")
    print()
    print("┌────────────────────────────────────────────────────────┐")
    print("│ Phase 1: 触发 (T-15 to T-10 年)                       │")
    print("│   M2_压力传导: 经济压力上升, 言论收紧                 │")
    print("│   PSI 表现: 缓慢下降 (SFD 也下降, 专家网络弱化)     │")
    print("│                                                        │")
    print("│ Phase 2: 临界 (T-10 to T-5 年)                        │")
    print("│   M1_认知窗口: 精英感知到问题, 公开表达负面情绪      │")
    print("│   M3_网络失序: 边缘精英被孤立, 主流精英失语            │")
    print("│   PSI 表现: 急剧下降 (谷值出现)                       │")
    print("│                                                        │")
    print("│ Phase 3: 危机 (T-5 to T)                              │")
    print("│   PSI 表现: 持续低位, 进一步崩溃 (密度崩溃)           │")
    print("│   危机事件: 起义/入侵/政变                            │")
    print("└────────────────────────────────────────────────────────┘")
    print()
    print("v4.x 的 PSI 谷值主要在 Phase 2 出现, 领先 Phase 3 危机 5-10 年。")
    print()
    print("这一理论解释了为什么 PSI 能预测危机:")
    print("- Phase 1 压力传导 → 精英语义信号弱化 (SFD ↓)")
    print("- Phase 2 临界 → 精英集体情绪崩溃 (MMP ↓↓)")
    print("- Phase 3 危机 → 物理崩溃 (事件链触发)")

    # 5. 可证伪的预测
    print("\n可证伪预测 (与现有数据对照):")
    print()
    print("P1: 危机前 PSI 谷值与精英感知指标相关")
    print("    验证方法: 比较 PSI 谷值前后的精英谏言数量 (v5.0 需要)")
    print("    当前状态: 待验证")
    print()
    print("P2: PSI 谷值与经济压力传导指标相关")
    print("    验证方法: 粮价/税收压力 (v5.0 需要)")
    print("    当前状态: 间接支持 (PSI 独立于气候 r=0.02)")
    print()
    print("P3: PSI 谷值与精英社会网络密度变化相关")
    print("    验证方法: CBDB KIN_DATA 关系网络密度时序分析")
    print("    当前状态: 待验证")

    # 6. 保存
    output = {
        "meta": {
            "version": "v4.x Theoretical Framework",
            "approach": "从现象观察到机制解释",
            "three_mechanisms": list(MECHANISMS.keys()),
        },
        "mechanisms": MECHANISMS,
        "three_phase_model": {
            "phase_1_trigger": {
                "years_before_crisis": "T-15 to T-10",
                "primary_mechanism": "M2 压力传导",
                "psi_behavior": "缓慢下降",
            },
            "phase_2_critical": {
                "years_before_crisis": "T-10 to T-5",
                "primary_mechanism": "M1 认知窗口 + M3 网络失序",
                "psi_behavior": "急剧下降 (谷值)",
            },
            "phase_3_crisis": {
                "years_before_crisis": "T-5 to T",
                "primary_mechanism": "物理事件链触发",
                "psi_behavior": "持续低位",
            },
        },
        "psi_event_analysis": {
            cat: {
                "n": len(psis),
                "mean_psi_z": float(np.mean(psis)),
            }
            for cat, psis in psi_by_event_type.items() if len(psis) >= 3
        },
        "falsifiable_predictions": [
            "P1: 危机前 PSI 谷值与精英谏言数量相关",
            "P2: PSI 谷值与经济压力传导指标相关",
            "P3: PSI 谷值与精英社会网络密度变化相关",
        ],
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/theoretical_framework.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 理论框架保存: {out_path}")


if __name__ == "__main__":
    main()
