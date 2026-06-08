#!/usr/bin/env python3
"""
v6.0 阶段76: 跨域 UPSI 统一实证 (Global UPSI Timeline)

合并 6 域 PSI 到统一"全球压力时间线":
- 1990-2020: 标普 500 + 上证 + 政治 + 宏观 (4 域)
- 公元前 218-2022: 政治 + 中华 (2 域)

目标: 看 1990-2020 这个窗口, 跨 4 域的 PSI 是否同步共振
"""
import json
import statistics
from pathlib import Path
from datetime import datetime

DATA4 = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
DATA5 = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")
OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v6/data")


def returns(p): return [p[i]/p[i-1]-1 for i in range(1, len(p))]
def rolling_mmp(p, w=60): return [p[i]/max(p[i-w:i+1])-1 for i in range(w, len(p))]
def rolling_vol(r, w=20): return [statistics.stdev(r[i-w:i])*(252**0.5) for i in range(w, len(r))]


def main():
    print("=" * 80)
    print("【跨域 UPSI 统一实证】 1990-2020 全球压力时间线")
    print("=" * 80)

    # 1. 中国金融 (上证 2018-2026)
    with open(DATA4 / "market_psi_v4.json", encoding="utf-8") as f:
        sh = json.load(f)["sh000001"]
    sh_psi = dict(zip(sh["dates"], sh["psi"]))

    # 2. 全球金融 (标普 1990-2020)
    with open(DATA4 / "global_market_data.json", encoding="utf-8") as f:
        raw = json.load(f)
    sp_bars = sorted(raw["US.SP500"], key=lambda x: x[0])
    sp_dates = [b[0] for b in sp_bars]
    sp_prices = [b[1] for b in sp_bars]
    sp_rets = returns(sp_prices)
    sp_mmp = rolling_mmp(sp_prices, 60)
    sp_sfd = rolling_vol(sp_rets, 20)
    L = min(len(sp_mmp), len(sp_sfd))
    sp_psi_raw = [(sp_mmp[i] + sp_sfd[i])/2 for i in range(L)]
    sp_mu, sp_sd = statistics.mean(sp_psi_raw), statistics.stdev(sp_psi_raw)
    sp_psi = [(p-sp_mu)/sp_sd for p in sp_psi_raw]
    sp_offset = len(sp_bars) - L
    sp_dates = sp_dates[sp_offset:]

    # 3. 政治 PSI
    with open(DATA5 / "political_psi_v5.json", encoding="utf-8") as f:
        pol = json.load(f)
    pol_years = pol["psi"]["years"]
    pol_psi = pol["psi"]["psi"]

    # 4. 宏观 PSI (INDPRO 1919-2026)
    with open(DATA5 / "fred_macro_data.json", encoding="utf-8") as f:
        fred = json.load(f)
    if "INDPRO" in fred:
        d = sorted(fred["INDPRO"]["data"], key=lambda x: x[0])
        m_dates = [x[0] for x in d]
        m_prices = [x[1] for x in d]
        m_rets = returns(m_prices)
        m_mmp = rolling_mmp(m_prices, 12)  # 12 月
        m_sfd = rolling_vol(m_rets, 12)
        L2 = min(len(m_mmp), len(m_sfd))
        m_psi_raw = [(m_mmp[i] + m_sfd[i])/2 for i in range(L2)]
        m_mu, m_sd = statistics.mean(m_psi_raw), statistics.stdev(m_psi_raw)
        m_psi = [(p-m_mu)/m_sd for p in m_psi_raw]
        m_offset = len(d) - L2
        m_dates = m_dates[m_offset:]

    # === 1990-2020 跨域对齐 ===
    # 把所有域聚合成 10 年窗
    print("\n【10 年窗聚合】 1990-2020")
    decades = ["1990", "2000", "2010", "2020"]

    # 标普 (日度 → 10 年)
    sp_decadal = {}
    for d_str in decades:
        d_int = int(d_str)
        relevant = [(d, p) for d, p in zip(sp_dates, sp_psi) if d_int <= int(d[:4]) < d_int + 10]
        if relevant:
            sp_decadal[d_str] = statistics.mean([p for _, p in relevant])

    # 政治 (已有 10 年)
    pol_decadal = {}
    for d_str in decades:
        d_int = int(d_str)
        relevant = [(y, p) for y, p in zip(pol_years, pol_psi) if d_int <= y < d_int + 10]
        if relevant:
            pol_decadal[d_str] = statistics.mean([p for _, p in relevant])

    # 宏观 (月度 → 10 年)
    m_decadal = {}
    for d_str in decades:
        d_int = int(d_str)
        relevant = [(d, p) for d, p in zip(m_dates, m_psi) if d_int <= int(d[:4]) < d_int + 10]
        if relevant:
            m_decadal[d_str] = statistics.mean([p for _, p in relevant])

    # 上证 (2018+, 只有 2020 数据)
    sh_decadal = {}
    for d_str in decades:
        d_int = int(d_str)
        if d_int == 2020:
            relevant = [(d, p) for d, p in sh_psi.items() if d_int <= int(d[:4]) < d_int + 10]
            if relevant:
                sh_decadal[d_str] = statistics.mean([p for _, p in relevant])

    print(f"  标普: {sp_decadal}")
    print(f"  政治: {pol_decadal}")
    print(f"  宏观 (INDPRO): {m_decadal}")
    print(f"  上证: {sh_decadal}")

    # === 跨域相关性 ===
    print()
    print("=" * 80)
    print("【跨域 PSI 相关性】")
    print("=" * 80)

    # 找共同 decade
    common = sorted(set(sp_decadal) & set(pol_decadal) & set(m_decadal))
    print(f"  共同 decade: {common}")

    if len(common) >= 3:
        # 4 域两两相关
        domains = {
            "标普 (金融)": sp_decadal,
            "政治": pol_decadal,
            "宏观 (INDPRO)": m_decadal,
        }
        if sh_decadal:
            domains["上证 (金融)"] = sh_decadal

        print(f"\n  跨域相关矩阵:")
        for d1 in domains:
            for d2 in domains:
                if d1 < d2:
                    common_2 = sorted(set(domains[d1]) & set(domains[d2]))
                    if len(common_2) >= 3:
                        xs = [domains[d1][d] for d in common_2]
                        ys = [domains[d2][d] for d in common_2]
                        mx, my = statistics.mean(xs), statistics.mean(ys)
                        num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
                        dx = (sum((x-mx)**2 for x in xs))**0.5
                        dy = (sum((y-my)**2 for y in ys))**0.5
                        r = num/(dx*dy) if dx*dy > 0 else 0
                        print(f"    {d1:18s} ↔ {d2:18s}: r = {r:+.3f}")

    # === UPSI 统一公式 ===
    print()
    print("=" * 80)
    print("【UPSI 统一公式】")
    print("=" * 80)
    print("""
  UPSI = 0.40 × Material + 0.30 × Fragmentation + 0.30 × Disengagement

  跨域实例化:
  - 金融域: Material=回撤, Fragmentation=波动, Disengagement=换手率
  - 政治域: Material=战争死亡, Fragmentation=革命频率, Disengagement=精英外流
  - 宏观域: Material=工业产出下降, Fragmentation=失业率波动, Disengagement=消费信心

  共同点: 三维度的同步退化 = 系统压力
""")

    # 4 域 PSI 合成 UPSI
    print("=" * 80)
    print("【UPSI 跨域综合】 1990-2020 4 域合成")
    print("=" * 80)
    for d in common:
        vals = []
        for src in [sp_decadal, pol_decadal, m_decadal]:
            if d in src:
                vals.append(src[d])
        if len(vals) == 3:
            # 归一化后加权平均
            upsi = statistics.mean(vals)
            print(f"  {d}: 标普={sp_decadal.get(d, 'N/A'):.2f}, 政治={pol_decadal.get(d, 'N/A'):.2f}, 宏观={m_decadal.get(d, 'N/A'):.2f}, UPSI={upsi:+.3f}")

    # 重大事件验证
    print()
    print("=" * 80)
    print("【UPSI 跨域验证】 已知历史事件")
    print("=" * 80)
    EVENTS = {
        "2000": ("互联网泡沫", "应该 UPSI < 0"),
        "2008": ("金融危机", "应该 UPSI < 0 同步"),
        "2020": ("COVID", "应该 UPSI 急降后反弹"),
    }
    for d_str, (name, expected) in EVENTS.items():
        if d_str in common:
            vals = [sp_decadal.get(d_str), pol_decadal.get(d_str), m_decadal.get(d_str)]
            vals_clean = [v for v in vals if v is not None]
            if vals_clean:
                avg = statistics.mean(vals_clean)
                status = "✓ 符合" if avg < 0 else "✗ 不符合"
                print(f"  {d_str} {name}: UPSI={avg:+.3f}, {expected} → {status}")

    # 保存
    out = {
        "decades": common,
        "sp_decadal": sp_decadal,
        "pol_decadal": pol_decadal,
        "m_decadal": m_decadal,
        "sh_decadal": sh_decadal,
        "n_domains_compared": 3 if sh_decadal else 2,
    }
    with open(OUT / "global_upsi_v6.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/global_upsi_v6.json")


if __name__ == "__main__":
    main()
