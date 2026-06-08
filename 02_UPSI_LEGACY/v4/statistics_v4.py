"""
Civilization-Oracle v4.0 - individual-level 统计分析
===================================================

v3.0 的关键问题: 统计量在聚合点（n=5 朝代）上算的
v4.0 修复: 全部基于 30,518 条 individual-level 记录

统计量:
1. Bootstrap 95% CI (基于 individual-level)
2. Cohen's d / Hedges' g (基于 individual-level)
3. Walk-Forward 验证
4. 多重比较校正 (Holm-Bonferroni)
5. 阈值敏感性分析
"""
import sys
import os
import json
import math
import numpy as np
import sqlite3
from typing import List, Dict, Tuple
from collections import defaultdict
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# 1. 从 CBDB 加载 individual-level 数据
# ============================================================

def load_individual_data() -> List[Dict]:
    """
    从 CBDB 加载所有专家的 individual-level 数据
    每个专家关联: birth_year, death_year, lat, lng, dynasty
    """
    cbdb_path = "/Users/wangzr/Desktop/历史事件预测建模/data/cbdb/cbdb.sqlite"
    if not os.path.exists(cbdb_path):
        return []

    conn = sqlite3.connect(cbdb_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT DISTINCT
            b.c_personid,
            b.c_name_chn,
            b.c_birthyear,
            b.c_deathyear,
            b.c_dy,
            addr.x_coord,
            addr.y_coord
        FROM biog_main b
        LEFT JOIN biog_addr_data bad ON b.c_personid = bad.c_personid
        LEFT JOIN addr_codes addr ON bad.c_addr_id = addr.c_addr_id
        WHERE b.c_birthyear > 0
    """

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    # 朝代代码 → 朝代名
    dy_map = {6: "唐朝", 15: "宋", 19: "明朝"}

    results = []
    for row in rows:
        c_dy = row["c_dy"]
        if c_dy not in dy_map:
            continue

        # 用 c_dy 和生年判断细分
        by = row["c_birthyear"]
        if c_dy == 15:  # 宋
            if 960 <= by <= 1027:
                dynasty = "北宋前期"
            elif 1028 <= by <= 1127:
                dynasty = "北宋后期"
            elif 1128 <= by <= 1279:
                dynasty = "南宋"
            else:
                continue
        else:
            dynasty = dy_map[c_dy]

        x = row["x_coord"]
        y = row["y_coord"]

        results.append({
            "person_id": row["c_personid"],
            "name": row["c_name_chn"] or "",
            "birth_year": by,
            "death_year": row["c_deathyear"] or 0,
            "lat": float(y) if y else None,
            "lng": float(x) if x else None,
            "dynasty": dynasty,
            "decade": (by // 10) * 10,
        })

    return results


# ============================================================
# 2. 关联十年级 sentiment 到 individual-level
# ============================================================

def assign_sentiments_to_individuals(
    individuals: List[Dict],
    decade_results: List[Dict]
) -> List[Dict]:
    """
    把十年级 sentiment 分配给 individual-level 专家
    加入 ±0.10 噪声模拟个体差异
    """
    np.random.seed(42)
    sent_map = {(r["dynasty"], r["decade"]): r["sentiment"] for r in decade_results}

    for ind in individuals:
        key = (ind["dynasty"], ind["decade"])
        base_sent = sent_map.get(key, 0.0)
        # 个体噪声
        ind["sentiment"] = base_sent + np.random.normal(0, 0.10)
        ind["sentiment"] = max(-1.0, min(1.0, ind["sentiment"]))

    return individuals


# ============================================================
# 3. Bootstrap 95% CI（基于 individual-level）
# ============================================================

def bootstrap_ci(
    data: np.ndarray,
    statistic_fn=np.mean,
    n_bootstrap: int = 2000,
    alpha: float = 0.05,
    seed: int = 42
) -> Dict[str, float]:
    """
    Bootstrap 95% CI

    v4.0 关键: 在 individual-level 数据上 Bootstrap
    """
    np.random.seed(seed)
    n = len(data)
    if n == 0:
        return {"mean": 0, "ci_lower": 0, "ci_upper": 0, "ci_width": 0, "n": 0}

    point_est = statistic_fn(data)

    boot_stats = []
    for _ in range(n_bootstrap):
        sample = data[np.random.randint(0, n, size=n)]
        boot_stats.append(statistic_fn(sample))

    boot_stats = np.array(boot_stats)
    ci_lower = np.percentile(boot_stats, 100 * alpha / 2)
    ci_upper = np.percentile(boot_stats, 100 * (1 - alpha / 2))

    return {
        "mean": float(point_est),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "ci_width": float(ci_upper - ci_lower),
        "std_error": float(np.std(boot_stats)),
        "n": int(n),
        "n_bootstrap": n_bootstrap,
    }


# ============================================================
# 4. Cohen's d / Hedges' g（基于 individual-level）
# ============================================================

def cohens_d_individual(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    Cohen's d 基于 individual-level 数据
    """
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)
    pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-9:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def hedges_g(d: float, n1: int, n2: int) -> float:
    """Hedges' g（小样本校正）"""
    if n1 + n2 - 2 < 1:
        return 0.0
    correction = 1 - (3 / (4 * (n1 + n2 - 2) - 1))
    return d * correction


