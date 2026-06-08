#!/usr/bin/env python3
"""
v6.1 阶段83 (P0 阻塞): H-β 重新验证

升级方案 CZ-1 警示: H=0.958, β=1.66 不符合标准分形理论
- fBm 预测 β = 2H+1 = 2.916
- fGn 预测 β = 2H-1 = 0.916
- 我们的 1.66 不匹配任何已知过程

要验证:
1. R/S 方法 vs DFA (去趋势波动分析) - 用两种方法算 H
2. FFT vs Whittle - 用两种方法算 β
3. 用 fBm, fGn, Levy-stable 拟合
4. 看是不是新普适类

如果 H 和 β 一致 → 新普适类
如果不一致 → 可能有 bug
"""
import json
import statistics
import math
from pathlib import Path

DATA4 = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v6.1/data")
OUT.mkdir(parents=True, exist_ok=True)


def returns(p): return [p[i]/p[i-1] - 1 for i in range(1, len(p))]


def hurst_rs(series, max_lag=None):
    """R/S 方法 - 估计 Hurst H"""
    n = len(series)
    if max_lag is None:
        max_lag = n // 4
    rs_values = []
    lags = []
    for lag in range(10, max_lag, 5):
        n_sub = n // lag
        if n_sub < 2:
            continue
        r_vals = []
        for i in range(n_sub):
            sub = series[i*lag:(i+1)*lag]
            if len(sub) < 2:
                continue
            mean = sum(sub) / len(sub)
            devs = [x - mean for x in sub]
            cum = [sum(devs[:j+1]) for j in range(len(devs))]
            r = max(cum) - min(cum)
            s = statistics.stdev(sub) if len(sub) > 1 else 0
            if s > 0:
                r_vals.append(r / s)
        if r_vals:
            rs_values.append(statistics.mean(r_vals))
            lags.append(lag)
    if len(rs_values) < 3:
        return None
    log_lags = [math.log(l) for l in lags]
    log_rs = [math.log(r) for r in rs_values]
    n_pts = len(log_lags)
    mx = sum(log_lags) / n_pts
    my = sum(log_rs) / n_pts
    num = sum((log_lags[i] - mx) * (log_rs[i] - my) for i in range(n_pts))
    den = sum((log_lags[i] - mx) ** 2 for i in range(n_pts))
    return num / den if den > 0 else 0.5


def hurst_dfa(series, max_lag=None):
    """DFA (Detrended Fluctuation Analysis) - 估计 Hurst H
    这是更稳健的 H 估计方法"""
    n = len(series)
    if max_lag is None:
        max_lag = n // 4
    # 计算累积和
    mean = sum(series) / n
    y = [series[i] - mean for i in range(n)]
    cum_y = [sum(y[:i+1]) for i in range(n)]

    fluct = []
    lags = []
    for lag in range(10, max_lag, 5):
        n_sub = n // lag
        if n_sub < 2:
            continue
        f_vals = []
        for i in range(n_sub):
            sub = cum_y[i*lag:(i+1)*lag]
            # 局部趋势 (线性)
            x = list(range(len(sub)))
            n_pts = len(x)
            sx = sum(x)
            sy = sum(sub)
            sxx = sum(xi*xi for xi in x)
            sxy = sum(x[i]*sub[i] for i in range(n_pts))
            denom = n_pts * sxx - sx * sx
            if denom == 0:
                continue
            b = (n_pts * sxy - sx * sy) / denom
            a = (sy - b * sx) / n_pts
            # 残差
            trend = [a + b * x[i] for i in range(n_pts)]
            res = [sub[i] - trend[i] for i in range(n_pts)]
            f = (sum(r*r for r in res) / n_pts) ** 0.5
            f_vals.append(f)
        if f_vals:
            fluct.append(statistics.mean(f_vals))
            lags.append(lag)
    if len(fluct) < 3:
        return None
    log_lags = [math.log(l) for l in lags]
    log_f = [math.log(f) for f in fluct]
    n_pts = len(log_lags)
    mx = sum(log_lags) / n_pts
    my = sum(log_f) / n_pts
    num = sum((log_lags[i] - mx) * (log_f[i] - my) for i in range(n_pts))
    den = sum((log_lags[i] - mx) ** 2 for i in range(n_pts))
    return num / den if den > 0 else 0.5


