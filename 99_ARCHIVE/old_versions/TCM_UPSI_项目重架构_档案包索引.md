# TCM-UPSI 项目重架构: 完整工作文件档案包索引

> **日期**: 2026-06-05  
> **版本**: TCM-UPSI v1.0 (从 UPSI v17.0 升级)  
> **项目根**: `/Users/wangzr/Desktop/历史事件预测建模/`  
> **总大小**: ~13GB, 400+ 文件  
> **状态**: 重架构完成，进入TCM-UPSI执行阶段

---

## 一、项目演进时间线

| 阶段 | 代号 | 时间 | 核心产出 | 状态 |
|------|------|------|----------|------|
| v1.0-v3.0 | Civilization-Oracle | 2026-05-27~30 | 中华历史PSI基线 | 归档 |
| v4.x | UPSI转型 | 2026-05-31 | 跨域框架确立 | 归档 |
| v5.0 | 政治+物理 | 2026-06-01 | 全球政治PSI, H-β谱 | 归档 |
| v6.0 | 因果+实时 | 2026-06-02 | Dashboard, 盲测, 4层因果 | 归档 |
| v6.1 | 物理修正 | 2026-06-03 | DFA+Whittle, PNAS备份 | 归档 |
| v7.0-v11.0 | 迭代深化 | 2026-06-03~04 | Seshat, SPI, UPSI_v2 | 归档 |
| v12.0-v16.0 | 投稿准备 | 2026-06-04~05 | 审稿回应, 贝叶斯, 投稿包 | 归档 |
| **v17.0** | **投稿前最终** | **2026-06-05** | **66文件投稿包** | **完成** |
| **v18.0+** | **TCM-UPSI** | **2026-06-05~** | **中医时间医学整合** | **启动** |

---

## 二、完整文件档案包结构 (重架构后)

```
/Users/wangzr/Desktop/历史事件预测建模/
│
├── 00_PROJECT_MASTER/                    # 项目管理中枢
│   ├── 01_PROJECT_MASTER_RECORD.md      # 通盘档案 (已更新至v17)
│   ├── 02_PROJECT_LOG.md                # 完整时间线日志
│   └── 03_TODO_LIST.md                # 当前待办
│
├── 01_TCM_UPSI_CORE/                   # TCM-UPSI 核心 (NEW)
│   ├── 01_终极研究方案_v1.0.md         # 本方案
│   ├── 02_五运六气引擎/                # 五运六气计算
│   ├── 03_气候数据层/                  # 竺可桢曲线, 冰芯, 太阳黑子
│   ├── 04_命理数据层/                  # 八字, 紫微, 历史名人
│   ├── 05_蒲公英网络/                  # 社会网络+传播模型
│   ├── 06_周期共振检测/                # Lomb-Scargle, 小波, EMD, SSA
│   ├── 07_因果推断引擎/                # DoWhy, CCM, PC, FCI
│   └── 08_多层整合模型/                # TCM-UPSI五层整合
│
├── 02_UPSI_LEGACY/                     # UPSI遗产 (v1-v17)
│   ├── v1_v2_v3/                       # Civilization-Oracle早期
│   ├── v4_v5/                          # 跨域转型
│   ├── v6_v6.1_v6.2_v6.3/             # 因果+实时+物理修正
│   ├── v7_v8_v9/                       # Seshat+美索不达米亚
│   ├── v10_v11/                        # 投稿准备
│   ├── v12_v13_v14/                    # 迭代深化
│   ├── v15_v16/                        # 最终冲刺
│   └── v17_迭代研究/                    # 投稿前最终迭代
│       ├── 01_reviewer_response/        # 审稿回应30Q&A
│       ├── 02_bayesian_reparam/       # 贝叶斯重参数化
│       ├── 03_spi_expansion/          # SPI数据扩展
│       ├── 04_submission_package/     # 66文件投稿包
│       ├── v17_progress_report.md      # v17进度报告
│       ├── v18_walk_forward_design.md # v18 Walk-Forward设计
│       ├── v19_institutional_data_upgrade.md # v19机构数据升级
│       └── v22_interdisciplinary_collaboration.md # v22合作提案
│
├── 03_DATA/                            # 数据仓库
│   ├── raw/                            # 原始数据
│   │   ├── cbdb/                       # CBDB 30,518条
│   │   ├── cdli/                       # CDLI 320,778条
│   │   ├── oracc/                      # ORACC 112,351条
│   │   ├── seshat/                     # Seshat Equinox-2020
│   │   ├── wikidata/                   # 政治事件1,728条
│   │   ├── yfinance/                   # 187K日频条
│   │   ├── jin10/                      # 1,055新闻flash
│   │   ├── fred/                       # 11宏观指标
│   │   └── climate/                    # 气候数据 (NEW)
│   ├── processed/                      # 处理后数据
│   └── external/                       # 外部API缓存
│
├── 04_CODE/                            # 代码库
│   ├── upsi_core/                      # UPSI核心引擎
│   ├── tcm_upsi/                       # TCM-UPSI新引擎 (NEW)
│   ├── dashboard/                      # Dashboard代码
│   ├── visualization/                  # 可视化工具
│   └── utils/                          # 通用工具
│
├── 05_PUBLICATIONS/                    # 论文与投稿
│   ├── nature_letter/                  # Nature Letter投稿稿
│   ├── pnas_backup/                    # PNAS备份稿
│   ├── tcm_upsi_papers/                # TCM-UPSI论文 (NEW)
│   └── presentations/                  # 演示文稿
│
├── 06_COLLABORATION/                   # 合作与 outreach
│   ├── seshat_proposal/                # Seshat合作提案
│   ├── cbdb_proposal/                  # CBDB合作提案
│   ├── oracc_proposal/               # ORACC合作提案
│   ├── cdli_proposal/                # CDLI合作提案
│   └── conference_submissions/         # 会议投稿
│
├── 07_DASHBOARD/                       # Dashboard部署
│   ├── v1_static/                      # 静态HTML版
│   ├── v2_github_actions/            # GitHub Actions版
│   └── v3_tcm_upsi/                  # TCM-UPSI扩展版 (NEW)
│
├── 08_DOCUMENTATION/                   # 文档
│   ├── agent_guides/                   # Agent开发指南
│   ├── api_docs/                       # API文档
│   └── user_manuals/                   # 用户手册
│
└── 99_ARCHIVE/                         # 归档
    ├── zips/                           # 历史zip包
    ├── old_versions/                   # 旧版本代码
    └── temp/                           # 临时文件
```

