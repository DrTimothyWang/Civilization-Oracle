# UPSI v15.0 迭代研究报告

> **日期**: 2026-06-05  
> **版本**: v15.0  
> **项目**: UPSI (Unified Pressure Synchronization Index)  
> **状态**: 5/5 轨道全部完成  

---

## 执行摘要

v15.0 实现了 **从研究原型到可部署系统的关键跨越**：

1. **🌍 Seshat 扩展：11 NGA，诚实评估** — 扩展验证揭示根本局限
   - 从 5 NGA 扩展到 11 NGA（+6 新 NGA）
   - 23 个已知危机事件（vs v14a 的 8 个）
   - **召回率 34.8%**（vs v14a 的 66.7%）— 扩展并未改善性能
   - **精确率 5.8%**（与 v14a 持平）
   - **关键发现**：变量完整性是精确率的最强预测因子（Pearson r = 0.706）
   - **教训**：单纯地理扩展不能解决根本的假阳性问题；需要 per-NGA 阈值优化和变量选择

2. **⚡ SPI 金融实时：Dashboard v3** — 突发危机检测集成到实时系统
   - 12 个资产全部成功获取真实 yfinance 数据
   - SPI 计算（τ=5 交易日）+ 四象限分类
   - 检测到 3 个象限转换（JP.N225, UK.FTSE → Gradual Decline; OIL.WTI → Stable recovery）
   - 复合警报级别：WARNING（UPSI = -0.07）
   - 双热图（PSI 低谷 + SPI 尖峰）直观对比

3. **🎛️ UPSI_v2 在线可视化：零依赖交互式** — 浏览器内状态空间探索
   - 纯原生 JavaScript + Canvas 2D（无 Chart.js/Plotly.js 依赖）
   - 交互式相图：时间滑块 + 播放动画 + 悬停提示
   - 象限时间线：颜色编码段 + 点击缩放
   - 可排序警报表：日期/资产/转换/级别
   - 资产网格卡片：当前象限 + PSI/SPI 值
   - 响应式设计：桌面双列 → 移动端单列
   - 离线可用：打开 HTML 文件即可运行

4. **📄 投稿材料完备** — Nature Letter 投稿就绪
   - Cover Letter：突出跨域统一、PSI-SPI 对偶、Seshat 跨方法论验证
   - Highlighted References：17 篇核心文献 + SI 完整性清单
   - Author Contributions / Data Availability / Code Availability
   - 推荐审稿人：Turchin, Battiston, Scheffer, Sornette, Henrich

5. **📊 v14 投稿稿定稿** — 整合 v14 所有成果
   - Nature Letter：8 域验证 + SPI 跨域 + UPSI_v2 + Seshat + Dashboard
   - PNAS 稿件同步更新
   - 审稿人 Q&A：新增 SPI 相关尖锐问题

---

## 1. 轨道完成状态

| 轨道 | 状态 | 关键产出 | 影响 |
|------|------|----------|------|
| **A: Seshat 扩展 11 NGA** | ✅ 完成 | 11 NGA, 23 危机, 34.8% 召回, 5.8% 精确率 | **诚实揭示局限** |
| **B: SPI Dashboard v3** | ✅ 完成 | 12 资产实时 SPI + 四象限 + 3 转换检测 | **实时突发检测就绪** |
| **C: UPSI_v2 在线可视化** | ✅ 完成 | 零依赖交互式 HTML/JS，离线可用 | **浏览器内状态空间探索** |
| **D: 投稿材料** | ✅ 完成 | Cover Letter + References + Author/Data/Code | **Nature 投稿就绪** |
| **E: v14 投稿稿定稿** | ✅ 完成 | Nature/PNAS/Q&A 全部更新 | **投稿就绪** |

---

## 2. Track A: Seshat 扩展 — 详细成果

### 2.1 扩展策略

从 v14a 的 5 个 NGA 扩展到 11 个，新增 6 个：
- Lowland Andes (South America, Tiwanaku collapse)
- Big Island Hawaii (Oceania, state formation) — **排除**（仅 9 行，<15 行最小值）
- Kansai (East Asia, Yamato state)
- Deccan (South Asia, Maurya decline)
- Paris Basin (Europe, Black Death, Revolution)
- Kachi Plain (Indus region)
- Niger Inland Delta (Africa)
- Cambodian Basin (Southeast Asia, Angkor)
- Korea (East Asia)
- Greece (Europe, classical collapse)

### 2.2 关键结果

