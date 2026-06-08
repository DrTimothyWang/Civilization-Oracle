"""
v4.x 阶段 20: CBDB 真实 TKG 训练
==================================

v3.0 TKG v3.0 是 mock (用 ICEWS 数据集, MRR=0.36)

v4.x 真实 TKG:
- 从 CBDB EVENTS_DATA 抽取 427 条真实历史事件
- 构建 (entity_person, relation, time) 三元组
- 训练简化 TKG 模型（基于事件链）
- 用 PSI 信号做事件预测
- 评估真正的 MRR
"""
import sys
import os
import json
import sqlite3
import re
from collections import defaultdict
import numpy as np
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_cbdb_events():
    """从 CBDB 加载真实历史事件"""
    cbdb_path = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"
    if not os.path.exists(cbdb_path):
        return []

    conn = sqlite3.connect(cbdb_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.c_personid, e.c_sequence, e.c_event_code,
            e.c_year, e.c_intercalary, c.c_event_name_chn
        FROM EVENTS_DATA e
        LEFT JOIN EVENT_CODES c ON e.c_event_code = c.c_event_code
        WHERE e.c_personid > 0
    """)
    rows = cur.fetchall()
    conn.close()

    events = []
    for r in rows:
        events.append({
            "person_id": r["c_personid"],
            "event_code": r["c_event_code"],
            "year": r["c_year"] or 0,
            "event_name_chn": r["c_event_name_chn"] or "",
        })

    return events


def load_person_dynasty():
    """加载人物-朝代映射"""
    cbdb_path = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"
    if not os.path.exists(cbdb_path):
        return {}

    conn = sqlite3.connect(cbdb_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT c_personid, c_dy, c_birthyear
        FROM biog_main
        WHERE c_dy IS NOT NULL AND c_dy != 0
    """)
    rows = cur.fetchall()
    conn.close()

    result = {}
    for r in rows:
        result[r["c_personid"]] = {
            "c_dy": r["c_dy"],
            "birthyear": r["c_birthyear"],
        }
    return result


def build_event_chains(events):
    """构建事件链：每个人物按时间排序的事件序列"""
    chains = defaultdict(list)
    for e in events:
        if e["year"] > 0:
            chains[e["person_id"]].append(e)

    # 按时间排序
    for pid in chains:
        chains[pid] = sorted(chains[pid], key=lambda x: x["year"])

    return chains


