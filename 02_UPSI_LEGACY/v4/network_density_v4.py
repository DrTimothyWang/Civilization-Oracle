"""
v4.x 阶段 22b: 精英社会网络密度分析 (机制 M3 验证)
================================================

假说: 危机前精英社会网络断裂 → 网络密度下降 → 体现在 PSI 谷值

CBDB 数据:
- KIN_DATA: 556,767 条亲属关系
- POSTED_TO_OFFICE_DATA: 588,294 条任职关系
- 30,518 个专家

按十年计算网络密度 = 关系数 / 专家数
检验是否与 PSI 谷值相关
"""
import sys
import os
import json
import sqlite3
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def compute_network_density_by_decade():
    """计算每十年的精英网络密度"""
    cbdb_path = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"
    conn = sqlite3.connect(cbdb_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 十年区间
    decade_ranges = [
        (610, 919, "唐朝"),
        (960, 1127, "北宋"),
        (1128, 1279, "南宋"),
        (1368, 1644, "明朝"),
    ]

    results = []

    for start, end, dy in decade_ranges:
        for decade in range(start, end, 10):
            # 该十年的专家数
            cur.execute("""
                SELECT COUNT(DISTINCT c_personid) FROM biog_main
                WHERE c_birthyear >= ? AND c_birthyear < ?
            """, (decade, decade + 10))
            n_experts = cur.fetchone()[0]

            if n_experts == 0:
                continue

            # 关系数
            cur.execute("""
                SELECT COUNT(*) FROM KIN_DATA
                WHERE c_personid IN (
                    SELECT c_personid FROM biog_main
                    WHERE c_birthyear >= ? AND c_birthyear < ?
                )
            """, (decade, decade + 10))
            kin_count = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*) FROM POSTED_TO_OFFICE_DATA
                WHERE c_personid IN (
                    SELECT c_personid FROM biog_main
                    WHERE c_birthyear >= ? AND c_birthyear < ?
                )
            """, (decade, decade + 10))
            office_count = cur.fetchone()[0]

            total_relations = kin_count + office_count
            density = total_relations / n_experts if n_experts > 0 else 0

            results.append({
                "decade": decade,
                "dynasty": dy,
                "n_experts": n_experts,
                "kin_relations": kin_count,
                "office_relations": office_count,
                "total_relations": total_relations,
                "density": density,
            })

    conn.close()
    return results


def main():
    print("=" * 70)
    print("v4.x 阶段 22b: 精英社会网络密度分析")
    print("=" * 70)

    # 1. 计算网络密度
    print("\n步骤 1: 计算每十年精英网络密度")
    network_data = compute_network_density_by_decade()
    print(f"  处理 {len(network_data)} 个十年窗口")

    # 2. 加载 PSI
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    psi_by_decade = {r["decade"]: r["psi_z"] for r in psi["decade_results"]}

    # 3. 合并数据
    print("\n步骤 2: 合并 PSI 和网络密度")
    combined = []
    for nd in network_data:
        if nd["decade"] in psi_by_decade:
            nd["psi_z"] = psi_by_decade[nd["decade"]]
            combined.append(nd)

    # 4. 关键时段分析
    print("\n步骤 3: 关键危机前后的网络密度变化")
    print(f"{'时期':<20} {'十年':<8} {'dynasty':<6} {'n_experts':<10} {'relations':<12} {'density':<8} {'PSI_z':<8}")
    print("-" * 75)

    key_decades = [
        # 唐朝
        710, 750, 800, 850, 870,  # 开元盛世到黄巢前夕
        # 北宋
        1020, 1050, 1080, 1100, 1120,  # 仁宗到靖康
        # 南宋
        1180, 1230, 1270,  # 偏安到崖山
        # 明朝
        1410, 1500, 1580, 1620, 1640,  # 永乐到明亡
    ]
    for dec in key_decades:
        for nd in combined:
            if nd["decade"] == dec:
                density_norm = nd["density"] / 10  # 归一化
                print(f"{'':.<20} {dec}s  {nd['dynasty']:<6} {nd['n_experts']:<10} "
                      f"{nd['total_relations']:<12} {nd['density']:.1f}      {nd['psi_z']:+.3f}")
                break

    # 5. 计算网络密度 vs PSI 相关性
    print("\n步骤 4: 网络密度 vs PSI 相关性")
    if len(combined) > 10:
        densities = np.array([nd["density"] for nd in combined])
        psis = np.array([nd["psi_z"] for nd in combined])

        # Pearson 相关
        if np.std(densities) > 0 and np.std(psis) > 0:
            r = np.corrcoef(densities, psis)[0, 1]
            print(f"  跨所有朝代网络密度 vs PSI: r = {r:.4f}")
            if abs(r) < 0.2:
                print("    → 弱相关: 网络密度不直接预测 PSI（但可能间接作用）")
            else:
                print(f"    → 强相关 (r={r:.3f})")

    # 6. 按朝代分层
    print("\n步骤 5: 按朝代分层")
    by_dy = defaultdict(list)
    for nd in combined:
        by_dy[nd["dynasty"]].append(nd)

    for dy in ["唐朝", "北宋", "南宋", "明朝"]:
        if dy not in by_dy:
            continue
        dds = np.array([x["density"] for x in by_dy[dy]])
        pps = np.array([x["psi_z"] for x in by_dy[dy]])
        if len(dds) > 2 and np.std(dds) > 0 and np.std(pps) > 0:
            r = np.corrcoef(dds, pps)[0, 1]
            print(f"  {dy}: 网络密度 vs PSI r = {r:.4f} (n={len(dds)})")

    # 7. 关键危机前的网络密度变化
    print("\n步骤 6: 关键危机前 5-10 年的网络密度变化")
    crisis_5y_before = {
        755: 750,  # 安史之乱前 5 年
        875: 870,  # 黄巢
        907: 900,  # 唐亡
        1127: 1120,  # 靖康
        1279: 1270,  # 崖山
        1644: 1640,  # 明亡
    }
    crisis_15y_before = {
        755: 740, 875: 860, 907: 890, 1127: 1110, 1279: 1260, 1644: 1630
    }

    print(f"{'危机':<15} {'前15年密度':<12} {'前5年密度':<12} {'变化':<10} {'前5年PSI':<10}")
    print("-" * 60)
    for cy, d5 in crisis_5y_before.items():
        d15 = crisis_15y_before[cy]
        d15_val = next((x["density"] for x in combined if x["decade"] == d15), 0)
        d5_val = next((x["density"] for x in combined if x["decade"] == d5), 0)
        psi_5y = psi_by_decade.get(d5, 0)
        change = ((d5_val - d15_val) / d15_val * 100) if d15_val > 0 else 0
        print(f"{cy} 危机    {d15_val:.1f}        {d5_val:.1f}        {change:+.1f}%     {psi_5y:+.3f}")

    # 8. 保存
    output = {
        "meta": {
            "version": "v4.x M3 Mechanism Test",
            "data_source": "CBDB KIN_DATA + POSTED_TO_OFFICE_DATA",
            "hypothesis": "Crisis前精英网络密度下降（M3 机制）",
        },
        "network_data": combined,
        "overall_correlation": float(r) if len(combined) > 10 else None,
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/network_density_v4.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 网络密度数据保存: {out_path}")


if __name__ == "__main__":
    main()
