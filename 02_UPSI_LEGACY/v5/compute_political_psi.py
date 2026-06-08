#!/usr/bin/env python3
"""
v5.0 阶段46a: 政治 PSI (Wikipedia/Wikidata)
- 1000+ 战争 + 革命事件
- 时间线: -1000 to 2026
- 按年份聚合成"政治压力指数"
- 检验 PSI<-0 模式匹配历史重大危机
"""
import json
import requests
from pathlib import Path
from datetime import datetime
import time
import statistics
from collections import defaultdict

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v5/data")

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "PSI-Research/1.0 (mavis@example.com)"}


def fetch_events():
    """拉所有战争 + 革命事件"""
    events = []
    for etype, qid, label in [
        ("war", "Q198", "war"),
        ("revolution", "Q10931", "revolution"),
        ("civil_conflict", "Q215140", "civil conflict"),
    ]:
        print(f"[fetch] {label} ({qid})...")
        offset = 0
        while True:
            query = f"""
SELECT ?item ?itemLabel ?start ?end ?deaths ?countryLabel WHERE {{
  ?item wdt:P31 wd:{qid} .
  ?item wdt:P580 ?start .
  OPTIONAL {{ ?item wdt:P582 ?end }}
  OPTIONAL {{ ?item wdt:P1120 ?deaths }}
  OPTIONAL {{ ?item wdt:P17 ?country }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'en' }}
}}
ORDER BY ?start
LIMIT 1000
OFFSET {offset}
"""
            try:
                r = requests.get(WIKIDATA_SPARQL,
                                 params={"query": query, "format": "json"},
                                 headers=HEADERS, timeout=60)
                data = r.json()
                bindings = data.get("results", {}).get("bindings", [])
                if not bindings:
                    break
                for b in bindings:
                    start = b.get("start", {}).get("value", "")[:10]
                    end = b.get("end", {}).get("value", "")[:10] if "end" in b else None
                    deaths = float(b.get("deaths", {}).get("value", 0)) if "deaths" in b else 0
                    name = b.get("itemLabel", {}).get("value", "")
                    country = b.get("countryLabel", {}).get("value", "")
                    if start:
                        events.append({
                            "type": etype,
                            "name": name,
                            "start": start,
                            "end": end,
                            "deaths": deaths,
                            "country": country,
                        })
                print(f"  offset {offset}: {len(bindings)} events")
                if len(bindings) < 1000:
                    break
                offset += 1000
                time.sleep(0.5)
            except Exception as e:
                print(f"  err: {e}")
                break

    return events


def compute_political_psi(events, window=10):
    """按年份聚合 + PSI 三维度"""
    # 1. 按年统计事件数 + 死亡数
    by_year = defaultdict(lambda: {"n_events": 0, "deaths": 0, "events": []})
    for e in events:
        try:
            year = int(e["start"][:4]) if e["start"][0] != "-" else -int(e["start"][1:5])
        except:
            continue
        by_year[year]["n_events"] += 1
        by_year[year]["deaths"] += e["deaths"]
        by_year[year]["events"].append(e["name"])

    years = sorted(by_year.keys())
    n_events = [by_year[y]["n_events"] for y in years]
    deaths = [by_year[y]["deaths"] for y in years]
    intensity = [n + d/10000 for n, d in zip(n_events, deaths)]  # 综合强度

    # 2. PSI 三维度
    L = len(years) - window
    psi = []
    psi_dates = []
    for i in range(L):
        y = years[i+window]
        sub_n = n_events[i:i+window+1]
        sub_d = deaths[i:i+window+1]
        sub_i = intensity[i:i+window+1]
        # MMP: 当前事件数 vs 前期均值
        mmp = sub_n[-1] - statistics.mean(sub_n[:-1])
        # SFD: 死亡数波动
        sfd = statistics.stdev(sub_d) if len(sub_d) > 1 else 0
        # EED: 强度变化率
        if sub_i[-2] > 0:
            eed = (sub_i[-1] - sub_i[-2]) / sub_i[-2]
        else:
            eed = 0
        psi.append(mmp + sfd/1000 + eed)
        psi_dates.append(y)

    # z-score 标准化
    mu = statistics.mean(psi)
    sd = statistics.stdev(psi)
    psi_z = [(p - mu) / sd for p in psi]

    return {"years": psi_dates, "psi": psi_z, "intensity": intensity[L:], "n_events": n_events[L:]}


def main():
    # 拉数据
    events = fetch_events()
    print(f"\n[load] {len(events)} events loaded")
    # 写原始
    with open(OUT / "wikidata_events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False)
    print(f"✅ 保存 {OUT}/wikidata_events.json")

    # 算 PSI
    psi = compute_political_psi(events, window=10)
    print(f"\n[PSI] {len(psi['psi'])} 年份")
    print(f"  PSI 范围: {min(psi['psi']):.2f} ~ {max(psi['psi']):.2f}")

    # 检验历史大事件
    MAJOR = {
        -218: "第二次布匿战争",
        -49: "凯撒内战",
        117: "图拉真巅峰",
        235: "三世纪危机",
        410: "西哥特洗劫罗马",
        476: "西罗马灭亡",
        622: "伊斯兰创立",
        800: "查理曼加冕",
        1066: "诺曼征服",
        1215: "大宪章",
        1347: "黑死病",
        1453: "君士坦丁堡陷落",
        1492: "哥伦布",
        1517: "宗教改革",
        1648: "威斯特伐利亚",
        1789: "法国大革命",
        1815: "拿破仑战争结束",
        1848: "欧洲革命",
        1861: "美国内战",
        1914: "一战",
        1918: "一战结束",
        1929: "大萧条",
        1939: "二战",
        1945: "二战结束",
        1950: "朝鲜战争",
        1968: "全球抗议",
        1975: "越战结束",
        1989: "柏林墙",
        1991: "苏联解体",
        2001: "911",
        2008: "GFC",
        2011: "阿拉伯之春",
        2020: "COVID",
        2022: "俄乌",
    }

    print("\n" + "=" * 80)
    print("【政治 PSI 检验】 PSI<-0 是否匹配已知历史危机")
    print("=" * 80)
    psi_map = dict(zip(psi["years"], psi["psi"]))
    hits = 0
    n_tested = 0
    for year, name in MAJOR.items():
        # 找 ± 5 年窗口内 PSI 极小
        in_range = [(y, p) for y, p in psi_map.items() if abs(y - year) <= 5]
        if not in_range:
            continue
        n_tested += 1
        min_y, min_p = min(in_range, key=lambda x: x[1])
        if min_p < 0:
            hits += 1
        lead = year - min_y
        marker = "✓" if min_p < -0.5 else ("·" if min_p < 0 else " ")
        print(f"  {marker} {year:+5d} {name:25s} | 极小 PSI {min_p:+.2f} @ {min_y:+5d} (Lead {lead:+3d})")

    print(f"\n  召回: {hits}/{n_tested} = {hits/n_tested:.0%}")

    # 保存
    with open(OUT / "political_psi_v5.json", "w", encoding="utf-8") as f:
        json.dump({
            "psi": {"years": psi["years"], "psi": psi["psi"]},
            "n_events": len(events),
            "n_years": len(psi["psi"]),
            "psi_range": [min(psi["psi"]), max(psi["psi"])],
            "historical_test": {
                "n_tested": n_tested,
                "n_hits": hits,
                "recall": hits / n_tested if n_tested else 0,
            },
        }, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/political_psi_v5.json")


if __name__ == "__main__":
    main()