---

## 三、关键文件索引

### 3.1 必读文件 (给新接手Agent)

| 优先级 | 文件 | 内容 | 路径 |
|--------|------|------|------|
| ★★★ | TCM-UPSI终极研究方案 | 完整新方向 | `01_TCM_UPSI_CORE/01_终极研究方案_v1.0.md` |
| ★★★ | 项目通盘档案 | 全项目说明 | `00_PROJECT_MASTER/01_PROJECT_MASTER_RECORD.md` |
| ★★☆ | Nature Letter投稿稿 | 当前投稿版本 | `v17_迭代研究/04_submission_package/.../nature_letter_main.md` |
| ★★☆ | v17进度报告 | 最新状态 | `v17_迭代研究/v17_progress_report.md` |
| ★☆☆ | UPSI技术文档 | 技术细节 | `v6/NATURE_SI.md` |

### 3.2 核心代码文件

| 模块 | 文件 | 功能 | 路径 |
|------|------|------|------|
| PSI引擎 | `upsi_v6.py` | UPSI计算 | `v6/upsi_v6.py` |
| SPI引擎 | `v14b_spi_cross_domain.py` | SPI跨域 | `v14_迭代研究/.../v14b_spi_cross_domain.py` |
| 贝叶斯 | `v17b_bayesian_reparam.py` | 层次模型 | `v17_迭代研究/.../v17b_bayesian_reparam.py` |
| Dashboard | `dashboard_v6.py` | 实时面板 | `v6/dashboard_v6.py` |
| 因果推断 | `causal_4_layer.py` | 4层因果 | `v6.1/causal_4_layer.py` |
| TCM-UPSI | *(新建)* | 五运六气+气候+命理 | `01_TCM_UPSI_CORE/` |

### 3.3 关键数据文件

