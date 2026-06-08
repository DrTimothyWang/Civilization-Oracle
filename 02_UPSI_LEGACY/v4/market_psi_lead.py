#!/usr/bin/env python3
"""
阶段 36b: 金融 PSI Lead Time 分析
- 计算每个已知危机: 第一个 PSI_z<-0.5 信号距离危机有多少天?
- 计算 "预警精度"：在 PSI<-0.5 后的 30/60/90 天内发生危机的频率
- 假阳率：所有 PSI<-0.5 信号中，多少比例后面真的发生危机？
"""
import json
import statistics
from datetime import datetime
from pathlib import Path

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v4/data")
with open(DATA / "market_psi_v4.json", encoding="utf-8") as f:
    results = json.load(f)


def date_diff(d1, d2):
    a = datetime.strptime(d1, "%Y-%m-%d")
    b = datetime.strptime(d2, "%Y-%m-%d")
    return (a - b).days


# 已知金融危机列表
known_crises = [
    "2018-10-11", "2019-05-10", "2020-01-23", "2020-03-23",
    "2022-02-24", "2022-10-31", "2024-02-05",
]

# 上证市场做完整分析
key = "sh000001"
r = results[key]
dates = r["dates"]
psi = r["psi"]
date_to_psi = dict(zip(dates, psi))

# 1. 危机前第一个 PSI_z < -0.5 信号的天数
print("=" * 60)
print(f"【{key}】 危机预警 Lead Time (首次 PSI_z < -0.5 至危机日)")
print("=" * 60)
for crisis in known_crises:
    if crisis not in date_to_psi:
        continue
    crisis_idx = dates.index(crisis)
    # 向前找第一个 PSI<-0.5
    lead = None
    for i in range(crisis_idx, -1, -1):
        if psi[i] < -0.5:
            lead = crisis_idx - i
            break
    if lead is not None:
        lead_date = dates[crisis_idx - lead]
        print(f"  {crisis}: Lead={lead} 天, 信号日 {lead_date}, 信号强度 {psi[crisis_idx - lead]:.2f}")
    else:
        print(f"  {crisis}: 无 PSI<-0.5 信号")

# 2. 假阳率分析
print()
print("=" * 60)
print(f"【{key}】 假阳率分析: PSI_z < -0.5 信号的危机命中率")
print("=" * 60)
signals = [(d, p) for d, p in zip(dates, psi) if p < -0.5]
print(f"  总信号数: {len(signals)}")

# 90 天窗口: 信号后 90 天内是否发生已知危机
hits = 0
n_known = 0
for crisis in known_crises:
    if crisis not in date_to_psi:
        continue
    n_known += 1
    crisis_idx = dates.index(crisis)
    # 看 crisis 前 180 天内是否有 PSI<-0.5
    has_signal = any(psi[i] < -0.5 for i in range(max(0, crisis_idx-180), crisis_idx+1))
    if has_signal:
        hits += 1
print(f"  已知危机被 PSI<-0.5 提前预警 (180天内): {hits}/{n_known} = {hits/n_known:.0%}")

# 3. 假阳率 (总信号中, 后面 90 天内真发生危机的比例)
# 但要排除已知危机造成的"成功信号"
print()
print("=" * 60)
print(f"【{key}】 信号后 90 天内发生已知危机?")
print("=" * 60)
signal_followed_by_crisis = 0
for sig_date, sig_psi in signals:
    for crisis in known_crises:
        if crisis not in date_to_psi:
            continue
        diff = date_diff(crisis, sig_date)
        if 0 < diff <= 90:
            signal_followed_by_crisis += 1
            break
print(f"  {len(signals)} 个信号中, 90 天内有已知危机跟进的: {signal_followed_by_crisis}")
print(f"  粗命中率: {signal_followed_by_crisis/len(signals):.0%} (但可能多重信号算一次)")

# 4. PSI<0 占比 与未来收益 (回归)
print()
print("=" * 60)
print(f"【{key}】 PSI<0 占比 与 未来 20/60 日收益")
print("=" * 60)
# 重新载入价格
with open(DATA / "market_raw_data.json", encoding="utf-8") as f:
    raw = json.load(f)
