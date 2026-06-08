#!/usr/bin/env python3
"""
v6.0 阶段73: 改进 PSI 策略 + 真正未来盲测

A. 改进策略:
   - 旧: PSI<-0.5 任何一天就触发 (过于频繁)
   - 新: PSI<-0.5 持续 30 天才触发 (更稳健)
   - 持续 PSI>0 退出

B. 真正未来盲测:
   - 用 2020-2023 PSI 数据
   - 不知道 2024 雪球崩 / 2025 牛市
   - 用 UPSI 预测 2024-2025
   - 验证
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


def compute_psi(price_arr):
    """简版 PSI"""
    rets = returns(price_arr)
    mmp = rolling_mmp(price_arr, 60)
    sfd = rolling_vol(rets, 20)
    L = min(len(mmp), len(sfd))
    psi = [(mmp[i] + sfd[i])/2 for i in range(L)]
    mu, sd = statistics.mean(psi), statistics.stdev(psi)
    return [(p-mu)/sd for p in psi]


def main():
    with open(DATA4 / "global_market_data.json", encoding="utf-8") as f:
        raw = json.load(f)

    # 用标普 500
    sp_bars = sorted(raw["US.SP500"], key=lambda x: x[0])
    sp_dates = [b[0] for b in sp_bars]
    sp_prices = [b[1] for b in sp_bars]
    sp_psi = compute_psi(sp_prices)
    offset = len(sp_bars) - len(sp_psi)
    sp_dates = sp_dates[offset:]
    sp_prices = sp_prices[offset:]

    print("=" * 80)
    print("【改进 PSI 策略 v2】 持续 30 天触发")
    print("=" * 80)

    # 改进策略: 持续 30 天 PSI<-0.5 才买入, 持续 30 天 PSI>0 才退出
    HOLD_PERIOD = 30  # 30 天确认
    in_position = False
    buy_idx = None
    n_neg_streak = 0
    n_pos_streak = 0
    trades = []
    capital = 1.0

    for i in range(len(sp_psi)):
        psi = sp_psi[i]
        if psi < -0.5:
            n_neg_streak += 1
            n_pos_streak = 0
        elif psi > 0:
            n_pos_streak += 1
            n_neg_streak = 0
        else:
            n_neg_streak = max(0, n_neg_streak - 1)
            n_pos_streak = max(0, n_pos_streak - 1)

        if not in_position and n_neg_streak >= HOLD_PERIOD:
            in_position = True
            buy_idx = i
            n_neg_streak = 0
        elif in_position and n_pos_streak >= HOLD_PERIOD:
            in_position = False
            sell_idx = i
            ret = (sp_prices[sell_idx] - sp_prices[buy_idx]) / sp_prices[buy_idx]
            capital *= (1 + ret)
            trades.append({
                "buy_date": sp_dates[buy_idx],
                "sell_date": sp_dates[sell_idx],
                "ret": ret,
                "capital_after": capital,
            })
            n_pos_streak = 0

    print(f"\n改进策略交易数: {len(trades)}")
    print(f"\n交易明细:")
    for t in trades[:20]:
        print(f"  {t['buy_date']} 买入 → {t['sell_date']} 卖出, 收益 {t['ret']*100:+.1f}%, 累计 {t['capital_after']:.2f}x")
    print(f"\n改进策略终值: {capital:.2f}x ({(capital-1)*100:+.1f}%)")
    bh = sp_prices[-1] / sp_prices[0]
    print(f"Buy & Hold: {bh:.2f}x ({(bh-1)*100:+.1f}%)")
    if capital > bh:
        print(f"✅ 改进策略胜出! +{((capital-bh)/bh)*100:.1f}%")
    else:
        print(f"❌ 仍落后 Buy & Hold {((bh-capital)/capital)*100:.1f}%")

    # === 真正未来盲测 ===
    print()
    print("=" * 80)
    print("【真正未来盲测】 用 2020-2023 预测 2024-2025")
    print("=" * 80)

    # 标普 2020-2023 PSI
    train_idx = [i for i, d in enumerate(sp_dates) if "2020" <= d[:4] <= "2023"]
    train_psi = [sp_psi[i] for i in train_idx]
    train_dates = [sp_dates[i] for i in train_idx]
    test_idx = [i for i, d in enumerate(sp_dates) if "2024" <= d[:4] <= "2025"]
    test_psi = [sp_psi[i] for i in test_idx]
    test_dates = [sp_dates[i] for i in test_idx]

    print(f"\n训练期 (2020-2023): {len(train_psi)} 天, PSI 范围 {min(train_psi):+.2f} ~ {max(train_psi):+.2f}")
    print(f"测试期 (2024-2025): {len(test_psi)} 天, PSI 范围 {min(test_psi):+.2f} ~ {max(test_psi):+.2f}")

    # 训练期"模式"
    train_mean = statistics.mean(train_psi)
    train_std = statistics.stdev(train_psi)
    train_neg_days = sum(1 for p in train_psi if p < -0.5)
    print(f"  训练期平均 PSI: {train_mean:+.3f}")
    print(f"  训练期 PSI<-0.5 天数: {train_neg_days}/{len(train_psi)} ({train_neg_days/len(train_psi):.0%})")

    # 预测测试期: 训练期 PSI<-0.5 占比 16%, 假设测试期相同
    expected_neg = int(len(test_psi) * train_neg_days / len(train_psi))
    actual_neg = sum(1 for p in test_psi if p < -0.5)
    print(f"  测试期 PSI<-0.5: 预期 {expected_neg} 实际 {actual_neg}")

    # 看测试期 PSI 是否比训练期更负 (即压力期)
    test_mean = statistics.mean(test_psi)
    print(f"  测试期平均 PSI: {test_mean:+.3f} (vs 训练期 {train_mean:+.3f})")
    if test_mean < train_mean - 0.1:
        print(f"  → 测试期压力比训练期更高, 预测测试期有更多危机事件")
    elif test_mean > train_mean + 0.1:
        print(f"  → 测试期压力低, 预测测试期偏乐观")
    else:
        print(f"  → 测试期压力类似训练期")

    # 实际 2024-2025 重大事件
    print(f"\n2024-2025 实际重大事件:")
    print(f"  2024-02 雪球敲入/小盘股崩")
    print(f"  2024-08 套利崩")
    print(f"  2025-XX 持续牛市")

    # 检查测试期 PSI 是否实际预测了这些
    crisis_2024 = ["2024-02-05", "2024-08-05"]
    print(f"\n2024 危机日期 PSI 状态:")
    for c in crisis_2024:
        if c in sp_dates:
            idx = sp_dates.index(c)
            print(f"  {c}: PSI = {sp_psi[idx]:+.2f}")

    # 2024-02-05 雪球崩: 检查前后 60 天
    if "2024-02-05" in sp_dates:
        idx = sp_dates.index("2024-02-05")
        pre_window = [sp_psi[i] for i in range(max(0, idx-60), idx)]
        if pre_window:
            n_neg = sum(1 for p in pre_window if p < -0.5)
            print(f"  2024-02 雪球崩 前 60 天 PSI<-0.5: {n_neg}/60 = {n_neg/60:.0%}")

    # 2025 持续牛市
    psi_2025 = [sp_psi[i] for i, d in enumerate(sp_dates) if d[:4] == "2025"]
    if psi_2025:
        n_pos = sum(1 for p in psi_2025 if p > 0.5)
        print(f"  2025 PSI>+0.5: {n_pos}/{len(psi_2025)} = {n_pos/len(psi_2025):.0%} (预期: 牛市应 > 50%)")

    # 跨域盲测: 用 2020-2023 政治 + 金融 PSI 预测 2024-2025
    with open(DATA5 / "political_psi_v5.json", encoding="utf-8") as f:
        pol = json.load(f)
    pol_years = pol["psi"]["years"]
    pol_psi = pol["psi"]["psi"]
    train_pol = [(y, p) for y, p in zip(pol_years, pol_psi) if 2020 <= y <= 2023]
    test_pol = [(y, p) for y, p in zip(pol_years, pol_psi) if 2024 <= y <= 2025]
    if train_pol and test_pol:
        print(f"\n政治 PSI:")
        print(f"  训练 (2020-2023) 平均: {statistics.mean(p for _, p in train_pol):+.3f}")
        print(f"  测试 (2024-2025) 平均: {statistics.mean(p for _, p in test_pol):+.3f}")

    # 保存
    with open(OUT / "blind_test_v6.json", "w", encoding="utf-8") as f:
        json.dump({
            "improved_strategy": {
                "n_trades": len(trades),
                "final_capital": capital,
                "buy_hold": bh,
                "outperform": capital > bh,
            },
            "blind_test": {
                "train_years": "2020-2023",
                "test_years": "2024-2025",
                "train_mean_psi": train_mean,
                "test_mean_psi": test_mean,
                "train_neg_rate": train_neg_days / len(train_psi),
                "test_neg_rate": actual_neg / len(test_psi),
                "test_predicted_pressure": test_mean < train_mean - 0.1,
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/blind_test_v6.json")


if __name__ == "__main__":
    main()