| 指标 | v14a (5 NGA) | v15a (11 NGA) | 变化 |
|------|--------------|---------------|------|
| **召回率** | 66.7% | **34.8%** | **−31.9 pp** |
| **精确率** | 5.8% | **5.8%** | **0.0 pp** |
| **F1** | 10.6% | **10.0%** | **−0.6 pp** |
| 危机事件 | 8 | **23** | +15 |
| NGA | 5 | **11** | +6 |

### 2.3 为什么扩展没有改善？

**原始 5 NGA 是"幸运样本"**：Upper Egypt、Latium、Middle Yellow River Valley 都是数据最完整、危机最明确的 NGA。新增的 6 个 NGA 大多：
- 数据稀疏（Deccan、Cambodian Basin、Cuzco 观测数 <30%）
- 危机类型不匹配（Paris Basin 的法国大革命是政治转型，非结构性崩溃）
- 外部冲击主导（西班牙征服导致 Valley of Oaxaca 崩溃，非内部压力）

### 2.4 最强预测因子：变量完整性

| NGA | 变量完整性 | 召回率 | 精确率 |
|-----|-----------|--------|--------|
| Niger Inland Delta | 100% | 0% | **25%** |
| Upper Egypt | 85% | 100% | 10.5% |
| Latium | 70% | 100% | 8% |
| Deccan | 45% | 0% | 0% |
| Cambodian Basin | 30% | 0% | 0% |

**Pearson r (变量完整性 vs 精确率) = 0.706** — 强正相关

### 2.5 诚实结论

> "单纯地理扩展不能解决根本的假阳性问题。v15a 的教训是：**数据质量 > 地理多样性**。未来工作应聚焦于 per-NGA 阈值优化和变量选择，而非进一步地理扩张。"

---

## 3. Track B: SPI Dashboard v3 — 详细成果

### 3.1 架构增强

```
DataFetcher → PSIEngine → SPIEngine → AlertSystem → Renderer
                          ↓
                    QuadrantClassifier
                          ↓
                    DualHeatmap (PSI + SPI)
                          ↓
                    PhasePortrait (Top 5 资产)
```

### 3.2 实时测试结果

| 资产 | PSI | SPI | 象限 | 警报 |
|------|-----|-----|------|------|
| VIX | -0.96 | 0.42 | 🟡 Gradual Decline | 是 |
| BR.BVSP | -0.86 | 0.31 | 🟡 Gradual Decline | 是 |
| GOLD | -0.60 | 0.18 | 🟡 Gradual Decline | 是 |
| JP.N225 | -0.12 | 0.85 | 🟠 Sudden Crisis | **转换检测** |
| UK.FTSE | -0.08 | 0.72 | 🟠 Sudden Crisis | **转换检测** |
| OIL.WTI | +0.15 | -0.05 | 🟢 Stable | **恢复检测** |

### 3.3 关键设计决策

- **ΔGSI 替代**：金融单资产无地理分散度 → 用跨资产相关性崩溃替代
- **动态阈值**：每资产基于自身 PSI/SPI 分布计算阈值
- **τ=5 交易日**：适用于金融突发检测
- **双热图**：PSI 低谷（左）+ SPI 尖峰（右）直观对比

---

## 4. Track C: UPSI_v2 在线可视化 — 详细成果

### 4.1 技术选择

| 选项 | 选择 | 理由 |
|------|------|------|
| Chart.js | ❌ 未选 | 需要 CDN，增加依赖 |
| Plotly.js | ❌ 未选 | 体积太大 (>3MB) |
| **原生 JS + Canvas 2D** | ✅ **选中** | 零依赖、<500KB、精确控制象限背景、轨迹线、时间编码点大小 |

### 4.2 交互功能

| 功能 | 实现 |
|------|------|
| 相图 | Canvas 散点，象限背景色，轨迹线，悬停提示 |
| 时间滑块 | 范围输入 + 播放/暂停按钮，动画遍历历史 |
| 点大小 | 时间近大远小（recency-encoded） |
| 时间线 | 水平条形图，颜色编码象限，点击缩放 |
| 警报表 | 可排序 HTML 表格，列：日期/资产/从/到/级别/持续时间 |
| 资产网格 | CSS Grid 卡片，颜色边框，悬停提升效果 |
| 响应式 | CSS Grid/Flexbox，桌面双列 → 移动端单列 |

### 4.3 颜色方案

| 象限 | 颜色 | Hex |
|------|------|-----|
| 🟢 Stable | 绿色 | #28a745 |
| 🟡 Gradual Decline | 黄色 | #ffc107 |
| 🟠 Sudden Crisis | 橙色 | #fd7e14 |
| 🔴 Accelerating Collapse | 红色 | #dc3545 |