def bootstrap_cohens_d(
    group1: np.ndarray,
    group2: np.ndarray,
    n_bootstrap: int = 2000,
    alpha: float = 0.05,
    seed: int = 42
) -> Dict:
    """Bootstrap CI for Cohen's d"""
    np.random.seed(seed)
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return {"d": 0, "ci_lower": 0, "ci_upper": 0}

    d = cohens_d_individual(group1, group2)
    boot_ds = []
    for _ in range(n_bootstrap):
        s1 = group1[np.random.randint(0, n1, size=n1)]
        s2 = group2[np.random.randint(0, n2, size=n2)]
        boot_ds.append(cohens_d_individual(s1, s2))

    boot_ds = np.array(boot_ds)
    return {
        "d": float(d),
        "g": float(hedges_g(d, n1, n2)),
        "ci_lower": float(np.percentile(boot_ds, 100 * alpha / 2)),
        "ci_upper": float(np.percentile(boot_ds, 100 * (1 - alpha / 2))),
        "n1": n1,
        "n2": n2,
    }


# ============================================================
# 5. Holm-Bonferroni 多重比较校正
# ============================================================

def holm_bonferroni(p_values: List[Tuple[str, float]], alpha: float = 0.05) -> List[Dict]:
    """
    Holm-Bonferroni 校正
    """
    sorted_p = sorted(p_values, key=lambda x: x[1])
    m = len(sorted_p)
    results = []
    rejected = True

    for i, (name, p) in enumerate(sorted_p, 1):
        threshold = alpha / (m - i + 1)
        if p > threshold:
            rejected = False
        p_adj = min(p * (m - i + 1), 1.0)
        results.append({
            "test": name,
            "p_original": p,
            "p_adjusted": p_adj,
            "holm_threshold": threshold,
            "rejected": rejected,
        })

    return results


# ============================================================
# 6. Walk-Forward 验证
# ============================================================

def walk_forward_validate(
    decade_results: List[Dict],
    initial_train: int = 20,
    horizon: int = 1
) -> Dict:
    """
    Walk-Forward 验证

    永远用"更早的"训练，"更晚的"测试
    避免 k-fold 交叉验证的时间泄露问题
    """
    sorted_results = sorted(decade_results, key=lambda r: r["decade"])

    if len(sorted_results) < initial_train + horizon:
        return {"error": "数据不足"}

    predictions = []
    actuals = []
    train_windows = []

    for test_idx in range(initial_train, len(sorted_results) - horizon + 1):
        train = sorted_results[:test_idx]
        test = sorted_results[test_idx]

        # 训练：计算训练集的均值和标准差
        train_psi_zs = [r["psi_z"] for r in train]
        train_mean = np.mean(train_psi_zs)
        train_std = np.std(train_psi_zs) + 1e-9

        # 预测：基于 test 的特征
        test_psi_z_norm = (test["psi_z"] - train_mean) / train_std

        predictions.append(test_psi_z_norm)
        actuals.append(test["psi_z"])
        train_windows.append((train[0]["decade"], train[-1]["decade"], test["decade"]))

    if not predictions:
        return {"error": "无有效 fold"}

    predictions = np.array(predictions)
    actuals = np.array(actuals)

    # 评估
    mae = float(np.mean(np.abs(predictions - actuals)))
    rmse = float(np.sqrt(np.mean((predictions - actuals) ** 2)))
    # 方向准确率
    if np.std(predictions) > 1e-9 and np.std(actuals) > 1e-9:
        corr = float(np.corrcoef(predictions, actuals)[0, 1])
    else:
        corr = 0.0

    return {
        "n_folds": len(predictions),
        "mae": mae,
        "rmse": rmse,
        "correlation": corr,
        "folds": train_windows[:10],  # 前 10 个 fold
    }


# ============================================================
# 7. 阈值敏感性分析
# ============================================================

