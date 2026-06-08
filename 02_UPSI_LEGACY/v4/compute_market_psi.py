#!/usr/bin/env python3
"""
阶段 36: 金融 PSI_z 验证

PSI 三维度的金融映射:
- MMP (Macro-Material Pressure)  → 沪深300 60日最大回撤
- SFD (Social Fragmentation)     → 20日 realized volatility
- EED (Elite/Expert Disengagement) → 20日换手率 z-score (聪明钱活跃度)

公式 (与 v4.x 论文一致):
PSI_z = 0.40×MMP_z + 0.30×SFD_z + 0.30×EED_z

其中 z-score 用 252 个交易日滚动窗口标准化 (≈ 1 年)

然后测试 PSI_z < 0 是否领先于已知金融危机的发生日。
"""
import json
import statistics
from pathlib import Path
from datetime import datetime

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")


def parse_data(raw, key):
    """统一解析腾讯/新浪数据为 [(date, close), ...]"""
    arr = raw.get(key, [])
    out = []
    for bar in arr:
        if isinstance(bar, list):  # 腾讯
            date, o, c, h, l, v = bar[:6]
            out.append((date, float(c), float(v)))
        elif isinstance(bar, dict):  # 新浪
            date = bar.get("day")
            c = float(bar.get("close", 0))
            v = float(bar.get("volume", 0))
            out.append((date, c, v))
    return out


def returns(prices):
    """日收益率"""
    return [prices[i] / prices[i-1] - 1 for i in range(1, len(prices))]


def rolling_max_drawdown(prices, window=60):
    """滚动最大回撤 (-max_dd), 取负值 = 压力"""
    out = []
    for i in range(window, len(prices)):
        sub = prices[i-window:i+1]
        peak = max(sub)
        dd = sub[-1] / peak - 1
        out.append(dd)  # 负数表示回撤
    return out


def rolling_vol(returns_arr, window=20):
    """20日年化 realized volatility"""
    out = []
    for i in range(window, len(returns_arr)):
        sub = returns_arr[i-window:i]
        vol = statistics.stdev(sub) * (252 ** 0.5) if len(sub) > 1 else 0
        out.append(vol)
    return out


def rolling_zscore(arr, window=252):
    """滚动 z-score"""
    out = []
    for i in range(window, len(arr)):
        sub = arr[i-window:i]
        mu = statistics.mean(sub)
        sd = statistics.stdev(sub) if len(sub) > 1 else 0
        z = (arr[i] - mu) / sd if sd > 0 else 0
        out.append(z)
    return out


def compute_psi(bars, symbol):
    """计算 PSI 三维度"""
    bars.sort(key=lambda x: x[0])
    dates = [b[0] for b in bars]
    prices = [b[1] for b in bars]
    volumes = [b[2] for b in bars]

    rets = returns(prices)
    mmp_raw = rolling_max_drawdown(prices, window=60)  # 60日回撤 (负值)
    sfd_raw = rolling_vol(rets, window=20)            # 20日 vol

    # 滚动换手率 (volume normalized by 60d mean) - 衡量活跃度
    # 用 volume z-score 简单代理
    eed_raw = []
    for i in range(60, len(volumes)):
        sub = volumes[i-60:i]
        if sub and statistics.mean(sub) > 0:
            eed_raw.append(volumes[i] / statistics.mean(sub) - 1)
        else:
            eed_raw.append(0)
    # EED 越高 = 越活跃 = 越"喧闹"，精英脱节 → 用负号使低活跃 = 危机

    # 取三组长度对齐
    L = min(len(mmp_raw), len(sfd_raw), len(eed_raw))
    mmp = mmp_raw[-L:]
    sfd = sfd_raw[-L:]
    eed = eed_raw[-L:]

    # z-score 标准化 (跨全样本均值)
    mmp_mu, mmp_sd = statistics.mean(mmp), statistics.stdev(mmp)
    sfd_mu, sfd_sd = statistics.mean(sfd), statistics.stdev(sfd)
    eed_mu, eed_sd = statistics.mean(eed), statistics.stdev(eed)

    mmp_z = [(x - mmp_mu) / mmp_sd for x in mmp]
    sfd_z = [(x - sfd_mu) / sfd_sd for x in sfd]
    eed_z = [-(x - eed_mu) / eed_sd for x in eed]  # 负号: 高活跃=正=盛世

    psi = [0.4 * m + 0.3 * s + 0.3 * e for m, s, e in zip(mmp_z, sfd_z, eed_z)]
    # 起始日期对齐
    offset = len(dates) - L
    aligned_dates = dates[offset:]

    return {
        "dates": aligned_dates,
        "prices": prices[offset:],
        "mmp": mmp_z,
        "sfd": sfd_z,
        "eed": eed_z,
        "psi": psi,
    }