sse_raw = raw["sh000001"]
# 建 date->close 映射 (用 close 字段, 腾讯格式: [date, open, close, high, low, vol])
date_to_close = {}
for bar in sse_raw:
    if isinstance(bar, list):
        d, o, c = bar[0], bar[1], bar[2]
        date_to_close[d] = float(c)

# 对齐: dates[i] 时, 未来 20 天收益 = close[i+20]/close[i] - 1
fut20, fut60 = [], []
for i, d in enumerate(dates):
    # 找 i+20, i+60
    if i + 20 < len(dates):
        d20 = dates[i+20]
        if d in date_to_close and d20 in date_to_close:
            fut20.append(date_to_close[d20] / date_to_close[d] - 1)
        else:
            fut20.append(None)
    if i + 60 < len(dates):
        d60 = dates[i+60]
        if d in date_to_close and d60 in date_to_close:
            fut60.append(date_to_close[d60] / date_to_close[d] - 1)
        else:
            fut60.append(None)

# PSI<0 时的平均未来收益 vs PSI>0 时
n = min(len(fut20), len(psi))
psi_aligned = psi[:n]
fut20_aligned = fut20[:n]
fut60_aligned = fut60[:n]
neg_fut20 = [f for f, p in zip(fut20_aligned, psi_aligned) if f is not None and p < -0.5]
pos_fut20 = [f for f, p in zip(fut20_aligned, psi_aligned) if f is not None and p > 0.5]
neg_fut60 = [f for f, p in zip(fut60_aligned, psi_aligned) if f is not None and p < -0.5]
pos_fut60 = [f for f, p in zip(fut60_aligned, psi_aligned) if f is not None and p > 0.5]
print(f"  PSI<-0.5 时未来20日平均收益: {statistics.mean(neg_fut20):.2%} (N={len(neg_fut20)})")
print(f"  PSI> 0.5 时未来20日平均收益: {statistics.mean(pos_fut20):.2%} (N={len(pos_fut20)})")
print(f"  PSI<-0.5 时未来60日平均收益: {statistics.mean(neg_fut60):.2%} (N={len(neg_fut60)})")
print(f"  PSI> 0.5 时未来60日平均收益: {statistics.mean(pos_fut60):.2%} (N={len(pos_fut60)})")

# 5. 跨市场 PSI<0 一致性 (多市场同时 PSI<0 = 强信号)
print()
print("=" * 60)
print("【跨市场】 多市场同时 PSI<-0.5 的日期 (系统性危机信号)")
print("=" * 60)
markets = ["sh000001", "hkHSI", "sz399001_sina", "sh000300_sina"]
common_dates = set(results["sh000001"]["dates"])
for m in markets[1:]:
    common_dates &= set(results[m]["dates"])
common_dates = sorted(common_dates)
print(f"  4 市场共同日期: {len(common_dates)} 天")
sys_signals = []
for d in common_dates:
    n_neg = sum(1 for m in markets if results[m]["psi"][results[m]["dates"].index(d)] < -0.5)
    if n_neg >= 3:
        sys_signals.append((d, n_neg))
print(f"  至少 3 市场同时 PSI<-0.5 的天数: {len(sys_signals)}")
for d, n in sys_signals[:20]:
    print(f"    {d}: {n} 市场")

# 6. 保存 lead time 表
lead_table = {}
for crisis in known_crises:
    if crisis not in date_to_psi:
        continue
    crisis_idx = dates.index(crisis)
    lead = None
    for i in range(crisis_idx, -1, -1):
        if psi[i] < -0.5:
            lead = crisis_idx - i
            break
    lead_table[crisis] = {
        "lead_days": lead,
        "signal_date": dates[crisis_idx - lead] if lead else None,
        "signal_psi": psi[crisis_idx - lead] if lead else None,
    }
out = {
    "key": key,
    "lead_table": lead_table,
    "n_signals": len(signals),
    "hit_rate_180d": hits / n_known,
    "fut20_neg_psi": statistics.mean(neg_fut20) if neg_fut20 else None,
    "fut20_pos_psi": statistics.mean(pos_fut20) if pos_fut20 else None,
    "fut60_neg_psi": statistics.mean(neg_fut60) if neg_fut60 else None,
    "fut60_pos_psi": statistics.mean(pos_fut60) if pos_fut60 else None,
    "n_systemic_signals": len(sys_signals),
}
with open(DATA / "market_psi_lead.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\n✅ 保存到 {DATA}/market_psi_lead.json")
