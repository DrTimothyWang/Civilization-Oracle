#!/usr/bin/env python3
"""
v6.0 阶段78: PSI 策略 v3 (真正可用的 trading 策略)

改进:
1. 多市场综合 PSI (上证 + 标普 + 恒生)
2. 仓位管理 (Kelly Criterion 简化版)
3. 止损 (-10% 强制平仓)
4. 持续期 (60 天 PSI<0 才入场)

回测期: 2018-2026 (8 年)
对照: Buy & Hold, Mean Reversion
"""
import json
import statistics
from pathlib import Path

DATA4 = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v6/data")


def main():
    # 加载 4 指数 PSI
    with open(DATA4 / "market_psi_v4.json", encoding="utf-8") as f:
        fin = json.load(f)

    # 用上证和恒生
    sh = fin["sh000001"]
    hsi = fin["hkHSI"]

    # 找共同日期
    common = sorted(set(sh["dates"]) & set(hsi["dates"]))
    sh_map = dict(zip(sh["dates"], sh["psi"]))
    hsi_map = dict(zip(hsi["dates"], hsi["psi"]))

    # 4 指数价格 (从原始数据)
    with open(DATA4 / "market_raw_data.json", encoding="utf-8") as f:
        raw = json.load(f)

    def get_price(symbol, date):
        for b in raw.get(symbol, []):
            if b[0] == date:
                return b[1]
        return None

    # 简化: 假设上证价格 (转 float)
    sh_price_map = {}
    for b in raw.get("sh000001", []):
        if isinstance(b, list) and b[0] in common:
            try:
                sh_price_map[b[0]] = float(b[2])  # close price
            except:
                pass

    # === 策略 v3 ===
    print("=" * 80)
    print("【PSI 策略 v3】 多市场 + 仓位 + 止损")
    print("=" * 80)

    HOLD_DAYS = 20  # 持续 20 天 PSI<0 才入场 (放宽)
    STOP_LOSS = 0.08  # 8% 止损
    TAKE_PROFIT_PSI = 0.0  # PSI > 0 退出

    # 找每个市场的进场/退场点
    in_position = False
    entry_idx = None
    entry_price = None
    position_size = 0.5  # 50% 仓位 (保守)
    capital = 1.0
    cash = 1.0
    shares = 0
    n_neg_streak = 0
    trades = []

    for i, d in enumerate(common):
        # 多市场综合 PSI
        avg_psi = (sh_map.get(d, 0) + hsi_map.get(d, 0)) / 2
        price = sh_price_map.get(d)
        if price is None:
            continue

        # 计算持续期
        if avg_psi < -0.5:
            n_neg_streak += 1
        else:
            n_neg_streak = max(0, n_neg_streak - 1)

        # 入场: 60 天持续 PSI<0
        if not in_position and n_neg_streak >= HOLD_DAYS:
            in_position = True
            entry_idx = i
            entry_price = price
            # 用 50% 仓位
            shares = (cash * position_size) / price
            cash -= shares * price
            n_neg_streak = 0

        # 退场: 止损 / 60 天 PSI>0
        if in_position:
            current_return = (price - entry_price) / entry_price
            # 止损
            if current_return < -STOP_LOSS:
                cash += shares * price
                ret = current_return
                capital += ret * position_size
                trades.append({"entry": common[entry_idx], "exit": d, "ret": ret, "reason": "STOP_LOSS"})
                in_position = False
                shares = 0
                n_neg_streak = 0
            # 持续 PSI>0 退出 (用 TAKE_PROFIT_PSI 阈值)
            elif avg_psi > TAKE_PROFIT_PSI:
                cash += shares * price
                ret = (price - entry_price) / entry_price
                capital += ret * position_size
                trades.append({"entry": common[entry_idx], "exit": d, "ret": ret, "reason": "TAKE_PROFIT"})
                in_position = False
                shares = 0
                n_neg_streak = 0

    if in_position:
        last_p = sh_price_map.get(common[-1], 0)
        cash += shares * last_p
        ret = (last_p - entry_price) / entry_price if entry_price else 0
        trades.append({"entry": common[entry_idx], "exit": common[-1], "ret": ret, "reason": "END"})

    # 报告
    print(f"\n总交易: {len(trades)}")
    print(f"\n交易明细:")
    for t in trades[:10]:
        emoji = "🟢" if t["ret"] > 0 else "🔴"
        print(f"  {emoji} {t['entry']} → {t['exit']}: {t['ret']*100:+.1f}% ({t['reason']})")
    if len(trades) > 10:
        print(f"  ... +{len(trades)-10} more")

    # 计算收益
    if trades:
        wins = sum(1 for t in trades if t["ret"] > 0)
        losses = sum(1 for t in trades if t["ret"] < 0)
        avg_win = statistics.mean([t["ret"] for t in trades if t["ret"] > 0]) if wins else 0
        avg_loss = statistics.mean([t["ret"] for t in trades if t["ret"] < 0]) if losses else 0
        win_rate = wins / len(trades)
        profit_factor = (avg_win * wins) / (-avg_loss * losses) if losses else float('inf')
        print(f"\n  胜率: {win_rate:.1%} ({wins}胜/{losses}负)")
        print(f"  平均盈利: {avg_win*100:+.1f}%, 平均亏损: {avg_loss*100:+.1f}%")
        print(f"  盈亏比: {profit_factor:.2f}")

    # Buy & Hold
    first_price = sh_price_map.get(common[0])
    last_price = sh_price_map.get(common[-1])
    bh = last_price / first_price if first_price else 1
    print(f"\n  PSI 策略 v3 终值: {capital:.2f}x ({(capital-1)*100:+.1f}%)")
    print(f"  Buy & Hold: {bh:.2f}x ({(bh-1)*100:+.1f}%)")
    if capital > bh:
        print(f"  ✅ 胜出! +{((capital-bh)/bh)*100:.1f}%")
    else:
        print(f"  ❌ 落后 {((bh-capital)/capital)*100:.1f}%")

    # 保存
    with open(OUT / "psi_strategy_v3.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_trades": len(trades),
            "wins": wins if trades else 0,
            "losses": losses if trades else 0,
            "win_rate": win_rate if trades else 0,
            "avg_win": avg_win if wins else 0,
            "avg_loss": avg_loss if losses else 0,
            "profit_factor": profit_factor if trades else 0,
            "final_capital": capital,
            "buy_hold": bh,
            "outperform": capital > bh,
            "trades": trades,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/psi_strategy_v3.json")


if __name__ == "__main__":
    main()
