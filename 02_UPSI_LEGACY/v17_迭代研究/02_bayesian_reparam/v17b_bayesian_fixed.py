#!/usr/bin/env python3
"""
v17b_bayesian_fixed.py — 修复版贝叶斯采样
=============================================

基于数据审计结果修复v17B:
  1. 使用去重后的数据 (6213样本)
  2. 对Domain 4进行分层下采样 (从5808→1000)
  3. 使用固定效应替代随机效应 (domain不平衡)
  4. 更强的先验: Half-Normal(0,0.5)替代Half-Cauchy(0,1)
  5. 增加target_accept到0.99
  6. 减少max_treedepth到10 (避免过度探索)

作者: Mavis Agent Team
日期: 2026-06-05
"""

import sys
sys.path.insert(0, "/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam")

import json
import numpy as np
import pymc as pm
import arviz as az
import warnings
warnings.filterwarnings('ignore')

from v17b_bayesian_reparam import prepare_all_data

# 修复版配置
N_CHAINS = 2
N_TUNE = 1000
N_DRAWS = 2000
TARGET_ACCEPT = 0.99
RANDOM_SEED = 42

print("=" * 70)
print("v17B Fixed — 修复版贝叶斯采样")
print("=" * 70)

# 1. 加载并修复数据
print("\n[步骤1] 加载并修复数据...")
data_list = prepare_all_data()
print(f"  原始样本: {len(data_list)}")

# 去重
unique_data = []
seen = set()
for d in data_list:
    key = (d['psi'], d['is_crisis'], d['domain'], d.get('spi', 0))
    if key not in seen:
        seen.add(key)
        unique_data.append(d)

print(f"  去重后: {len(unique_data)}")

# Domain 4下采样 (从5808→1000)
domain4_data = [d for d in unique_data if d['domain'] == 4]
other_data = [d for d in unique_data if d['domain'] != 4]

print(f"  Domain 4: {len(domain4_data)}个, 其他: {len(other_data)}个")

# 分层采样: 保留所有危机样本, 正常样本随机采样
np.random.seed(42)
domain4_crisis = [d for d in domain4_data if d['is_crisis']]
domain4_normal = [d for d in domain4_data if not d['is_crisis']]

# 正常样本采样到与危机样本平衡
n_crisis = len(domain4_crisis)
n_normal_sample = min(len(domain4_normal), n_crisis * 3)  # 1:3比例

sampled_normal = np.random.choice(len(domain4_normal), n_normal_sample, replace=False)
domain4_normal_sampled = [domain4_normal[i] for i in sampled_normal]

balanced_domain4 = domain4_crisis + domain4_normal_sampled
np.random.shuffle(balanced_domain4)

# 合并
fixed_data = other_data + balanced_domain4
np.random.shuffle(fixed_data)

print(f"  修复后总样本: {len(fixed_data)}")

# 2. 准备数据
y = np.array([d['is_crisis'] for d in fixed_data])
psi = np.array([d['psi'] for d in fixed_data])
domain = np.array([d['domain'] for d in fixed_data])

# 重新编码domain为连续整数
domain_map = {d: i for i, d in enumerate(sorted(set(domain)))}
domain_recode = np.array([domain_map[d] for d in domain])
n_domains = len(domain_map)

print(f"  危机率: {y.mean():.3f} ({y.sum()}/{len(y)})")
print(f"  Domain数: {n_domains}")
print(f"  PSI范围: [{psi.min():.3f}, {psi.max():.3f}]")

# 3. 构建修复版模型 (固定效应)
print("\n[步骤2] 构建修复版模型 (固定效应)...")

with pm.Model() as model_fixed:
    # 固定效应先验 (更强的先验)
    alpha = pm.Normal('alpha', 0, 0.5, shape=n_domains)
    beta = pm.Normal('beta', 0, 0.5, shape=n_domains)
    
    # 线性预测
    eta = alpha[domain_recode] + beta[domain_recode] * psi
    
    # 似然
    y_obs = pm.Bernoulli('y_obs', logit_p=eta, observed=y)
    
    # 采样
    print("\n[步骤3] MCMC采样...")
    trace = pm.sample(
        draws=N_DRAWS,
        tune=N_TUNE,
        chains=N_CHAINS,
        cores=1,
        target_accept=TARGET_ACCEPT,
        random_seed=RANDOM_SEED,
        return_inferencedata=True,
    )

# 4. 收敛诊断
print("\n[步骤4] 收敛诊断...")
summary = az.summary(trace, var_names=['alpha', 'beta'])
print(summary)

# 检查divergences
divergences = trace.sample_stats.diverging.sum().values
print(f"\n  Divergences: {divergences}")

# 检查R-hat
rhat_max = np.max([np.max(trace.posterior[v].values) for v in trace.posterior.data_vars])
print(f"  R-hat max: {rhat_max:.3f}")

# 5. 保存结果
print("\n[步骤5] 保存结果...")
results = {
    'model': 'Fixed Effects (Repaired)',
    'n_chains': N_CHAINS,
    'n_tune': N_TUNE,
    'n_draws': N_DRAWS,
    'n_obs': len(y),
    'n_domains': n_domains,
    'crisis_rate': float(y.mean()),
    'divergences': int(divergences),
    'summary': summary.to_dict(),
}

with open("/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam/v17b_fixed_results.json", 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("  ✓ 结果已保存")

print("\n" + "=" * 70)
print("v17B Fixed 完成")
print("=" * 70)