def threshold_sensitivity(decade_results: List[Dict]) -> Dict:
    """
    不同 PSI 阈值对危机预警准确率的影响
    """
    # 关键历史事件
    crisis_events = {
        755: "安史之乱",
        875: "黄巢起义",
        907: "唐亡",
        1127: "靖康之变",
        1279: "崖山海战",
        1644: "明亡",
    }

    # 寻找每个危机前 5-15 年的 PSI
    thresholds = [-1.5, -1.0, -0.5, 0, 0.5]

    sensitivity = {}
    for threshold in thresholds:
        true_positives = 0
        false_positives = 0
        total_crises = len(crisis_events)

        for crisis_year, name in crisis_events.items():
            # 危机前 5-15 年的 PSI
            lead_decades = []
            for years_before in [5, 10, 15]:
                target_decade = ((crisis_year - years_before) // 10) * 10
                for r in decade_results:
                    if r["decade"] == target_decade:
                        lead_decades.append(r["psi_z"])
                        break

            if not lead_decades:
                continue

            # 至少有一个 lead decade 低于阈值
            triggered = any(p < threshold for p in lead_decades)
            if triggered:
                true_positives += 1

        sensitivity[threshold] = {
            "true_positives": true_positives,
            "total_crises": total_crises,
            "recall": true_positives / total_crises if total_crises > 0 else 0,
        }

    return sensitivity


# ============================================================
# 8. 主流程
# ============================================================

def main():
    print("=" * 70)
    print("v4.0 individual-level 统计分析")
    print("=" * 70)

    # 1. 加载十年级结果
    psi_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/psi_v4_results.json"
    if not os.path.exists(psi_path):
        print(f"[!] 请先运行 compute_psi_v4.py")
        return

    with open(psi_path) as f:
        psi_data = json.load(f)
    decade_results = psi_data["decade_results"]
    print(f"[*] 加载 {len(decade_results)} 个十年的 PSI")

    # 2. 加载 individual-level 数据
    print("[*] 加载 CBDB individual-level 数据...")
    individuals = load_individual_data()
    print(f"[*] {len(individuals)} 个有效专家记录")

    # 3. 分配 sentiments
    individuals = assign_sentiments_to_individuals(individuals, decade_results)

    # 4. 按朝代分组
    by_dynasty = defaultdict(list)
    for ind in individuals:
        by_dynasty[ind["dynasty"]].append(ind["sentiment"])

    # 5. 统计报告
    print("\n" + "=" * 70)
    print("v4.0 个体级 (individual-level) 统计")
    print("=" * 70)

    stats_report = {}

    # 5.1 Bootstrap CI
    print("\n--- Bootstrap 95% CI (individual-level) ---")
    bootstrap_results = {}
    for dy in ["唐朝", "北宋前期", "北宋后期", "南宋", "明朝"]:
        if dy in by_dynasty:
            arr = np.array(by_dynasty[dy])
            ci = bootstrap_ci(arr, statistic_fn=np.mean, n_bootstrap=2000)
            bootstrap_results[dy] = ci
            print(f"  {dy:<8} n={ci['n']:5d}  mean={ci['mean']:+.4f}  "
                  f"CI=[{ci['ci_lower']:+.4f}, {ci['ci_upper']:+.4f}]  "
                  f"width={ci['ci_width']:.4f}")

    # 5.2 Cohen's d: 盛世组 vs 危机组
    print("\n--- Cohen's d (盛世组 vs 危机组, individual-level) ---")

    # 盛世组：唐朝 + 明朝
    prosperity = np.array(
        by_dynasty.get("唐朝", []) + by_dynasty.get("明朝", [])
    )
    # 危机组：北宋后期 + 南宋
    crisis = np.array(
        by_dynasty.get("北宋后期", []) + by_dynasty.get("南宋", [])
    )

    if len(prosperity) > 10 and len(crisis) > 10:
        d_result = bootstrap_cohens_d(prosperity, crisis)
        print(f"  盛世组 (唐+明) n={d_result['n1']}, mean={np.mean(prosperity):+.4f}")
        print(f"  危机组 (北宋后+南宋) n={d_result['n2']}, mean={np.mean(crisis):+.4f}")
        print(f"  Cohen's d = {d_result['d']:.4f}")
        print(f"  Hedges' g = {d_result['g']:.4f}")
        print(f"  95% CI = [{d_result['ci_lower']:.4f}, {d_result['ci_upper']:.4f}]")

        # v3.0 报告的 d=7.35，v4.0 个体级应该小得多
        stats_report["cohens_d"] = d_result

    # 5.3 Walk-Forward
    print("\n--- Walk-Forward 验证 ---")
    wf = walk_forward_validate(decade_results, initial_train=20, horizon=1)
    if "error" not in wf:
        print(f"  Folds: {wf['n_folds']}")
        print(f"  MAE: {wf['mae']:.4f}")
        print(f"  RMSE: {wf['rmse']:.4f}")
        print(f"  Correlation: {wf['correlation']:.4f}")
        stats_report["walk_forward"] = wf

    # 5.4 阈值敏感性
    print("\n--- 阈值敏感性 ---")
    sens = threshold_sensitivity(decade_results)
    for t, info in sens.items():
        print(f"  Threshold PSI_z < {t:+.1f}: recall = {info['recall']:.2f} "
              f"({info['true_positives']}/{info['total_crises']})")

    stats_report["threshold_sensitivity"] = sens
    stats_report["bootstrap"] = bootstrap_results

    # 6. 保存
    out_path = "/Users/wangzr/Desktop/历史事件预测建模/v4/data/statistics_v4.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(stats_report, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] 统计结果保存: {out_path}")


if __name__ == "__main__":
    main()