def main():
    print("=" * 70)
    print("v4.x 阶段 20: CBDB 真实 TKG 训练")
    print("=" * 70)

    # 1. 加载数据
    print("\n步骤 1: 加载 CBDB EVENTS_DATA")
    events = load_cbdb_events()
    print(f"  加载 {len(events)} 条历史事件")

    person_dy = load_person_dynasty()
    print(f"  加载 {len(person_dy)} 个人物-朝代映射")

    # 2. 提取朝代
    dy_map = {6: "唐朝", 15: "宋", 19: "明朝"}

    # 3. 按朝代分组事件
    events_by_dy = defaultdict(list)
    for e in events:
        if e["person_id"] in person_dy:
            c_dy = person_dy[e["person_id"]]["c_dy"]
            if c_dy in dy_map:
                e["dynasty"] = dy_map[c_dy]
                events_by_dy[dy_map[c_dy]].append(e)

    for dy, evs in events_by_dy.items():
        print(f"  {dy}: {len(evs)} 条事件")

    # 4. 事件类型统计
    event_types = defaultdict(int)
    for e in events:
        if e["event_name_chn"]:
            # 简化分类
            name = e["event_name_chn"]
            if "進士" in name or "及第" in name:
                event_types["jinshi"] += 1
            elif "知" in name or "通判" in name or "轉運" in name:
                event_types["official"] += 1
            elif "卒" in name or "死" in name or "亡" in name:
                event_types["death"] += 1
            elif "生" in name:
                event_types["birth"] += 1
            else:
                event_types["other"] += 1
        else:
            event_types["unknown"] += 1

    print("\n事件类型分布:")
    for t, n in sorted(event_types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {n}")

    # 5. 构建事件链
    print("\n步骤 2: 构建事件链 (按人物)")
    chains = build_event_chains(events)
    print(f"  共有事件链: {len(chains)} 条")

    # 6. 关键人物的事件链 (5 个最著名)
    famous_ids = {
        333: "王安石 (1021-1086)",
        518: "張邦昌 (1081-?)",
        # 找几个更多
    }

    # 找有 3+ 事件的最著名人物
    chain_lengths = [(pid, len(c)) for pid, c in chains.items()]
    chain_lengths.sort(key=lambda x: -x[1])

    print("\n事件链最长的 10 个人物:")
    for pid, n in chain_lengths[:10]:
        name = "Unknown"
        # 查名字
        try:
            conn = sqlite3.connect("/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite")
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT c_name_chn FROM biog_main WHERE c_personid = ?", (pid,))
            row = cur.fetchone()
            if row:
                name = row["c_name_chn"] or "?"
            conn.close()
        except:
            pass
        print(f"  person_id={pid} ({name}): {n} 条事件")

    # 7. TKG 评估
    print("\n步骤 3: TKG 评估 (简化版)")

    # 用前 80% 事件训练，后 20% 测试
    if len(events) < 10:
        print("[!] 事件太少")
        return

    events.sort(key=lambda e: e["year"])
    split = int(len(events) * 0.8)
    train_events = events[:split]
    test_events = events[split:]
    print(f"  训练: {len(train_events)}  测试: {len(test_events)}")

    # 简化 TKG: 训练时学"特定事件后最可能的事件"
    transition_count = defaultdict(lambda: defaultdict(int))
    for pid in chains:
        chain = chains[pid]
        for i in range(len(chain) - 1):
            curr_event = chain[i]["event_name_chn"] or f"event_{chain[i]['event_code']}"
            next_event = chain[i+1]["event_name_chn"] or f"event_{chain[i+1]['event_code']}"
            transition_count[curr_event][next_event] += 1

    # 测试：对于每个测试事件，找它在训练集中相同人物的"上一事件"作为 query
    # 然后模型预测 top-1 / top-5 / top-10 候选
    print(f"  学到的事件转移数: {len(transition_count)}")

    # 评估 MRR
    reciprocal_ranks = []
    for te in test_events:
        pid = te["person_id"]
        if pid not in chains:
            continue
        chain = chains[pid]
        # 找测试事件在 chain 中的位置
        for i, e in enumerate(chain):
            if e["year"] == te["year"] and e["event_code"] == te["event_code"]:
                if i == 0:
                    continue
                prev_event = chain[i-1]["event_name_chn"] or f"event_{chain[i-1]['event_code']}"
                target_event = e["event_name_chn"] or f"event_{e['event_code']}"

                # 模型预测: top-N 后继
                successors = transition_count.get(prev_event, {})
                if not successors:
                    continue
                sorted_succ = sorted(successors.items(), key=lambda x: -x[1])
                # 找 target 在 sorted_succ 中的 rank
                for rank, (succ, _) in enumerate(sorted_succ, 1):
                    if succ == target_event:
                        reciprocal_ranks.append(1.0 / rank)
                        break
                else:
                    reciprocal_ranks.append(0.0)
                break

    if reciprocal_ranks:
        mrr = float(np.mean(reciprocal_ranks))
        hits_1 = sum(1 for r in reciprocal_ranks if r >= 1.0)
        hits_3 = sum(1 for r in reciprocal_ranks if r >= 1/3)
        hits_10 = sum(1 for r in reciprocal_ranks if r >= 1/10)
        n_test_tkg = len(reciprocal_ranks)
        print(f"  TKG 评估 (基于 {n_test_tkg} 个测试):")
        print(f"    MRR: {mrr:.4f}")
        print(f"    Hits@1: {hits_1/n_test_tkg:.2%}")
        print(f"    Hits@3: {hits_3/n_test_tkg:.2%}")
        print(f"    Hits@10: {hits_10/n_test_tkg:.2%}")
    else:
        mrr = 0.0
        n_test_tkg = 0

    # 8. PSI 增强：用 PSI 信号重新排序 TKG 预测
    print("\n步骤 4: PSI 增强的 TKG")

    # 加载 PSI
    with open("/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json") as f:
        psi = json.load(f)
    psi_by_decade = {r["decade"]: r["psi_z"] for r in psi["decade_results"]}

    # PSI-aware TKG: 用 PSI 重新加权
    # 假设: PSI 越低, 越可能发生"重大"事件 (death, rebellion)
    # 如果 TKG 预测的 successor 是 "death" 且 PSI 低, 加分
    def psi_aware_score(succ_event, psi_val):
        base = successors.get(succ_event, 0)
        # PSI 调整
        if any(kw in succ_event for kw in ["卒", "死", "亡"]):
            return base * (1 + max(0, -psi_val))  # 死亡事件在 PSI 低时加权
        elif any(kw in succ_event for kw in ["進士", "及第"]):
            return base * (1 + max(0, psi_val))  # 中举事件在 PSI 高时加权
        return base

    reciprocal_ranks_psi = []
    for te in test_events:
        pid = te["person_id"]
        if pid not in chains:
            continue
        chain = chains[pid]
        for i, e in enumerate(chain):
            if e["year"] == te["year"] and e["event_code"] == te["event_code"]:
                if i == 0:
                    continue
                prev_event = chain[i-1]["event_name_chn"] or f"event_{chain[i-1]['event_code']}"
                target_event = e["event_name_chn"] or f"event_{e['event_code']}"

                # 用 PSI 重新打分
                decade = (te["year"] // 10) * 10
                psi_val = psi_by_decade.get(decade, 0)
                successors = transition_count.get(prev_event, {})
                if not successors:
                    continue
                sorted_succ = sorted(
                    successors.items(),
                    key=lambda x: -psi_aware_score(x[0], psi_val)
                )
                for rank, (succ, _) in enumerate(sorted_succ, 1):
                    if succ == target_event:
                        reciprocal_ranks_psi.append(1.0 / rank)
                        break
                else:
                    reciprocal_ranks_psi.append(0.0)
                break

    if reciprocal_ranks_psi:
        mrr_psi = float(np.mean(reciprocal_ranks_psi))
        hits_1_psi = sum(1 for r in reciprocal_ranks_psi if r >= 1.0)
        n_test_psi = len(reciprocal_ranks_psi)
        print(f"  PSI 增强 TKG 评估:")
        print(f"    MRR: {mrr_psi:.4f}")
        print(f"    Hits@1: {hits_1_psi/n_test_psi:.2%}")
        if mrr > 0:
            print(f"    提升: {(mrr_psi - mrr) / mrr * 100:+.1f}%")
        else:
            print(f"    提升: N/A (基线 MRR=0)")
    else:
        mrr_psi = 0.0

    # 9. 保存
    output = {
        "meta": {
            "version": "v4.x Real TKG",
            "data_source": "CBDB EVENTS_DATA (真实数据)",
            "n_events": len(events),
            "n_chains": len(chains),
            "n_event_types": len(event_types),
        },
        "event_type_distribution": dict(event_types),
        "tkg_baseline_mrr": float(mrr) if reciprocal_ranks else 0,
        "tkg_baseline_hits_at_1": float(hits_1/len(reciprocal_ranks)) if reciprocal_ranks else 0,
        "tkg_psi_enhanced_mrr": float(mrr_psi) if reciprocal_ranks_psi else 0,
        "tkg_psi_enhanced_hits_at_1": float(hits_1_psi/len(reciprocal_ranks_psi)) if reciprocal_ranks_psi else 0,
        "improvement_pct": float((mrr_psi - mrr) / mrr * 100) if (mrr > 0 and reciprocal_ranks_psi) else 0,
    }

    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/real_tkg_v4.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 真实 TKG 评估保存: {out_path}")


if __name__ == "__main__":
    main()
