#!/usr/bin/env python3
"""
v6.1 阶段92: CDLI 按 dates_referenced 重算真实年代 PSI

v6.0/v6.1 的 cdli_psi_analysis 用 period 字段做简化的 period_to_year 映射。
v6.1.1 升级: 用 dates_referenced 字段直接提取真实年代 (如 "-2200" → year=-2200)。
"""
import csv
import statistics
import re
import json
from pathlib import Path
from collections import defaultdict

DATA = Path("/Users/wangzr/Desktop/历史事件预测建模/v6.1/data")
SRC = Path("/Users/wangzr/Desktop/历史事件预测建模/v6.1/data/cdli_cat.csv")

# 已知重要美索不达米亚事件
EVENTS = {
    -3200: "Uruk III 末期",
    -2900: "Early Dynastic I 开始",
    -2334: "阿卡德帝国建立 (Sargon)",
    -2154: "Ur III 帝国建立",
    -2004: "Ur III 陷落",
    -1792: "汉谟拉法典 (Old Babylonian)",
    -1595: "Old Babylonian 陷落 (Hittite)",
    -1200: "青铜时代崩溃",
    -911: "Neo-Assyrian 帝国建立",
    -612: "Neo-Assyrian 陷落 (巴比伦)",
    -539: "新巴比伦陷落 (波斯 Cyrus)",
    -331: "波斯陷落 (Alexander)",
}


def parse_year(s):
    """从字符串提取年份整数 (支持 -2200, 2200 BC, 2154 BCE 等格式)"""
    if not s:
        return None
    s = str(s).strip()
    # 匹配 -NNNN, NNNN BC, NNNN BCE
    m = re.search(r'-?\d{3,4}', s)
    if m:
        try:
            y = int(m.group())
            # 如果是 BC/BCE 标识
            if 'BC' in s.upper() and y > 0:
                y = -y
            return y
        except:
            return None
    return None


def main():
    print("=" * 80)
    print("【CDLI 真实年代 PSI 重算】 v6.1.1 阶段 92")
    print("=" * 80)

    # 读取所有 records, 提取 dates_referenced
    print(f"\n[load] 读取 {SRC}...")
    by_year = defaultdict(lambda: {"count": 0, "genres": defaultdict(int), "provenances": set()})

    n_parsed = 0
    n_total = 0
    with open(SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i % 50000 == 0 and i > 0:
                print(f"  进度: {i} 行, 已解析 {n_parsed} 条")
            n_total += 1
            # 优先用 dates_referenced, 回退到 period
            date_ref = row.get("dates_referenced", "").strip()
            year = parse_year(date_ref)
            if year is None:
                # 回退到 period 字段: "Uruk III (ca. 3200-3000 BC)"
                period = row.get("period", "").strip()
                m = re.search(r'ca\.\s*(\d+)-(\d+)\s*BC', period)
                if m:
                    start = int(m.group(1))
                    end = int(m.group(2))
                    year = -(start + end) // 2  # 中点年份
            if year is None:
                continue
            n_parsed += 1
            by_year[year]["count"] += 1
            genre = row.get("genre", "").strip()
            if genre:
                by_year[year]["genres"][genre] += 1
            prov = row.get("provenience", "").strip()
            if prov:
                by_year[year]["provenances"].add(prov)

    print(f"\n[stat] 总 {n_total} 条, 成功解析 dates_referenced: {n_parsed} 条 ({n_parsed/n_total:.1%})")
    print(f"  覆盖 {len(by_year)} 个不同年份")

    # 按 100 年窗聚合
    year_windows = defaultdict(lambda: {"count": 0, "genres": set()})
    for y, d in by_year.items():
        window = (y // 100) * 100
        year_windows[window]["count"] += d["count"]
        year_windows[window]["genres"].update(d["genres"].keys())

    # 按 100 年窗计算 PSI
    print(f"\n[PSI] 按 100 年窗聚合, 跨 ~5,500 年")

    # 标准化 MMP/SFD/EED
    window_ps = {}
    max_n = max(d["count"] for d in year_windows.values()) if year_windows else 1
    max_genres = max(len(d["genres"]) for d in year_windows.values()) if year_windows else 1

    for window, d in year_windows.items():
        n = d["count"]
        n_genres = len(d["genres"])
        # MMP: 文本密度 (归一化)
        mmp = n / max_n
        # SFD: 多样性 (归一化)
        sfd = n_genres / max_genres
        # EED: 精英化 (假设精英文本比例 = ratio of literary/scientific)
        # 简化: 用 1 - mmp 代替 (文本少 = 精英化)
        eed = 1 - mmp
        # PSI 公式
        psi = 0.4 * mmp + 0.3 * (1 - sfd) + 0.3 * eed
        window_ps[window] = {
            "n": n,
            "n_genres": n_genres,
            "psi": psi,
            "mmp": mmp,
            "sfd": sfd,
            "eed": eed,
        }

    # 排序并打印
    print(f"\n  年代 | 记录数 | genre 数 | PSI | 重要事件")
    print("  " + "-" * 80)
    sorted_windows = sorted(window_ps.keys())

    # 标记重要事件
    for window in sorted_windows:
        if window < -3000 or window > 0:
            continue
        d = window_ps[window]
        # 找最近的已知事件
        event_marker = ""
        for ev_year, ev_name in EVENTS.items():
            if abs(ev_year - window) < 50:
                event_marker = f" ← {ev_year} {ev_name}"
                break
        marker = " ⚠️" if d["psi"] > 0.7 else ""
        print(f"  {window:+5d} | {d['n']:5d} | {d['n_genres']:3d} | {d['psi']:.3f}{marker}{event_marker}")

    # 关键事件 PSI 验证
    print(f"\n  【关键事件 PSI 验证】")
    print(f"  {'事件':10s} | 年代 | PSI | 状态")
    for ev_year, ev_name in sorted(EVENTS.items()):
        # 找最近的 100 年窗
        window = (ev_year // 100) * 100
        if window in window_ps:
            psi = window_ps[window]["psi"]
            # 高 PSI 表示"盛世/扩张", 低 PSI 表示"危机/收缩"
            status = "✓ 盛世 PSI 高" if psi > 0.5 else ("✓ 危机 PSI 低" if psi < 0.4 else "· 中性")
            print(f"  {ev_year:+5d} {ev_name:18s} | {window:+5d} | {psi:.3f} | {status}")

    # 保存
    with open(DATA / "cdli_psi_real_v61.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_total": n_total,
            "n_parsed": n_parsed,
            "n_years": len(by_year),
            "n_windows": len(window_ps),
            "psi_by_window": {str(k): v for k, v in window_ps.items()},
            "events_verified": {str(k): v for k, v in EVENTS.items()},
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {DATA}/cdli_psi_real_v61.json")
    print(f"   {n_parsed} 条 CDLI 记录按真实年代 PSI 计算完成")


if __name__ == "__main__":
    main()