def main():
    with open(DATA / "market_raw_data.json", encoding="utf-8") as f:
        raw = json.load(f)

    results = {}
    for key in ["sh000001", "hkHSI", "sz399001_sina", "sh000300_sina"]:
        bars = parse_data(raw, key)
        if not bars:
            print(f"[skip] {key}: no data")
            continue
        # 去重 (腾讯多日同date)
        seen = set()
        uniq = []
        for b in bars:
            if b[0] not in seen:
                uniq.append(b)
                seen.add(b[0])
        print(f"[{key}] {len(uniq)} unique bars, {uniq[0][0]} ~ {uniq[-1][0]}")
        r = compute_psi(uniq, key)
        results[key] = {
            "dates": r["dates"],
            "psi": r["psi"],
            "mmp_z": r["mmp"],
            "sfd_z": r["sfd"],
            "eed_z": r["eed"],
            "prices": r["prices"],
            "n": len(r["psi"]),
            "psi_mean": statistics.mean(r["psi"]),
            "psi_std": statistics.stdev(r["psi"]),
            "psi_min": min(r["psi"]),
            "psi_max": max(r["psi"]),
        }

    # 已知金融危机日期 (中国/全球主要事件)
    known_crises = [
        ("2018-01-29", "2018-01 美股闪崩"),
        ("2018-10-11", "2018-10 美股大跌"),
        ("2019-05-10", "2019-05 贸易战升级"),
        ("2020-01-23", "2020-01-23 武汉封城 (COVID)"),
        ("2020-03-23", "2020-03-23 全球股灾底"),
        ("2022-02-24", "2022-02-24 俄乌战争"),
        ("2022-10-31", "2022-Q4 防疫转折/港股崩"),
        ("2024-02-05", "2024-02 雪球敲入/小盘股崩"),
    ]

    # 检验: 危机前 60 天内 PSI_z < 0 的次数
    from datetime import datetime
    def date_diff(d1, d2):
        try:
            a = datetime.strptime(d1, "%Y-%m-%d")
            b = datetime.strptime(d2, "%Y-%m-%d")
            return (a - b).days
        except:
            return None

    print("\n=== PSI 预测检验 ===")
    for key, r in results.items():
        if not r["psi"]:
            continue
        print(f"\n--- {key} ---")
        print(f"  N={r['n']} days, mean={r['psi_mean']:.3f}, std={r['psi_std']:.3f}, min={r['psi_min']:.2f}, max={r['psi_max']:.2f}")
        # 检查每个已知危机
        for crisis_date, crisis_name in known_crises:
            # 找 crisis_date 在 dates 里的索引
            if crisis_date not in r["dates"]:
                continue
            idx = r["dates"].index(crisis_date)
            # 看前 60 天 PSI 是否 < 0
            window_psi = r["psi"][max(0, idx-60):idx+1]
            if not window_psi:
                continue
            n_neg = sum(1 for x in window_psi if x < 0)
            n_strong_neg = sum(1 for x in window_psi if x < -0.5)
            min_psi_in_window = min(window_psi)
            print(f"  {crisis_date} {crisis_name}: 前60天 PSI<0 占比 {n_neg/len(window_psi):.0%}, 强负 {n_strong_neg/len(window_psi):.0%}, 最低 {min_psi_in_window:.2f}")

    # 跨市场一致性: 在同期 PSI_z 相关性
    if "sh000001" in results and "hkHSI" in results:
        sse = results["sh000001"]
        hsi = results["hkHSI"]
        # 找共同日期
        sse_map = dict(zip(sse["dates"], sse["psi"]))
        hsi_map = dict(zip(hsi["dates"], hsi["psi"]))
        common = sorted(set(sse_map) & set(hsi_map))
        if common:
            xs = [sse_map[d] for d in common]
            ys = [hsi_map[d] for d in common]
            # Pearson 相关
            n = len(common)
            mx, my = statistics.mean(xs), statistics.mean(ys)
            num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
            dx = (sum((x-mx)**2 for x in xs))**0.5
            dy = (sum((y-my)**2 for y in ys))**0.5
            r = num / (dx * dy) if dx*dy > 0 else 0
            print(f"\n=== 跨市场相关性 ===")
            print(f"  上证 vs 恒生 PSI Pearson r = {r:.3f} (N={n} 天)")

    # 保存
    with open(DATA / "market_psi_v4.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False)
    print(f"\n✅ 保存到 {DATA}/market_psi_v4.json")

    return results


if __name__ == "__main__":
    main()