def power_spectrum_fft(series):
    """FFT 方法 - 估计功率谱指数 β"""
    n = len(series)
    if n < 100:
        return None
    # 去均值
    mean = sum(series) / n
    series = [s - mean for s in series]
    import numpy.fft as fft
    fft_vals = fft.rfft(series)
    psd = [abs(v)**2 for v in fft_vals]
    freqs = fft.rfftfreq(n)
    valid = [(f, s) for f, s in zip(freqs, psd) if f > 0 and s > 0]
    if len(valid) < 10:
        return None
    log_f = [math.log(f) for f, s in valid]
    log_s = [math.log(s) for f, s in valid]
    n_v = len(log_f)
    mx = sum(log_f) / n_v
    my = sum(log_s) / n_v
    num = sum((log_f[i] - mx) * (log_s[i] - my) for i in range(n_v))
    den = sum((log_f[i] - mx) ** 2 for i in range(n_v))
    return -num / den if den > 0 else 0


def whittle_estimator(series):
    """Whittle 似然估计 - 更稳健的 β 估计
    优化 Whittle 似然: 假设 1/f^β 谱, 找最优 β"""
    n = len(series)
    if n < 100:
        return None
    mean = sum(series) / n
    series = [s - mean for s in series]
    import numpy.fft as fft
    fft_vals = fft.rfft(series)
    psd = [abs(v)**2 for v in fft_vals]
    freqs = fft.rfftfreq(n)
    # Whittle 似然 (简化)
    # 找 β 让 sum log(f^β) + sum psd / f^β 最小
    best_beta = 0
    best_ll = float('inf')
    for beta in [x/10 for x in range(-20, 41)]:
        ll = 0
        for i, f in enumerate(freqs[1:], 1):
            if f > 0 and psd[i] > 0:
                expected = f ** (-beta)
                ll += math.log(expected) + psd[i] / expected
        if ll < best_ll:
            best_ll = ll
            best_beta = beta
    return best_beta


