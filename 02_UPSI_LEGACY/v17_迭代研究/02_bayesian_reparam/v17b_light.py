#!/usr/bin/env python3
"""
v17b_light.py — 轻量级贝叶斯采样验证
=====================================

用途: 快速验证v17B模型可以正常运行 (小参数)
配置:
  - N_CHAINS = 2
  - N_TUNE = 500
  - N_DRAWS = 1000
  - TARGET_ACCEPT = 0.9

预计运行时间: 5-15分钟
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

# 轻量级配置
N_CHAINS = 2
N_TUNE = 500
N_DRAWS = 1000
TARGET_ACCEPT = 0.9
RANDOM_SEED = 42

OUTPUT_DIR = "/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/02_bayesian_reparam"

print("=" * 70)
print("v17B Light — 轻量级贝叶斯采样验证")
print("=" * 70)

# 1. 数据准备
print("\n[步骤1] 数据准备...")
data_list = prepare_all_data()
print(f"  ✓ 总样本: {len(data_list)}")

# 2. 构建简化模型 (仅Model A: PSI-only)
print("\n[步骤2] 构建简化模型 A (PSI-only)...")

# 准备数据
y = np.array([d['is_crisis'] for d in data_list])
psi = np.array([d['psi'] for d in data_list])
domain = np.array([d['domain'] for d in data_list])

n_domains = len(np.unique(domain))
n_obs = len(y)

print(f"  观测数: {n_obs}")
print(f"  域数: {n_domains}")
print(f"  危机率: {y.mean():.3f}")

# 构建模型
with pm.Model() as model_a:
    # 非中心参数化
    mu_alpha = pm.Normal('mu_alpha', 0, 1)
    sigma_alpha = pm.HalfCauchy('sigma_alpha', 1)
    z_alpha = pm.Normal('z_alpha', 0, 1, shape=n_domains)
    alpha = mu_alpha + sigma_alpha * z_alpha
    
    mu_beta = pm.Normal('mu_beta', 0, 1)
    sigma_beta = pm.HalfCauchy('sigma_beta', 1)
    z_beta = pm.Normal('z_beta', 0, 1, shape=n_domains)
    beta = mu_beta + sigma_beta * z_beta
    
    # 线性预测
    eta = alpha[domain] + beta[domain] * psi
    
    # 似然
    y_obs = pm.Bernoulli('y_obs', logit_p=eta, observed=y)
    
    # 采样
    print("\n[步骤3] MCMC采样 (轻量级)...")
    trace = pm.sample(
        draws=N_DRAWS,
        tune=N_TUNE,
        chains=N_CHAINS,
        cores=1,
        target_accept=TARGET_ACCEPT,
        random_seed=RANDOM_SEED,
        return_inferencedata=True,
    )

# 3. 收敛诊断
print("\n[步骤4] 收敛诊断...")
summary = az.summary(trace, var_names=['mu_alpha', 'mu_beta', 'sigma_alpha', 'sigma_beta'])
print(summary)

# 4. 保存结果
print("\n[步骤5] 保存结果...")
results = {
    'model': 'Model A (PSI-only) Light',
    'n_chains': N_CHAINS,
    'n_tune': N_TUNE,
    'n_draws': N_DRAWS,
    'n_obs': n_obs,
    'n_domains': n_domains,
    'crisis_rate': float(y.mean()),
    'summary': summary.to_dict(),
}

with open(f"{OUTPUT_DIR}/v17b_light_results.json", 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"  ✓ 结果已保存: {OUTPUT_DIR}/v17b_light_results.json")

print("\n" + "=" * 70)
print("v17B Light 完成")
print("=" * 70)