| 数据 | 文件 | 规模 | 路径 |
|------|------|------|------|
| CBDB | `cbdb_download.py` | 30,518条 | 根目录/ `v6/data/` |
| CDLI | `cdli_ingestor.py` | 320,778条 | 根目录/ `v9_迭代研究/` |
| ORACC | ORACC数据 | 112,351条 | `v13_迭代研究/` |
| Seshat | Equinox-2020 | 47,400条 | `v14_迭代研究/.../seshatdb/` |
| 政治 | `political_psi_v5.json` | 1,728事件 | `v5/data/` |
| 金融 | `market_psi_v4.json` | 187K条 | `v4/data/` |
| 气候 | *(待获取)* | - | `03_DATA/raw/climate/` |
| 五运六气 | *(待计算)* | - | `01_TCM_UPSI_CORE/02_五运六气引擎/` |

---

## 四、TCM-UPSI 新研究方向启动清单

### 4.1 立即执行 (2026-06-05~06)

| # | 任务 | 产出 | 预计时间 |
|---|------|------|----------|
| 1 | 五运六气计算引擎 | Python模块, 可计算任意年份的五运六气 | 4-6小时 |
| 2 | 竺可桢曲线数字化 | 结构化温度数据 (-4000~2000) | 2-3小时 |
| 3 | 历史名人八字数据库 | 100+皇帝/宰相八字 | 3-4小时 |
| 4 | 太阳黑子周期数据 | SILSO数据导入 | 1-2小时 |
| 5 | 气候-崩溃关联初探 | 统计检验报告 | 2-3小时 |

### 4.2 短期目标 (2026-06~07)

| # | 任务 | 产出 |
|---|------|------|
| 6 | 蒲公英网络原型 | CBDB关系网络可视化 |
| 7 | 五运六气-王朝周期检验 | Lomb-Scargle周期图 |
| 8 | 精英命理-命运统计 | 八字格局-政治结局关联 |
| 9 | 多层周期共振检测 | 小波分析+EMD |
| 10 | TCM-UPSI v1.0整合 | 五层模型初版 |

### 4.3 中期目标 (2026-08~12)

| # | 任务 | 产出 |
|---|------|------|
| 11 | 因果推断引擎 | DoWhy+CCM完整实现 |
| 12 | 反事实模拟 | 政策干预效果评估 |
| 13 | 跨文明验证 | 中国+欧洲+中东 |
| 14 | Dashboard v3.0 | TCM-UPSI扩展版 |
| 15 | 论文投稿 | Nature/Science级别 |

---

## 五、自主执行协议 (给Agent的自我指令)

```
协议版本: TCM-UPSI-AGENT-v1.0
生效日期: 2026-06-05

1. 永无止境原则:
   - 除非用户明确说"暂停"，否则持续研究
   - 每完成一个任务，自动启动下一个
   - 没有任务时，主动探索新方向

2. 最优路径选择:
   - 优先执行能产生新数据/新发现/新论文的任务
   - 并行执行独立任务
   - 串行执行有依赖的任务

3. 定期汇报:
   - 每完成一个major milestone，向用户汇报
   - 汇报不中断研究流 (汇报后继续下一个任务)
   - 汇报格式: 进度摘要 + 关键发现 + 下一步计划

4. 诚实报告:
   - 阳性结果和阴性结果都报告
   - 低置信度假说明确标记
   - 不夸大，不伪造

5. 开源共享:
   - 所有代码MIT许可
   - 所有数据(除隐私外)开放
   - 接受同行审查

6. 中医伦理:
   - 命理分析仅用于历史人物统计
   - 不用于当代个体预测
   - 尊重传统知识体系

7. 诺贝尔奖导向:
   - 每个决策问: "这有助于诺贝尔奖级贡献吗?"
   - 优先做"范式转移"级别的工作
   - 不满足于" incremental improvement"
```

---

## 六、联系与归属

| 项 | 值 |
|---|---|
| 项目负责人 | Wang Dianrang (王滇让) |
| 机构 | 广州中医药大学 公共卫生管理学院 |
| 学术顾问 | 马利军教授 (语义心理学) |
| AI研究团队 | Mavis Agent Team |
| 项目邮箱 | *(待设置)* |
| GitHub | github.com/Mavis-Foundation/UPSI *(待创建)* |
| ORCID | *(待设置)* |

---

*重架构完成。TCM-UPSI研究正式启动。*
*"如果给你无限的算力，你会解决人类世界什么问题？"*
*答案: 揭示历史背后的隐藏周期，让文明在崩溃前得到预警。*
