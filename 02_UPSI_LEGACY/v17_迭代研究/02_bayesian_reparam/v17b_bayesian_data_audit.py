#!/usr/bin/env python3
"""
v17b_bayesian_data_audit.py — 数据审计与修复
=============================================

诊断v17B贝叶斯采样divergences问题的根本原因:
  1. 检查6832样本的数据质量 (重复、异常值、分布)
  2. 分析domain分布是否极度不平衡
  3. 检查PSI值范围是否合理
  4. 提出修复方案

作者: Mavis Agent Team
日期: 2026-06-05
"""

import sys
sys.path.insert(0, "/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam")

import json
import numpy as np
from collections import Counter, defaultdict

from v17b_bayesian_reparam import prepare_all_data

print("=" * 70)
print("v17B 数据审计与修复")
print("=" * 70)

# 1. 加载数据
print("\n[步骤1] 加载数据...")
data_list = prepare_all_data()
print(f"  总样本: {len(data_list)}")

# 2. 基本统计
print("\n[步骤2] 基本统计...")

y = np.array([d['is_crisis'] for d in data_list])
psi = np.array([d['psi'] for d in data_list])
domain = np.array([d['domain'] for d in data_list])
spi = np.array([d.get('spi', np.nan) for d in data_list])

print(f"  危机率: {y.mean():.3f} ({y.sum()}/{len(y)})")
print(f"  PSI范围: [{psi.min():.3f}, {psi.max():.3f}]")
print(f"  PSI均值: {psi.mean():.3f}, 标准差: {psi.std():.3f}")
print(f"  SPI非NaN: {np.sum(~np.isnan(spi))}/{len(spi)}")

# 3. Domain分布
print("\n[步骤3] Domain分布...")
domain_counts = Counter(domain)
for dom, count in sorted(domain_counts.items()):
    crisis_count = sum(1 for d in data_list if d['domain'] == dom and d['is_crisis'])
    print(f"  Domain {dom}: {count}样本, 危机{crisis_count}个 ({crisis_count/count*100:.1f}%)")

# 4. 检查重复
print("\n[步骤4] 检查重复样本...")
unique_samples = set()
duplicates = []
for i, d in enumerate(data_list):
    key = (d['psi'], d['is_crisis'], d['domain'], d.get('spi', 0))
    if key in unique_samples:
        duplicates.append(i)
    else:
        unique_samples.add(key)

print(f"  唯一样本: {len(unique_samples)}")
print(f"  重复样本: {len(duplicates)}")

# 5. PSI分布分析
print("\n[步骤5] PSI分布分析...")
psi_crisis = psi[y == 1]
psi_normal = psi[y == 0]

print(f"  危机组PSI: 均值={psi_crisis.mean():.3f}, 标准差={psi_crisis.std():.3f}")
print(f"  正常组PSI: 均值={psi_normal.mean():.3f}, 标准差={psi_normal.std():.3f}")

# 6. 异常值检测
print("\n[步骤6] 异常值检测 (IQR方法)...")
q1, q3 = np.percentile(psi, [25, 75])
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr
outliers = np.sum((psi < lower) | (psi > upper))
print(f"  Q1={q1:.3f}, Q3={q3:.3f}, IQR={iqr:.3f}")
print(f"  异常值范围: [{lower:.3f}, {upper:.3f}]")
print(f"  异常值数量: {outliers}/{len(psi)} ({outliers/len(psi)*100:.1f}%)")

# 7. 问题诊断
print("\n[步骤7] 问题诊断...")

problems = []

if len(duplicates) > 0:
    problems.append(f"重复样本: {len(duplicates)}个")

if y.mean() < 0.05 or y.mean() > 0.95:
    problems.append(f"类别极度不平衡: 危机率={y.mean():.3f}")

if psi.std() < 0.1:
    problems.append(f"PSI变化范围过小: std={psi.std():.3f}")

if len(domain_counts) < 3:
    problems.append(f"Domain数量过少: {len(domain_counts)}个")

max_dom_ratio = max(domain_counts.values()) / len(data_list)
if max_dom_ratio > 0.8:
    problems.append(f"Domain极度不平衡: 最大domain占比={max_dom_ratio:.1%}")

if problems:
    print("  发现的问题:")
    for p in problems:
        print(f"    ⚠️ {p}")
else:
    print("  未发现明显数据问题")

# 8. 修复建议
print("\n[步骤8] 修复建议...")

print("""
  [建议1] 数据去重
    - 移除重复样本, 保留唯一值
    - 预计减少至 ~{} 个样本

  [建议2] 类别平衡
    - 当前危机率={:.3f}
    - 如<0.1, 考虑过采样或调整先验

  [建议3] PSI标准化
    - 当前PSI范围 [{:.3f}, {:.3f}]
    - 建议标准化到 [-3, 3] 范围

  [建议4] 模型简化
    - 如domain不平衡, 考虑固定效应替代随机效应
    - 或使用更弱的domain先验

  [建议5] 更强的先验
    - Half-Cauchy(0,1) → Half-Normal(0,0.5)
    - 或增加target_accept到0.99
""".format(len(unique_samples), y.mean(), psi.min(), psi.max()))

# 9. 导出修复后的数据
print("\n[步骤9] 导出修复后的数据...")

# 去重
unique_data = []
seen = set()
for d in data_list:
    key = (d['psi'], d['is_crisis'], d['domain'], d.get('spi', 0))
    if key not in seen:
        seen.add(key)
        unique_data.append(d)

print(f"  去重后样本: {len(unique_data)}")

# 保存
with open("/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam/v17b_data_audit.json", 'w') as f:
    json.dump({
        'original_count': len(data_list),
        'unique_count': len(unique_data),
        'duplicate_count': len(duplicates),
        'crisis_rate': float(y.mean()),
        'psi_range': [float(psi.min()), float(psi.max())],
        'psi_mean': float(psi.mean()),
        'psi_std': float(psi.std()),
        'domain_distribution': {int(k): v for k, v in domain_counts.items()},
        'problems': problems,
        'unique_data': unique_data,
    }, f, indent=2)

print("  ✓ 审计结果已保存")

print("\n" + "=" * 70)
print("v17B 数据审计完成")
print("=" * 70)
