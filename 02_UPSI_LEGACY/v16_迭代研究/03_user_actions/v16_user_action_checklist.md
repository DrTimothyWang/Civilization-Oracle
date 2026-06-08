# v16.0 用户操作清单

> **日期**: 2026-06-05  
> **版本**: v16.0  
> **项目**: UPSI (Unified Pressure Synchronization Index)  
> **说明**: 以下操作需要用户手动执行，AI 无法代劳

---

## 操作 1: Dashboard 云部署（预计 15 分钟）

### 目标
将 UPSI Dashboard 部署到 GitHub，实现 7×24 小时自动运行和公网访问。

### 前置条件
- GitHub 账号（免费）
- Git 已安装（`git --version` 检查）
- Python 3.10+ 已安装

### 步骤

```bash
# 1. 进入部署包目录
cd /Users/wangzr/Desktop/历史事件预测建模/v14_迭代研究/04_dashboard_deploy

# 2. 运行部署脚本（交互式引导）
python3 v14d_deploy_script.py

# 3. 按提示操作：
#    - 在 GitHub 上创建新仓库（如 upsi-dashboard）
#    - 复制仓库 URL
#    - 粘贴到脚本提示中
#    - 脚本自动完成：git init → add → commit → push

# 4. 在 GitHub 上启用：
#    - Settings → Actions → General → Allow all actions
#    - Settings → Pages → Source: Deploy from a branch → Branch: gh-pages

# 5. 验证：
#    - 访问 https://yourusername.github.io/upsi-dashboard
#    - 检查 Actions 标签页是否有绿色 ✓ 的运行记录
```

### 验证清单
- [ ] GitHub 仓库已创建
- [ ] 代码已推送
- [ ] GitHub Actions 已启用
- [ ] gh-pages 已启用
- [ ] 公网 URL 可访问
- [ ] Dashboard 显示最新数据

---

## 操作 2: Nature Letter 投稿（预计 30 分钟）

### 目标
向 *Nature* 提交 Letter 投稿。

### 前置条件
- Nature 投稿系统账号（https://mts-nature.nature.com）
- 所有作者同意投稿
- 确认无利益冲突

### 投稿材料清单

| 材料 | 文件路径 | 状态 |
|------|----------|------|
| **Cover Letter** | `v15_迭代研究/04_submission/v15d_cover_letter_nature.md` | ✅ 就绪 |
| **Manuscript** | `v14_迭代研究/05_submission_final/v14_NATURE_MAIN.md` | ✅ 就绪 |
| **Highlighted References** | `v15_迭代研究/04_submission/v15d_highlighted_references.md` | ✅ 就绪 |
| **Author Contributions** | `v15_迭代研究/04_submission/v15d_author_data_code.md` | ✅ 就绪 |
| **Data Availability** | `v15_迭代研究/04_submission/v15d_author_data_code.md` | ✅ 就绪 |
| **Code Availability** | `v15_迭代研究/04_submission/v15d_author_data_code.md` | ✅ 就绪 |
| **SI** | 需从 v6 NATURE_SI.md + v14/v15 新增章节整合 | ⚠️ 需组装 |

### 步骤

```
1. 登录 Nature 投稿系统: https://mts-nature.nature.com
2. 选择 "Submit New Manuscript"
3. 选择文章类型: "Letter"
4. 上传文件:
   - Manuscript: v14_NATURE_MAIN.md (转换为 .docx 或 PDF)
   - Cover Letter: v15d_cover_letter_nature.md
   - Supplementary Information: 整合 SI (见下方)
   - Figures: 从 v4/v5/v6 figures/ 目录选择
5. 填写作者信息
6. 推荐审稿人: Peter Turchin, Stefano Battiston, Marten Scheffer, Didier Sornette, Joseph Henrich
7. 提交
```

### SI 组装指南

SI 需要整合以下章节：
- S1-S17: 来自 `v6/NATURE_SI.md`（v6.0 的 17 节 SI）
- S18: Seshat 验证（新增，参考 `v14_迭代研究/01_seshat_prototype/`）
- S19: SPI 计算和美索验证（新增，参考 `v13_迭代研究/02_spi_burst/`）
- S20: UPSI_v2 四象限分类器（新增，参考 `v14_迭代研究/03_upsi_v2/`）
- S21: Dashboard 架构和部署（新增，参考 `v14_迭代研究/04_dashboard_deploy/`）
- S22: 代码和数据可用性（新增，参考 `v15_迭代研究/04_submission/v15d_author_data_code.md`）

### 验证清单
- [ ] Nature 投稿系统账号已注册
- [ ] Manuscript 已转换为 .docx 或 PDF
- [ ] SI 已整合为单个文件
- [ ] 所有图表已上传
- [ ] 作者信息已填写
- [ ] 推荐审稿人已填写
- [ ] 投稿确认邮件已收到

---

## 操作 3: PNAS 备选投稿（可选，预计 20 分钟）

如果 Nature 拒稿或审稿周期过长，PNAS 是备选方案。

### 步骤
```
1. 登录 PNAS 投稿系统: https://www.pnascentral.org
2. 选择 "Submit New Manuscript"
3. 文章类型: "Research Article"
4. 上传文件: v14_PNAS_MANUSCRIPT.md (转换为 .docx 或 PDF)
5. 提交
```

---

## 操作 4: 本地验证 Dashboard v3（可选，预计 5 分钟）

在部署到 GitHub 前，可以先本地运行增强版 Dashboard。

```bash
cd /Users/wangzr/Desktop/历史事件预测建模/v15_迭代研究/02_spi_dashboard
python3 v15b_dashboard_v3.py --mode=once
# 查看生成的 v15b_dashboard_v3.html
```

---

## 操作 5: 本地体验 UPSI_v2 交互可视化（可选，预计 2 分钟）

```bash
# 直接打开交互式可视化
open /Users/wangzr/Desktop/历史事件预测建模/v15_迭代研究/03_upsi_v2_online/v15c_upsi_v2_interactive.html

# 或嵌入到现有网页
# 复制 v15c_upsi_v2_embed.js 到目标目录
# 在 HTML 中引入: <script src="v15c_upsi_v2_embed.js"></script>
```

---

## 紧急联系

如遇技术问题：
- Dashboard 部署问题：查看 `v14_迭代研究/04_dashboard_deploy/v14d_deployment_report.md` 故障排查章节
- 投稿系统问题：联系 Nature 编辑部 (editorial@nature.com)
- 代码问题：查看各目录下的 README 和 REPORT 文件

---

*操作清单版本: v16.0*  
*项目位置: `/Users/wangzr/Desktop/历史事件预测建模/`*  
*AI 无法执行的操作已明确标注*
