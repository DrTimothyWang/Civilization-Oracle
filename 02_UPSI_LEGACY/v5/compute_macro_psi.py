#!/usr/bin/env python3
"""
v5.0 阶段45b: 宏观 PSI 计算
- 11 个 FRED 宏观指标
- INDPRO 1919-2026 (107 年)
- 用类似 v4.x 公式但适配宏观

PSI_宏观 = 0.4×MMP_z + 0.3×SFD_z + 0.3×EED_z
- MMP: 12 月滚动最大回撤
- SFD: 12 月滚动波动率
- EED: 12 月 M2 增速 (流动性异常)
"""
import json
import statistics
from pathlib import Path

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")
with open(DATA / "fred_macro_data.json", encoding="utf-8") as f:
    raw = json.load(f)


def returns(vals):
    """月度环比变化率"""
    return [vals[i]/vals[i-1] - 1 for i in range(1, len(vals))]


def rolling_max_dd(vals, window=12):
    out = []
    for i in range(window, len(vals)):
        sub = vals[i-window:i+1]
        peak = max(sub)
        out.append(sub[-1]/peak - 1)
    return out


def rolling_vol(rets, window=12):
    out = []
    for i in range(window, len(rets)):
        sub = rets[i-window:i]
        out.append(statistics.stdev(sub) * (12**0.5) if len(sub) > 1 else 0)
    return out


# 用 INDPRO (工业产出) 作为主指标 (最长历史)
# 然后 M2/CPI/UNRATE 作为辅助

# 重要历史危机
CRISES = [
    ("1920-01-01", "1920 战后衰退"),
    ("1929-08-01", "1929 大萧条"),
    ("1937-05-01", "1937 二萧"),
    ("1945-08-01", "1945 二战结束"),
    ("1948-11-01", "1948 战后衰退"),
    ("1953-07-01", "1953 朝鲜战争衰退"),
    ("1957-08-01", "1957 衰退"),
    ("1960-04-01", "1960 衰退"),
    ("1970-01-01", "1970 滞胀"),
    ("1973-11-01", "1973 石油危机"),
    ("1980-01-01", "1980 沃克尔紧缩"),
    ("1981-07-01", "1981 衰退"),
    ("1990-07-01", "1990 海湾战争"),
    ("2001-03-01", "2001 互联网"),
    ("2007-12-01", "2007 大衰退"),
    ("2020-03-01", "2020 COVID"),
]


def compute_psi_macro(series_id, window=12):
    """宏观 PSI"""
    d = raw[series_id]["data"]
    d.sort(key=lambda x: x[0])
    dates = [x[0] for x in d]
    vals = [x[1] for x in d]
    rets = returns(vals)
    mmp = rolling_max_dd(vals, window)
    sfd = rolling_vol(rets, window)
    L = min(len(mmp), len(sfd))
    mmp = mmp[-L:]
    sfd = sfd[-L:]
    mmp_mu, mmp_sd = statistics.mean(mmp), statistics.stdev(mmp)
    sfd_mu, sfd_sd = statistics.mean(sfd), statistics.stdev(sfd)
    mmp_z = [(x-mmp_mu)/mmp_sd for x in mmp]
    sfd_z = [(x-sfd_mu)/sfd_sd for x in sfd]
    psi = [0.5*m + 0.5*s for m, s in zip(mmp_z, sfd_z)]  # 简版 2 维度
    offset = len(dates) - L
    return {"dates": dates[offset:], "psi": psi, "vals": vals[offset:]}


def main():
    results = {}
    for sid in raw.keys():
        print(f"[{sid}] {raw[sid]['name']}", end=" ")
        r = compute_psi_macro(sid)
        results[sid] = {
            "name": raw[sid]["name"],
            "dates": r["dates"],
            "psi": r["psi"],
        }
        # 简单回看 6/12 月均值
        n = len(r["psi"])
        n_neg = sum(1 for p in r["psi"] if p < -0.5)
        print(f"| n={n:4d}, n_neg<-0.5={n_neg:3d}, psi_min={min(r['psi']):.2f}, psi_max={max(r['psi']):.2f}")

    # 检验: 危机日 ± 6 个月内 PSI < -0.5 比例
    print("\n" + "=" * 80)
    print("【宏观 PSI 危机预警】")
    print("=" * 80)
    summary = {}
    for sid, r in results.items():
        date_to_psi = dict(zip(r["dates"], r["psi"]))
        n_total = len(r["psi"])
        n_crises = 0
        n_predicted = 0
        leads = []
        for crisis_date, crisis_name in CRISES:
            # 找 ± 6 月窗口
            crisis_year = int(crisis_date[:4])
            crisis_month = int(crisis_date[5:7]) if len(crisis_date) >= 7 else 1
            in_range = False
            for d in date_to_psi:
                dy = int(d[:4])
                dm = int(d[5:7])
                if abs((dy - crisis_year)*12 + (dm - crisis_month)) <= 6:
                    in_range = True
                    break
            if not in_range:
                continue
            n_crises += 1
            # 看危机前 12 月内 PSI<-0.5
            pre_window = []
            for d, p in date_to_psi.items():
                dy = int(d[:4])
                dm = int(d[5:7])
                diff = (crisis_year - dy)*12 + (crisis_month - dm)
                if 0 <= diff <= 12:
                    pre_window.append((d, p))
            if any(p < -0.5 for d, p in pre_window):
                n_predicted += 1
                # lead
                sig = next((d for d, p in pre_window if p < -0.5), None)
                if sig:
                    sy = int(sig[:4]); sm = int(sig[5:7])
                    lead = (crisis_year - sy)*12 + (crisis_month - sm)
                    leads.append(lead)
        recall = n_predicted/n_crises if n_crises else 0
        avg_lead = statistics.mean(leads) if leads else 0
        summary[sid] = {"n_crises": n_crises, "n_predicted": n_predicted, "recall": recall, "avg_lead_months": avg_lead}
        print(f"  [{sid:13s}] {r['name']:20s} | 危机 {n_crises:2d} | 预测 {n_predicted:2d} | 召回 {recall:5.0%} | 平均 Lead {avg_lead:5.1f} 月")

    # 保存
    with open(DATA / "macro_psi_v5.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "n_indicators": len(results)}, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {DATA}/macro_psi_v5.json")

    total_crises = sum(s["n_crises"] for s in summary.values())
    total_pred = sum(s["n_predicted"] for s in summary.values())
    print(f"\n【总召回】 {total_pred}/{total_crises} = {total_pred/total_crises:.1%}")


if __name__ == "__main__":
    main()
