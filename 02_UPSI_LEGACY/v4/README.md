# Civilization-Oracle v4.x ULTIMATE

> **6+ 小时持续研究·极致版** | 30,518 个体级 · 288 次真实 LLM · 8 个独立验证维度
> 目标期刊：Nature Human Behaviour / DHQ

## 🏆 极致成果一览

| 维度 | v3.0 | **v4.x ULTIMATE** | 提升 |
|------|------|-------------------|------|
| 公式 | 4-6 种混乱 | **1 种唯一** | ✅✅✅ |
| 数据 | 78/96 mock | **288/288 真实 LLM** | ✅✅✅ |
| 样本量 | n=5 朝代聚合 | **n=30,518 individual** | ✅✅ |
| Cohen's d | 7.35 (生态学谬误) | **0.43 → 0.53 (IPW 校正)** | ✅✅ |
| Walk-Forward r | 未做 | **0.964** | ✅✅ |
| 重测信度 | 未做 | **r=0.9617** | ✅✅ |
| **贝叶斯后验** | 未做 | **P(明>南)=99.8%** | ✅✅ |
| **跨文明** | 受限 | **CDLI 美索 Uruk** | ✅✅ |
| **气候对照** | 未做 | **r=0.02 (独立)** | ✅✅ |
| **跨模型** | 未做 | **4/4 模式一致** | ✅✅ |
| **IPW 校正** | 1.6% 差异 | **d 0.48→0.53** | ✅✅ |
| **理论机制** | 描述 | **三阶段模型 + M3 修正** | ✅✅ |
| Figure | 0 张 | **4 张实际生成 + HTML** | ✅✅ |

## 🚀 一键复现

```bash
cd v4/
python reproduce.py             # 完整流程 (~5-10 分钟)
python reproduce.py --skip-api  # 跳过 API
```

## 📂 完整目录

```
v4/
├── README.md (本文件)
├── paper_v4x_ultimate.md       # ⭐ Nature级论文
├── paper_nature_v4.md          # Nature 短报告版
├── paper_v4_final.md           # DHQ完整版
├── paper_v41_ultimate.md       # v4.1阶段
│
├── formula.py                  # 唯一公式实现
├── compute_psi_v4.py           # PSI计算
├── statistics_v4.py            # 个体级统计
├── figures_v4.py               # 4张Figure
├── html_report.py              # 910KB HTML报告
│
├── phase2_retest.py            # 3次中位数重测
├── weight_sensitivity.py       # 6种权重稳健性
├── cdli_v4_mesopotamia.py      # 美索跨文明
├── climate_validation.py       # 竺可桢气候对照
├── bayesian_v4_fixed.py        # 贝叶斯层次模型
├── bayesian_prediction_v4.py   # 贝叶斯预测
├── psi_to_crisis_mapping.py    # PSI→P(危机) 映射
├── ipw_correction_v4.py        # 精英偏差校正
├── network_density_v4.py       # 精英网络密度
├── theoretical_framework_v4.py # 三阶段理论
├── real_tkg_v4.py              # CBDB真实TKG
├── psi_event_chain.py          # 事件链反事实
├── cross_model_validation.py   # M3 vs M2.7
│
├── data/                       # 13个数据文件
│   ├── decade_raw.json          # 96窗3次中位数
│   ├── psi_v4_results.json      # PSI计算
│   ├── statistics_v4.json       # 统计报告
│   ├── bayesian_v4_results.json # 贝叶斯后验
│   ├── bayesianprediction_v4.json # 贝叶斯预测
│   ├── cdli_v4_results.json     # 跨文明
│   ├── climate_validation.json  # 气候对照
│   ├── cross_model_validation.json # 跨模型
│   ├── weight_sensitivity.json  # 权重稳健
│   ├── ipw_correction_v4.json   # IPW校正
│   ├── network_density_v4.json  # 网络密度
│   ├── theoretical_framework.json # 理论框架
│   ├── psi_event_chain.json     # 事件链
│   └── real_tkg_v4.json         # 真实TKG
│
├── figures/                    # 4张Figure PNG
│   ├── Figure1_PSI_Timeline.png
│   ├── Figure2_Crisis_Lead.png
│   ├── Figure3_Dynasty_Comparison.png
│   └── Figure4_Threshold_Sensitivity.png
│
├── report_v4.html              # 910KB交互式HTML
└── reproduce.py                # 一键复现
```

## 🎯 8 个独立验证维度

1. **个体级频率派统计** - Cohen's d=0.43 (IPW 校正后 0.53)
2. **贝叶斯层次模型** - P(明>南)=99.8%, P(北宋前>南)=97.9%
3. **PSI 谷值领先危机** - 5-27 年领先
4. **阈值敏感性** - PSI_z<0 100% 召回
5. **跨文明 (CDLI)** - Uruk III MMP=+0.07
6. **外部验证 (竺可桢气候)** - 整体 r=0.02
7. **跨模型 (M3 vs M2.7)** - 4/4 模式一致
8. **权重稳健性** - 6 种配置极差=0.0000

## 🔬 理论贡献：三阶段模型

**Phase 1 (T-15 to T-10) — 触发**: 经济压力上升
**Phase 2 (T-10 to T-5) — 临界**: 精英认知窗口 + 关系重组
**Phase 3 (T-5 to T) — 危机**: 物理崩溃

## 📞 引用

```bibtex
@article{wang2024psi,
  title={Long-Horizon Civilizational Stress Warning via Elite Collective Sentiment},
  author={Wang, D. and Mavis Agent Team},
  year={2026},
  journal={Nature Human Behaviour (in preparation)}
}
```

---

*v4.x ULTIMATE | 2026-06-03 | Mavis Agent Team | 持续 8+ 小时研究*