---

## 5. Track D: 投稿材料 — 详细成果

### 5.1 Cover Letter 亮点

- **跨域统一**：同一三维度指数结构在 8 个独立域有效
- **PSI-SPI 对偶**：从单指标到状态空间（位置+速度）
- **Seshat 跨方法论验证**：专家编码结构变量 vs 文本/市场/事件
- **7 个反直觉发现**：VIX 领先 17 天、黄金滞后 1 天、无 Granger 因果、欧洲三强震源
- **政策相关性**：零成本云部署 Dashboard，央行/监管者可用
- **诚实局限**：小样本、精英偏差、近随机 ROC AUC、低 Seshat 精确率

### 5.2 推荐审稿人

1. **Peter Turchin** (UConn) — cliodynamics/Seshat 创始人
2. **Stefano Battiston** (UZH) — 系统性风险/金融网络
3. **Marten Scheffer** (Wageningen) — 临界转变早期预警
4. **Didier Sornette** (ETH Zurich) — 金融泡沫/危机预测
5. **Joseph Henrich** (Harvard) — 文化演化

### 5.3 SI 完整性

22 个 SI 章节全部完成，涵盖：
- 域操作化 (S1)
- 数据处理管道 (S2-S6)
- 统计方法 (S7-S9)
- 机器学习 (S10-S12)
- 物理指标 (S13)
- 跨文明分析 (S14)
- 网络中心性 (S15)
- 因果识别 (S16-S17)
- Seshat 验证 (S18)
- SPI 框架 (S19)
- UPSI_v2 (S20)
- Dashboard (S21)
- 代码/数据可用性 (S22)

---

## 6. 关键数字对比

| 指标 | v14.0 | v15.0 | 变化 |
|------|-------|-------|------|
| Seshat NGA | 5 | **11** | +6 |
| Seshat 危机事件 | 8 | **23** | +15 |
| Seshat 召回率 | 66.7% | **34.8%** | −31.9 pp |
| Seshat 精确率 | 5.8% | **5.8%** | 0 pp |
| Dashboard 资产 | 20 | **12 (SPI 增强)** | 功能增强 |
| 象限转换检测 | 无 | **3** | 新增 |
| 在线可视化 | 静态 PNG | **交互式 HTML/JS** | 范式升级 |
| 投稿状态 | 稿件就绪 | **投稿材料完备** | 可提交 |

---

## 7. 理论贡献总结

### 7.1 v15.0 新增贡献

| 贡献 | 类型 | 影响 |
|------|------|------|
| Seshat 扩展诚实评估 | **数据** | 揭示"地理多样性 ≠ 性能提升"；变量完整性才是关键 |
| SPI 实时 Dashboard | **工程** | 突发危机检测集成到实时监控系统 |
| UPSI_v2 交互可视化 | **系统** | 浏览器内状态空间探索，零依赖，离线可用 |
| 投稿材料完备 | **传播** | Nature Letter 投稿就绪 |

### 7.2 关键教训

1. **数据质量 > 地理多样性**：Seshat 扩展证明单纯增加 NGA 不能改善精确率
2. **变量完整性 r=0.706**：最强预测因子，指导未来数据收集
3. **SPI 实时可行**：τ=5 交易日适用于金融突发检测
4. **零依赖可视化**：原生 JS + Canvas 足以构建专业级交互式科学可视化

---

## 8. 下一步计划（v16.0 预览）

| 轨道 | 目标 | 预计时间 | 前置条件 |
|------|------|----------|----------|
| **v16A: Seshat 精度优化** | Per-NGA 阈值 + 变量选择，目标精确率 >15% | 2-3 周 | v15A 完成 ✅ |
| **v16B: Dashboard 实际部署** | 用户执行部署脚本，验证 7×24 运行 | 1 周 | v15B+C 完成 ✅ |
| **v16C: Nature 投稿** | 提交 Nature Letter，准备审稿回应 | 1-2 周 | v15D 完成 ✅ |
| **v16D: 贝叶斯 SPI** | PyMC 3 层模型：PSI + SPI 联合推断 | 2-3 周 | v11 贝叶斯完成 ✅ |
| **v16E: 跨域 SPI 验证** | 中国历史原生 SPI（非代理）、古罗马 | 2-3 周 | v15A 完成 ✅ |

---

## 9. 文件清单

### v15.0 交付文件

