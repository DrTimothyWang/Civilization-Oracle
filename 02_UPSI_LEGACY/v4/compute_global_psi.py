#!/usr/bin/env python3
"""
阶段 40: 全球 PSI 多国家计算
- 13 个国家 + 4 类资产
- 1927-2026 (99 年美股)
- 检验 PSI<-0.5 在每个市场的已知危机日期
"""
import json
import statistics
from pathlib import Path
from datetime import datetime

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")

with open(DATA / "global_market_data.json", encoding="utf-8") as f:
    raw = json.load(f)


def returns(prices):
    return [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]


def rolling_max_drawdown(prices, window=60):
    out = []
    for i in range(window, len(prices)):
        sub = prices[i-window:i+1]
        peak = max(sub)
        out.append(sub[-1] / peak - 1)
    return out


def rolling_vol(rets, window=20):
    out = []
    for i in range(window, len(rets)):
        sub = rets[i-window:i]
        out.append(statistics.stdev(sub) * (252**0.5) if len(sub) > 1 else 0)
    return out


def compute_psi(bars, window_eed=60):
    bars.sort(key=lambda x: x[0])
    dates = [b[0] for b in bars]
    prices = [b[1] for b in bars]
    vols = [b[2] for b in bars]

    rets = returns(prices)
    mmp = rolling_max_drawdown(prices, 60)
    sfd = rolling_vol(rets, 20)

    eed = []
    for i in range(window_eed, len(vols)):
        sub = vols[i-window_eed:i]
        if sub and statistics.mean(sub) > 0:
            eed.append(vols[i] / statistics.mean(sub) - 1)
        else:
            eed.append(0)

    # 如果 volume 全为 0 (俄股), EED 用价格波动率 (parkinson) 替代
    if all(v == 0 for v in vols) and len(bars) > 0:
        # 用 high-low 范围估计
        eed = []
        for i in range(window_eed, len(bars)):
            window_data = bars[i-window_eed:i+1]
            if len(window_data) < 2:
                eed.append(0)
                continue
            # 用价格变化绝对值
            avg_abs_change = statistics.mean([abs(window_data[j][1] - window_data[j-1][1]) / window_data[j-1][1]
                                              for j in range(1, len(window_data)) if window_data[j-1][1] > 0])
            eed.append(avg_abs_change if avg_abs_change else 0)

    L = min(len(mmp), len(sfd), len(eed))
    mmp = mmp[-L:]
    sfd = sfd[-L:]
    eed = eed[-L:]

    mmp_mu, mmp_sd = statistics.mean(mmp), statistics.stdev(mmp)
    sfd_mu, sfd_sd = statistics.mean(sfd), statistics.stdev(sfd)
    eed_mu, eed_sd = statistics.mean(eed), statistics.stdev(eed)

    mmp_z = [(x-mmp_mu)/mmp_sd for x in mmp]
    sfd_z = [(x-sfd_mu)/sfd_sd for x in sfd]
    eed_z = [-(x-eed_mu)/eed_sd if eed_sd > 0 else 0 for x in eed]

    psi = [0.4*m + 0.3*s + 0.3*e for m, s, e in zip(mmp_z, sfd_z, eed_z)]
    offset = len(dates) - L
    return {"dates": dates[offset:], "psi": psi, "mmp": mmp_z, "sfd": sfd_z, "eed": eed_z, "prices": prices[offset:]}


# 已知历史金融危机 (NBER + 国际事件)
HISTORICAL_CRISES = [
    ("1929-10-29", "1929 大萧条"),
    ("1937-05-01", "1937 二萧"),
    ("1945-08-15", "1945 二战结束"),
    ("1962-05-28", "1962 古巴导弹"),
    ("1973-10-17", "1973 石油危机"),
    ("1980-01-01", "1980 沃克尔紧缩"),
    ("1987-10-19", "1987 黑色星期一"),
    ("1990-08-02", "1990 海湾战争"),
    ("1997-10-27", "1997 亚洲金融"),
    ("1998-08-17", "1998 俄罗斯违约"),
    ("2000-03-10", "2000 互联网泡沫"),
    ("2001-09-11", "2001 911"),
    ("2007-10-09", "2007 次贷危机"),
    ("2008-09-15", "2008 雷曼"),
    ("2009-03-09", "2009 市场底"),
    ("2010-05-06", "2010 闪崩"),
    ("2011-08-08", "2011 美债降级"),
    ("2015-06-12", "2015 中国股灾"),
    ("2016-06-23", "2016 英国脱欧"),
    ("2018-12-24", "2018 美股圣诞"),
    ("2020-03-23", "2020 COVID 底"),
    ("2022-02-24", "2022 俄乌"),
    ("2023-03-10", "2023 SVB"),
    ("2024-08-05", "2024 套利崩"),
]


