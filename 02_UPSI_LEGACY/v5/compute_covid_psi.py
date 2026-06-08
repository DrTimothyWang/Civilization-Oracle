#!/usr/bin/env python3
"""
v5.0 阶段47a: COVID PSI
- OWID COVID-19 数据 (2020-2026)
- 200+ 国家日度
- PSI 三维度: MMP=病例增速, SFD=波动, EED=测试强度
- 检验 PSI 是否预测各国疫情高峰
"""
import csv
import json
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")
SRC = "/tmp/owid_covid.csv"


def main():
    # 读 OWID
    by_country = defaultdict(list)
    print("[load] reading OWID COVID data...")
    with open(SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row["location"]
            date = row["date"]
            try:
                new_cases = float(row["new_cases_smoothed"] or 0)
                new_deaths = float(row["new_deaths_smoothed"] or 0)
                icu = float(row["icu_patients"] or 0) if row["icu_patients"] else 0
                pos_rate = float(row["positive_rate"] or 0) if row["positive_rate"] else 0
                hosp = float(row["hosp_patients"] or 0) if row["hosp_patients"] else 0
            except:
                continue
            by_country[country].append({
                "date": date,
                "nc": new_cases,
                "nd": new_deaths,
                "icu": icu,
                "pos": pos_rate,
                "hosp": hosp,
            })
    print(f"[load] {len(by_country)} countries, e.g. {list(by_country.keys())[:5]}")

    # 选大国家
    major = ["United States", "India", "Brazil", "Germany", "United Kingdom", "France",
             "Italy", "Spain", "Japan", "South Korea", "China", "Russia", "Canada",
             "Australia", "Mexico", "Indonesia", "Netherlands", "Saudi Arabia",
             "Turkey", "Switzerland", "Argentina", "Iran", "Sweden", "Belgium"]
    major = [c for c in major if c in by_country]

    # PSI 公式 (疫情版)
    # MMP_z: 14 日病例增速 z-score
    # SFD_z: 14 日病例波动率
    # EED_z: 14 日阳性率/ICU 占用

    results = {}
    for c in major:
        data = sorted(by_country[c], key=lambda x: x["date"])
        ncs = [d["nc"] for d in data]
        dates = [d["date"] for d in data]
        if len(ncs) < 60:
            continue
        # 计算三维度 (rolling 14 天)
        L = len(ncs) - 14
        mmp_z, sfd_z, eed_z = [], [], []
        for i in range(14, len(ncs)):
            window = ncs[i-14:i+1]
            if not any(window):
                continue
            # MMP: 当前 vs 14 日前增长率
            base = sum(window[:14]) / 14
            current = window[-1]
            growth = (current - base) / max(base, 1)
            mmp_z.append(growth)
            # SFD: 14 日 std
            sfd_z.append(statistics.stdev(window) if len(window) > 1 else 0)
            # EED: 住院率
            hosp = data[i]["hosp"] or 0
            eed_z.append(hosp)

        # 标准化
        def zscore(arr):
            if not arr or statistics.stdev(arr) == 0:
                return [0] * len(arr)
            mu = statistics.mean(arr)
            sd = statistics.stdev(arr)
            return [(x - mu) / sd for x in arr]

        m = zscore(mmp_z)
        s = zscore(sfd_z)
        e = zscore(eed_z)
        L = min(len(m), len(s), len(e))
        psi = [0.4*mm + 0.3*ss + 0.3*ee for mm, ss, ee in zip(m[-L:], s[-L:], e[-L:])]

        # 找 PSI 极小值 (疫情高峰前夕)
        psi_min_idx = psi.index(min(psi))
        psi_min_date = dates[14 + psi_min_idx]
        # 找实际病例高峰
        max_idx = ncs.index(max(ncs[60:]))  # 跳过早期
        max_date = dates[max_idx]

        results[c] = {
            "n": len(psi),
            "psi_min": min(psi),
            "psi_max": max(psi),
            "psi_min_date": psi_min_date,
            "max_cases_date": max_date,
            "max_cases": max(ncs[60:]),
            "lead_days": (datetime.strptime(max_date, "%Y-%m-%d") - datetime.strptime(psi_min_date, "%Y-%m-%d")).days,
        }
        print(f"  {c:20s} | PSI_min {psi_min_date} | 实际高峰 {max_date} | Lead {results[c]['lead_days']:4d} 天")

    # 检验: PSI 极小是否领先实际高峰
    print("\n" + "=" * 80)
    print("【COVID PSI 检验】 PSI 极小点 vs 实际病例高峰 (Lead)")
    print("=" * 80)
    valid = [r for r in results.values() if abs(r["lead_days"]) < 365]
    leads = [r["lead_days"] for r in valid]
    pos_leads = [l for l in leads if l > 0]
    print(f"  有效国家: {len(valid)}")
    print(f"  PSI 领先实际高峰: {len(pos_leads)}/{len(valid)} = {len(pos_leads)/len(valid):.0%}")
    print(f"  平均 Lead: {statistics.mean(leads):.1f} 天" if leads else "")
    print(f"  中位 Lead: {statistics.median(leads):.1f} 天" if leads else "")

    # 保存
    with open(OUT / "covid_psi_v5.json", "w", encoding="utf-8") as f:
        json.dump({"results": results,
                   "summary": {
                       "n_countries": len(valid),
                       "n_psi_leads": len(pos_leads),
                       "lead_rate": len(pos_leads)/len(valid) if valid else 0,
                       "avg_lead_days": statistics.mean(leads) if leads else 0,
                   }}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/covid_psi_v5.json")
    return results


if __name__ == "__main__":
    main()
