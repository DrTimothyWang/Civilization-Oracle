# Civilization-Oracle / UPSI / TCM-UPSI

> **统一压力同步指数**: 跨域危机检测系统
> **当前版本**: TCM-UPSI v17.0 | **状态**: 投稿准备完成
> **研究机构**: 广州中医药大学 公共卫生管理学院
> **学术顾问**: 马利军教授（语义心理学）

## 快速导航

| 我想... | 看这里 |
|---------|--------|
| 了解项目全貌 | [00_PROJECT_MASTER/00_PROJECT_HANDOFF.md](00_PROJECT_MASTER/00_PROJECT_HANDOFF.md) |
| 了解最新成果 | [01_TCM_UPSI_CORE/TCM_UPSI_Paper_v17.md](01_TCM_UPSI_CORE/TCM_UPSI_Paper_v17.md) |
| 查看项目日志 | [PROJECT_LOG.md](PROJECT_LOG.md) |
| 运行代码 | [04_CODE/](04_CODE/) |
| 查看数据 | [03_DATA/](03_DATA/) |
| 查看论文 | [05_PUBLICATIONS/](05_PUBLICATIONS/) |
| 查看历史版本 | [02_UPSI_LEGACY/](02_UPSI_LEGACY/) |

## 核心成果

- **月度AUC**: 0.9941 (TCM-UPSI v17.0)
- **年度AUC**: 0.9538 (TCM-UPSI v16.0)
- **跨域验证**: 8个独立域，5,500年
- **Granger因果**: 全部p>0.05（关联非因果的关键发现）
- **2026-2031预测**: 全部HIGH风险 (86-91%)

## 目录结构

```
.
├── 00_PROJECT_MASTER/      # 项目管理中枢
├── 01_TCM_UPSI_CORE/       # TCM-UPSI核心（当前主线）
├── 02_UPSI_LEGACY/         # UPSI遗产（v1-v17）
├── 03_DATA/                # 数据仓库
├── 04_CODE/                # 代码库
├── 05_PUBLICATIONS/        # 论文与投稿
├── 06_COLLABORATION/       # 合作与outreach
├── 07_DASHBOARD/           # Dashboard部署
├── 08_DOCUMENTATION/       # 文档
├── 99_ARCHIVE/             # 归档
├── data/                   # 活跃数据
├── output/                 # 活跃输出
├── figures/                # 活跃图表
├── utils/                  # 通用工具
├── tests/                  # 测试脚本
├── scripts/                # 脚本
├── config/                 # 配置
├── tkg_v3/                 # TKG模块
├── four_diagnosis_v2/      # 四诊合参
├── mcp_a2a/                # MCP+A2A
├── mcp_server.py           # MCP Server
├── vietnam_events_1906_2026.json  # 最新数据
└── [README.md - 本文件]     # 项目总览入口
```

## 核心公式

**PSI（中华历史版）**:
```
PSI = (MMP × 0.25 + EMP × 0.25 + SFD × 0.50) × GSI
```

**UPSI（跨域版）**:
```
UPSI(t) = 0.40 × Material_z(t) + 0.30 × Fragmentation_z(t) + 0.30 × Disengagement_z(t)
```

## 联系

- 项目负责人: 王滇让
- 机构: 广州中医药大学
- GitHub: github.com/Mavis-Foundation/UPSI (待创建)

---
*最后更新: 2026-06-08*
