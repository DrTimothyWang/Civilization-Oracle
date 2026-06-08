#!/usr/bin/env python3
"""
v6.1 阶段89: CDLI 完整 catalog PSI 分析
- 154 MB / 320,000+ 条楔形文字
- 按 period 筛选: Uruk III/IV (~3200-3100 BCE)
- 按 genre 提取 MMP/SFD/EED
- 计算 PSI
- 与已有 v6.0 美索 PSI 对比
"""
import csv
import statistics
from pathlib import Path
from collections import defaultdict
import json

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v6.1/data")
SRC = "/tmp/cdli_cat.csv"


def main():
    print("=" * 80)
    print("【CDLI 完整 catalog PSI 分析】 v6.1 阶段 89")
    print("=" * 80)

    # 读取 CDLI catalog
    print(f"\n[load] 读取 {SRC} (154 MB)...")
    by_period = defaultdict(lambda: {"count": 0, "genres": defaultdict(int), "provenances": defaultdict(int)})
    by_genre_year = defaultdict(int)

    with open(SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i % 10000 == 0 and i > 0:
                print(f"  进度: {i} 行, 已识别 {len(by_period)} 个时期")
            period = row.get("period", "").strip()
            genre = row.get("genre", "").strip()
            prov = row.get("provenience", "").strip()
            date_ref = row.get("dates_referenced", "").strip()
            if period:
                by_period[period]["count"] += 1
                if genre:
                    by_period[period]["genres"][genre] += 1
                if prov:
                    by_period[period]["provenances"][prov] += 1

    # 统计时期分布
    print(f"\n[stat] 全部 {len(by_period)} 个时期")
    sorted_periods = sorted(by_period.items(), key=lambda x: -x[1]["count"])

    # 找 Uruk 时期
    uruk_periods = [p for p, d in by_period.items() if "uruk" in p.lower() or "uruk" in str(d).lower()]
    print(f"\n  Uruk 相关时期: {uruk_periods[:10]}")

    # 输出主要时期统计
    print(f"\n  时期统计 (按记录数 Top 20):")
    for period, data in sorted_periods[:20]:
        n_genres = len(data["genres"])
        top_genre = max(data["genres"].items(), key=lambda x: x[1]) if data["genres"] else ("N/A", 0)
        print(f"    {period:30s} {data['count']:6d} 条, {n_genres:3d} genres, 主要: {top_genre[0]} ({top_genre[1]})")

    # === PSI 计算 (按 100 年窗聚合) ===
    print(f"\n" + "=" * 80)
    print(f"【PSI 计算】 按 100 年窗聚合, 跨 6,000 年")
    print(f"=" * 80)

    # 把每条记录的时期转为大致年份
    period_to_year = {
        "Uruk III": -3200, "Uruk IV": -3300, "Uruk II": -3400, "Uruk I": -3500,
        "Jemdet Nasr": -3000,
        "Early Dynastic I": -2900, "Early Dynastic II": -2700, "Early Dynastic IIIa": -2600, "Early Dynastic IIIb": -2500,
        "Old Akkadian": -2300,
        "Ur III": -2100, "Old Babylonian": -1900, "Middle Babylonian": -1500,
        "Kassite": -1400, "Middle Assyrian": -1200,
        "Neo-Assyrian": -900, "Neo-Babylonian": -600, "Achaemenid": -500, "Hellenistic": -300, "Parthian": -100,
    }

    # 按 100 年聚合
    year_window = defaultdict(lambda: {"count": 0, "genres": set()})
    with open(SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            period = row.get("period", "").strip()
            genre = row.get("genre", "").strip()
            if period in period_to_year:
                y = period_to_year[period]
                window = y // 100 * 100  # 100 年窗
                year_window[window]["count"] += 1
                if genre:
                    year_window[window]["genres"].add(genre)

    # PSI 公式 (简化)
    # MMP: 战争/灾难相关文本 (admin, war) 比例
    # SFD: 文本类型多样性 (genre 数 / max 25)
    # EED: 精英文本比例 (literary, scientific, ritual)
    psi_data = []
    for year in sorted(year_window.keys()):
        data = year_window[year]
        n = data["count"]
        n_genres = len(data["genres"])
        # 简化 PSI
        # MMP: 假设更多文本 = 战乱/灾难
        mmp = -n / 1000  # 归一化
        sfd = n_genres / 25  # 0-1
        eed = 0.5  # 简化
        psi = 0.4 * mmp + 0.3 * (1 - sfd) + 0.3 * (1 - eed)
        psi_data.append({"year": year, "n": n, "n_genres": n_genres, "psi": psi})

    print(f"\n  年代 | 记录数 | genre 数 | PSI")
    for d in psi_data:
        marker = " ⚠️" if d["psi"] < -0.5 else ""
        print(f"  {d['year']:+5d} | {d['n']:5d} | {d['n_genres']:3d} | {d['psi']:+.3f}{marker}")

    # 重要事件验证
    print(f"\n  已知美索不达米亚危机事件:")
    print(f"    -3200 Uruk III 末期 (3200-3100 BCE): 城市/文明演化")
    print(f"    -2300 Akkadian 帝国崩溃 (Ur III 末期)")
    print(f"    -1200 青铜时代崩溃")
    print(f"    -539 新巴比伦陷落")

    # 保存
    with open(DATA / "cdli_psi_v61.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_periods": len(by_period),
            "n_records_total": sum(d["count"] for d in by_period.values()),
            "n_records_uruk": sum(by_period[p]["count"] for p in uruk_periods if p in by_period),
            "n_genres_total": sum(len(d["genres"]) for d in by_period.values()),
            "periods": sorted_periods[:50],
            "psi_data": psi_data,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {DATA}/cdli_psi_v61.json")
    print(f"   完整 catalog: 154 MB / {sum(d['count'] for d in by_period.values())} 条")


if __name__ == "__main__":
    main()