def main():
    # 加载标普 500 价格
    with open(DATA4 / "global_market_data.json", encoding="utf-8") as f:
        raw = json.load(f)
    sp_bars = sorted(raw["US.SP500"], key=lambda x: x[0])
    sp_prices = [b[1] for b in sp_bars]
    sp_returns = returns(sp_prices)

    # 下采样到 2000 个点加速计算
    if len(sp_prices) > 3000:
        sp_prices = sp_prices[-3000:]
        sp_returns = returns(sp_prices)

    print("=" * 80)
    print("【H-β 重新验证】 v6.1 阶段 83 (P0 阻塞)")
    print("=" * 80)
    print(f"\n数据: 标普 500, {len(sp_prices)} 个价格, {len(sp_returns)} 个收益率")
    print(f"时间: {sp_bars[0][0]} ~ {sp_bars[-1][0]}")

    # === 1. 估计 Hurst H (4 种方法) ===
    print(f"\n" + "=" * 80)
    print(f"【Hurst H 估计】 4 种方法对比")
    print(f"=" * 80)

    # 价格水平 (level)
    H_level_RS = hurst_rs(sp_prices)
    H_level_DFA = hurst_dfa(sp_prices)
    # 收益率 (increments)
    H_ret_RS = hurst_rs(sp_returns)
    H_ret_DFA = hurst_dfa(sp_returns)

    print(f"  价格水平 (level):")
    print(f"    R/S 方法:   H = {H_level_RS:.4f}")
    print(f"    DFA 方法:   H = {H_level_DFA:.4f}")
    print(f"  收益率 (increments):")
    print(f"    R/S 方法:   H = {H_ret_RS:.4f}")
    print(f"    DFA 方法:   H = {H_ret_DFA:.4f}")

    # === 2. 估计功率谱 β (2 种方法) ===
    print(f"\n" + "=" * 80)
    print(f"【功率谱 β 估计】 2 种方法对比")
    print(f"=" * 80)
    beta_fft = power_spectrum_fft(sp_prices)
    beta_whittle = whittle_estimator(sp_prices)
    beta_fft_ret = power_spectrum_fft(sp_returns)
    beta_whittle_ret = whittle_estimator(sp_returns)

    print(f"  价格水平 (level):")
    print(f"    FFT:        β = {beta_fft:.4f}")
    print(f"    Whittle:    β = {beta_whittle:.4f}")
    print(f"  收益率 (increments):")
    print(f"    FFT:        β = {beta_fft_ret:.4f}")
    print(f"    Whittle:    β = {beta_whittle_ret:.4f}")

    # === 3. 一致性检验 ===
    print(f"\n" + "=" * 80)
    print(f"【H-β 一致性检验】")
    print(f"=" * 80)
    # 用 DFA (H_level) 和 Whittle (β) 作标准
    H = H_level_DFA
    beta = beta_whittle

    print(f"  使用 H (DFA on level) = {H:.4f}")
    print(f"  使用 β (Whittle on level) = {beta:.4f}")

    fbm_pred = 2 * H + 1
    fgn_pred = 2 * H - 1
    print(f"\n  理论预测 (fBm): β = 2H+1 = {fbm_pred:.4f}")
    print(f"  理论预测 (fGn): β = 2H-1 = {fgn_pred:.4f}")
    print(f"  实测 (Whittle):     β = {beta:.4f}")

    fbm_dev = abs(beta - fbm_pred) / fbm_pred * 100 if fbm_pred > 0 else 0
    fgn_dev = abs(beta - fgn_pred) / fgn_pred * 100 if fgn_pred > 0 else 0
    print(f"  偏差 vs fBm: {fbm_dev:.1f}%")
    print(f"  偏差 vs fGn: {fgn_dev:.1f}%")

    # 推算 H
    H_from_fbm = (beta - 1) / 2
    H_from_fgn = (beta + 1) / 2
    print(f"\n  反推 H from fBm: H = {H_from_fbm:.4f}")
    print(f"  反推 H from fGn: H = {H_from_fgn:.4f}")
    print(f"  实测 H: H = {H:.4f}")

    # === 4. 结论 ===
    print(f"\n" + "=" * 80)
    print(f"【结论】")
    print(f"=" * 80)

    consistent = abs(fbm_dev) < 10 or abs(fgn_dev) < 10
    if consistent:
        print("  ✓ H-β 一致! 符合标准分形过程")
    else:
        print("  ✗ H-β 不一致! 升级方案 CZ-1 警示确实存在")
        # 检查可能的非标准过程
        # Levy-stable: β = αH + 1
        alpha = (beta - 1) / H if H > 0 else 0
        print(f"  Levy-stable 拟合: α = {alpha:.4f}")
        if 0 < alpha <= 2:
            print(f"    → α 在 Levy-stable 有效范围 (0, 2] 内")

        # 检查多重分形
        # 关系: H_lev 和 H_inc 差异显著 → 多重分形
        if H_level_DFA and H_ret_DFA:
            delta = abs(H_level_DFA - H_ret_DFA)
            print(f"  H_lev - H_inc = {delta:.4f} (理论 fBm 应=1.0)")

    # 保存
    with open(OUT / "h_beta_recheck_v61.json", "w", encoding="utf-8") as f:
        json.dump({
            "H_estimates": {
                "level_RS": H_level_RS,
                "level_DFA": H_level_DFA,
                "ret_RS": H_ret_RS,
                "ret_DFA": H_ret_DFA,
            },
            "beta_estimates": {
                "level_FFT": beta_fft,
                "level_Whittle": beta_whittle,
                "ret_FFT": beta_fft_ret,
                "ret_Whittle": beta_whittle_ret,
            },
            "consistency": {
                "fbm_pred": fbm_pred,
                "fgn_pred": fgn_pred,
                "fbm_dev_pct": fbm_dev,
                "fgn_dev_pct": fgn_dev,
                "consistent": consistent,
                "levy_alpha": (beta - 1) / H if H > 0 else None,
            },
            "conclusion": "C1 警示确认" if not consistent else "H-β 一致",
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/h_beta_recheck_v61.json")


if __name__ == "__main__":
    main()