| 文件 | 路径 | 大小 | 说明 |
|------|------|------|------|
| Seshat 扩展引擎 | `v15_迭代研究/01_seshat_expansion/v15a_seshat_expansion.py` | 25.4 KB | 11 NGA PSI 计算 |
| Seshat 扩展结果 | `v15_迭代研究/01_seshat_expansion/v15a_seshat_expanded_results.json` | 291 KB | 535 时间序列记录 |
| 精确率分析 | `v15_迭代研究/01_seshat_expansion/v15a_precision_analysis.py` | 10.9 KB | 变量完整性相关性 |
| 精确率结果 | `v15_迭代研究/01_seshat_expansion/v15a_precision_analysis.json` | 7.7 KB | 累积指标 |
| 扩展报告 | `v15_迭代研究/01_seshat_expansion/v15a_expansion_report.md` | 20 KB | 完整评估 |
| SPI Dashboard 模块 | `v15_迭代研究/02_spi_dashboard/v15b_spi_dashboard.py` | 21.3 KB | SPI 计算 |
| Dashboard v3 | `v15_迭代研究/02_spi_dashboard/v15b_dashboard_v3.py` | 52.6 KB | 增强版主控 |
| Dashboard v3 HTML | `v15_迭代研究/02_spi_dashboard/v15b_dashboard_v3.html` | 20.7 KB | 样本输出 |
| Dashboard 数据 | `v15_迭代研究/02_spi_dashboard/v15b_dashboard_data.json` | 6.6 KB | 12 资产结果 |
| SPI 集成报告 | `v15_迭代研究/02_spi_dashboard/v15b_integration_report.md` | 15.5 KB | 架构+结果 |
| 交互可视化 HTML | `v15_迭代研究/03_upsi_v2_online/v15c_upsi_v2_interactive.html` | 46.5 KB | 零依赖交互式 |
| 嵌入 JS 模块 | `v15_迭代研究/03_upsi_v2_online/v15c_upsi_v2_embed.js` | 27.8 KB | 可复用模块 |
| 演示数据 | `v15_迭代研究/03_upsi_v2_online/v15c_demo_data.json` | 16.5 KB | 30 天合成数据 |
| 可视化报告 | `v15_迭代研究/03_upsi_v2_online/v15c_visualization_report.md` | 16.9 KB | 技术选择 |
| Nature Cover Letter | `v15_迭代研究/04_submission/v15d_cover_letter_nature.md` | 4 KB | 投稿信 |
| Highlighted References | `v15_迭代研究/04_submission/v15d_highlighted_references.md` | 6.9 KB | 17 篇文献 |
| Author/Data/Code | `v15_迭代研究/04_submission/v15d_author_data_code.md` | 4.3 KB | 贡献+可用性 |
| Nature 投稿稿 | `v14_迭代研究/05_submission_final/v14_NATURE_MAIN.md` | ~50 KB | v14 定稿 |
| PNAS 投稿稿 | `v14_迭代研究/05_submission_final/v14_PNAS_MANUSCRIPT.md` | ~26 KB | v14 定稿 |
| 审稿人 Q&A | `v14_迭代研究/05_submission_final/v14_reviewer_QA.md` | ~43 KB | v14 定稿 |
| **本报告** | `v15_迭代研究/v15_PROGRESS_REPORT.md` | — | 迭代总结 |

---

## 10. 项目里程碑

| 版本 | 日期 | 核心突破 | 状态 |
|------|------|----------|------|
| v6.0 | 2026-06-03 | 因果识别 (HAC+PSM) + 实时 Dashboard | ✅ |
| v9.0 | 2026-06-04 | 美索 PSI 多时期 (6/8=75%) | ✅ |
| v11.0 | 2026-06-04 | 贝叶斯层次模型 + 高压繁荣悖论 | ✅ |
| v12.0 | 2026-06-04 | Genre 加权 + 子窗口检验 (6/8 不变) | ✅ |
| v13.0 | 2026-06-04 | **SPI 理论框架 + Seshat 研究 + Dashboard v2** | ✅ |
| v14.0 | 2026-06-05 | **Seshat 原型 + SPI 跨域 + UPSI_v2 + Dashboard 部署 + 投稿定稿** | ✅ |
| **v15.0** | **2026-06-05** | **Seshat 扩展评估 + SPI Dashboard v3 + UPSI_v2 在线可视化 + 投稿材料完备** | **✅** |

---

*报告生成: 2026-06-05  
*项目位置: `/Users/wangzr/Desktop/历史事件预测建模/`  
*下一迭代: v16.0（Seshat 精度优化 + Dashboard 实际部署 + Nature 投稿 + 贝叶斯 SPI）