def main():
    results = {}
    for name, bars in raw.items():
        if not bars or len(bars) < 200:
            continue
        print(f"[{name}] {len(bars)} bars, {bars[0][0]} ~ {bars[-1][0]}", end=" ")
        r = compute_psi(bars)
        results[name] = {
            "dates": r["dates"],
            "psi": r["psi"],
            "mmp_z": r["mmp"],
            "sfd_z": r["sfd"],
            "eed_z": r["eed"],
            "prices": r["prices"],
            "n": len(r["psi"]),
            "psi_min": min(r["psi"]),
            "psi_max": max(r["psi"]),
        }
        n_neg = sum(1 for p in r["psi"] if p < -0.5)
        print(f"| min={results[name]['psi_min']:.2f}, max={results[name]['psi_max']:.2f}, n_neg<-0.5={n_neg}")

    # 检验 13 国 + 资产 × 24 历史危机
    print("\n" + "=" * 80)
    print("【全球 PSI 危机检验】 PSI<-0.5 预警召回率")
    print("=" * 80)
    summary = {}
    for name, r in results.items():
        date_to_psi = dict(zip(r["dates"], r["psi"]))
        n_crises_in_range = 0
        n_predicted = 0
        leads = []
        for crisis_date, crisis_name in HISTORICAL_CRISES:
            if crisis_date not in date_to_psi:
                continue
            n_crises_in_range += 1
            crisis_idx = r["dates"].index(crisis_date)
            # 找前 180 天内 PSI<-0.5
            lead = None
            for i in range(crisis_idx, max(0, crisis_idx-180), -1):
                if r["psi"][i] < -0.5:
                    lead = crisis_idx - i
                    break
            if lead is not None:
                n_predicted += 1
                leads.append(lead)
        recall = n_predicted / n_crises_in_range if n_crises_in_range else 0
        avg_lead = statistics.mean(leads) if leads else 0
        summary[name] = {
            "n_crises": n_crises_in_range,
            "n_predicted": n_predicted,
            "recall": recall,
            "avg_lead_days": avg_lead,
        }
        print(f"  {name:12s} {r['n']:6d} 天 | {n_crises_in_range:2d} 个危机 | 预警 {n_predicted:2d} | 召回 {recall:5.0%} | 平均 Lead {avg_lead:5.1f} 天")

    # 跨域 PSI 相关矩阵
    print("\n" + "=" * 80)
    print("【跨域 PSI 相关性矩阵】 13 市场")
    print("=" * 80)
    markets = list(results.keys())
    # 找共同日期范围
    from datetime import datetime
    common_dates = set(results[markets[0]]["dates"])
    for m in markets[1:]:
        common_dates &= set(results[m]["dates"])
    common_dates = sorted(common_dates)
    print(f"  共同日期: {len(common_dates)} 天 ({common_dates[0]} ~ {common_dates[-1]})")

    corr_matrix = {}
    for m1 in markets:
        m1_map = dict(zip(results[m1]["dates"], results[m1]["psi"]))
        corr_matrix[m1] = {}
        for m2 in markets:
            m2_map = dict(zip(results[m2]["dates"], results[m2]["psi"]))
            xs = [m1_map[d] for d in common_dates]
            ys = [m2_map[d] for d in common_dates]
            if len(xs) > 30:
                mx, my = statistics.mean(xs), statistics.mean(ys)
                num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
                dx = (sum((x-mx)**2 for x in xs))**0.5
                dy = (sum((y-my)**2 for y in ys))**0.5
                r = num/(dx*dy) if dx*dy > 0 else 0
                corr_matrix[m1][m2] = round(r, 3)

    # 简表
    print(f"\n  {'':12s} | " + " | ".join(f"{m[:6]:6s}" for m in markets))
    for m1 in markets:
        row = " | ".join(f"{corr_matrix[m1].get(m2, 0):6.3f}" for m2 in markets)
        print(f"  {m1:12s} | {row}")

    # 保存
    out = {
        "results": {k: {"n": v["n"], "psi_min": v["psi_min"], "psi_max": v["psi_max"]} for k, v in results.items()},
        "summary": summary,
        "corr_matrix": corr_matrix,
        "n_common_days": len(common_dates),
    }
    with open(DATA / "global_psi_v4.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {DATA}/global_psi_v4.json")

    # 总计
    total_crises = sum(s["n_crises"] for s in summary.values())
    total_predicted = sum(s["n_predicted"] for s in summary.values())
    print(f"\n【总召回】 {total_predicted}/{total_crises} = {total_predicted/total_crises:.1%}")


if __name__ == "__main__":
    main()
