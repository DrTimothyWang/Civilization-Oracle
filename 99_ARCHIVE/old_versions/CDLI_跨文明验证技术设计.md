# Civilization-Oracle 跨文明验证技术设计文档

**版本**: v1.0
**日期**: 2026-05-31
**状态**: 技术可行性验证完成，详细设计待马老师审稿后推进

---

## 摘要

本报告为 Civilization-Oracle v3.0 的跨文明验证阶段（Phase 2）提供技术设计。核心目标是：验证 PSI（心理语义指数）在中华文明之外是否同样具备预测文明稳定性的能力。

**关键发现**：CDLI（Cuneiform Digital Library Initiative）的罗马时期（Roman period）artifact 指的是罗马统治下的美索不达米亚（Parthian/Sassanian时期），楔形文字书写，而非拉丁文材料。因此，CDLI 接入的实际贡献是验证 PSI 在美索不达米亚文明的应用，而非古罗马拉丁文明。

---

## 1 数据源评估

### 1.1 CDLI（Cuneiform Digital Library Initiative）

**接入验证结果**（实测完成）：
- API 端点: `https://cdli.earth/artifacts.json` — ✅ 可访问
- 总 artifact 数: 368,735 条记录
- Inscriptions API: `https://cdli.earth/inscriptions.json` — ✅ 可获取楔形文字 transliteration
- Period 字段结构: `{'id': int, 'sequence': int, 'period': 'name (dates)'}`
- 数据格式: JSON / CSV，支持分页

**CDLI 覆盖的罗马时期**：
- CDLI 的 "Roman" period 指美索不达米亚在罗马统治/影响下的时期（0–640 CE）
- 主要语言: 阿卡德语（楔形文字）+ 少量希腊语
- 楔形文字书写传统: 新巴比伦/波斯/帕提亚/萨珊王朝
- 与中华文明时间重叠窗口：汉朝（206 BCE–220 CE）、唐朝（618–907 CE）

**数据质量评估**：
| 维度 | CDLI | CBDB |
|------|------|------|
| 规模 | 368,735 artifacts | 658,339 人物 |
| 时间粒度 | artifact 级别 | 精确到生卒年 |
| 文本可读性 | ATF transliteration（需亚述学知识） | 古汉语（可直接 NLP） |
| 情感分析成熟度 | 低（无现有模型） | 高（MiniMax API 可用） |
| Period 标注 | ✅ 有结构化 period 字段 | ✅ 有朝代代码 |

### 1.2 古罗马拉丁文替代数据源（补充方案）

如果目标是验证 PSI 在拉丁文材料上的应用，CDLI 不适用。替代数据源：

| 数据源 | 规模 | 语言 | API | 备注 |
|--------|------|------|-----|------|
| PHI (Packhard Humanities Institute) | 3000 万词拉丁文献 | 拉丁文 | 需要机构订阅 | 拉丁文学最全 |
| Perseus Digital Library | 古希腊/罗马文本 | 拉丁文/希腊文 | ✅ 免费 API | 覆盖文学/历史 |
| Brepolis (Brepols Publishers) | 拉丁文全文数据库 | 拉丁文 | 需订阅 | 历史/法律文献 |
| Thomist Archive | 经院哲学文本 | 拉丁文 | ✅ 免费 | 中世纪基督教 |

**推荐方案**：Perseus Digital Library 作为拉丁文 PSI 验证的数据源，优先于 CDLI（如果目标是古罗马拉丁文明）。

### 1.3 CDLI 接入的实际价值

即便 CDLI 不提供拉丁文，其美索不达米亚楔形文字数据对 Civilization-Oracle 仍有重要价值：

1. **跨语言验证**：楔形文字（阿卡德语）是独立于汉语的书写系统，可验证 PSI 的语言无关性
2. **跨文化验证**：美索不达米亚文明（苏美尔/巴比伦/亚述/波斯）与中华文明有完全不同的文化背景，可验证 PSI 的文化无关性
3. **时间对齐**：汉朝与罗马帝国的重叠期（206 BCE–220 CE）允许做跨文明的同期对比

---

## 2 技术架构

### 2.1 跨文明 PSI 统一框架

```
PSI_cross = f(MMP_cross, EMP_cross, SFD_cross, GSI_cross)

其中 MMP_cross: 跨文明语义情绪极性
     EMP_cross: 跨文明专家情绪极性
     SFD_cross: 跨文明专家密度
     GSI_cross: 地理压力指数（需文明专属校准）
```

### 2.2 CDLI 数据接入管线

```
┌──────────────────────────────────────────────────────────────┐
│                    CDLI Data Pipeline                         │
│                                                               │
│  cdli.earth/artifacts.json ──→ Period Filter ──→ Roman Period │
│           │                              (0-640 CE)            │
│           ▼                                                     │
│  cdli.earth/inscriptions.json ──→ ATF → Transliteration       │
│           │                              (阿卡德语楔形文字)    │
│           ▼                                                     │
│  Bilingual Mapping (阿卡德语 → 英语) ──→ Sentiment Analysis   │
│           │                              (MiniMax API)        │
│           ▼                                                     │
│  阿卡德语情感极性 (MMP_acd) ──→ PSI_acd                       │
│           │                                                     │
│           ▼                                                     │
│  美索不达米亚 PSI 时序 (0-640 CE)                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 核心模块设计

#### 模块 A: CDLI Data Ingestor

**功能**: 从 CDLI API 获取 Roman period artifact 及其 inscription

```python
class CDLIDataIngestor:
    """CDLI 数据接入器"""
    BASE_URL = "https://cdli.earth"

    def get_artifacts_by_period(self, period_name: str, limit: int = 1000) -> list:
        """获取指定时期的 artifact 列表"""
        # period_name: "Roman" / "Old Babylonian" / "Middle Babylonian" etc.
        # 返回 [{artifact_id, period, dates_referenced, provenience}, ...]

    def get_inscriptions(self, artifact_ids: list) -> list:
        """批量获取 artifact 对应的 inscription transliteration"""
        # 返回 [{artifact_id, atf, transliteration, transliteration_clean}, ...]

    def map_period_to_window(self, period: str) -> tuple:
        """将 CDLI period 映射为世纪级时间窗口"""
        # e.g., "Roman (ca. 0-640 CE)" → [(0, 100), (100, 200), ..., (600, 640)]
```

#### 模块 B: Bilingual Translation Layer

**功能**: 将阿卡德语 transliteration 转换为英文，再进行情感分析

**方案**：
1. 使用亚述学已有的 ATF → 翻译对照（CDLI 的 inscription 同时标注了 artifact 的 metadata）
2. 若无翻译，采用 GPT-4/Claude 辅助翻译阿卡德语 → 英文
3. MiniMax API 作为情感分析的最终计算层

```python
class AkkadianTranslator:
    """阿卡德语→英语翻译与情感分析"""

    def translate_and_analyze(self, akkadian_text: str) -> dict:
        """
        输入: 阿卡德语 transliteration (ATF format)
        输出: {
            'english': '...',
            'sentiment': float,  # [-1.0, +1.0]
            'confidence': float  # [0.0, 1.0]
        }
        """
        # Step 1: ATF cleanup (去除楔形文字符号标注)
        clean = self.clean_atf(akkadian_text)
        # Step 2: Translate (GPT-4 / Claude)
        english = self.translate(clean, source='akkadian', target='english')
        # Step 3: Sentiment analysis (MiniMax API)
        sentiment = self.analyze_sentiment(english)
        return {'english': english, 'sentiment': sentiment}
```

#### 模块 C: Cross-Civilizational PSI Calculator

**功能**: 计算美索不达米亚 PSI（MMP_acd + SFD_acd + GSI_acd）

```python
class CrossCivilizationalPSI:
    """跨文明 PSI 计算器"""

    def calculate_psi(self, inscriptions: list, period: str) -> dict:
        """
        输入: inscription 列表 + 时间窗口
        输出: {mmp, emp, sfd, gsi, psi, n_experts}
        """
        sentiments = [ins['sentiment'] for ins in inscriptions if ins.get('sentiment') is not None]

        mmp = np.mean(sentiments) if sentiments else 0.0
        emp = mmp  # 本阶段使用 MMP 代理 EMP
        sfd = self.calculate_sfd(sentiments, period)
        gsi = self.get_gsi_mesopotamia(period)  # 美索不达米亚 GSI 校准
        psi = (0.25 * mmp + 0.25 * emp + 0.5 * gsi)

        return {
            'mmp': mmp,
            'emp': emp,
            'sfd': sfd,
            'gsi': gsi,
            'psi': psi,
            'n_inscriptions': len(inscriptions),
            'period': period
        }

    def get_gsi_mesopotamia(self, period: str) -> float:
        """
        美索不达米亚 GSI 校准
        罗马时期美索不达米亚 GSI 取决于：
        - 北方边界压力（安息/萨珊帝国）
        - 内部政治稳定度（帕提亚/萨珊王朝更替）
        - 经济压力（丝绸之路贸易中断）
        """
        gsi_table = {
            'Roman (ca. 0-200 CE)': 0.72,    # 帕提亚帝国压力中等
            'Roman (ca. 200-400 CE)': 0.78,   # 萨珊帝国崛起，边境压力增加
            'Roman (ca. 400-640 CE)': 0.85,   # 晚期罗马崩溃，萨珊扩张
        }
        return gsi_table.get(period, 0.75)
```

---

## 3 实施计划

### Phase 2A: CDLI 美索不达米亚 PSI（1-3 个月）

**目标**: 验证 PSI 在美索不达米亚楔形文字文明的应用

| 步骤 | 工作内容 | 预期产出 | 时间 |
|------|---------|---------|------|
| 2A.1 | CDLI 数据接入器开发 | Python 模块 cdli_ingestor.py | 2 周 |
| 2A.2 | 阿卡德语翻译与情感分析 | 500 条 inscription 情感得分 | 3 周 |
| 2A.3 | 美索不达米亚 PSI 时序计算 | 罗马时期 6 个世纪级窗口 PSI | 2 周 |
| 2A.4 | 与中国 PSI 对比分析 | 跨文明 PSI 对比报告 | 2 周 |

### Phase 2B: 古罗马拉丁文 PSI（3-6 个月）（如果目标扩展）

**目标**: 验证 PSI 在古罗马拉丁文明的应用

| 步骤 | 工作内容 | 预期产出 | 时间 |
|------|---------|---------|------|
| 2B.1 | Perseus Digital Library API 接入 | 拉丁文 inscription 数据库 | 2 周 |
| 2B.2 | 拉丁文情感词典构建 | 拉丁文情感极性词典（500+词） | 4 周 |
| 2B.3 | 拉丁文 PSI 时序计算 | 共和国/帝国/危机期 PSI 时间线 | 3 周 |
| 2B.4 | 三文明 PSI 综合对比 | 中/美索/罗马 PSI 对比报告 | 2 周 |

---

## 4 技术风险与缓解

| 风险 | 等级 | 缓解方案 |
|------|------|---------|
| 阿卡德语翻译质量不稳定 | 高 | 采用 GPT-4 翻译 + 亚述学专家抽样验证（IAA ≥ 0.70） |
| CDLI inscription 覆盖稀疏（罗马时期） | 中 | 分阶段扩大 artifact 范围（Roman → Parthian → Sassanian） |
| GSI 校准缺少历史文献支持 | 中 | 查阅亚述学文献，建立 GSI 校准表 |
| 跨文明 PSI 对比缺乏统计方法 | 中 | 引入 Fisher's exact test 验证 PSI 跨文明稳定性 |
| CDLI API 访问限流 | 低 | 实现缓存机制（Redis）+ 请求退避 |

---

## 5 学术价值评估

**CDLI 美索不达米亚验证的学术贡献**：

1. **跨语言验证**：证明 PSI 不依赖特定书写系统（汉语 vs 楔形文字）
2. **跨文化验证**：美索不达米亚与中华文明有不同的宇宙观、宗教、政治结构；若 PSI 同样有效，说明"专家语义压力预测文明稳定性"具有跨文化普遍性
3. **学术独特性**：目前没有其他工作在做楔形文字语义 PSI 分析，此方向可发表在 Journal of Cuneiform Studies 或 Digital Humanities Quarterly

**古罗马拉丁文验证的额外价值**（Phase 2B）：

- 西方古典文明 PSI 验证，与 Seshat / Cliodynamics 的罗马数据做交叉验证
- 可发表在 Journal of Roman Studies 或 Antiquity

---

## 6 里程碑设定

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| CDLI API 验证完成 | ✅ 完成（2026-05-31） | 本文档 |
| CDLI 数据接入器 | +2 周 | cdli_ingestor.py |
| 首批美索不达米亚 PSI | +5 周 | mesopotamia_psi_results.json |
| 跨文明 PSI 对比报告 | +9 周 | Cross_Civilizational_PSI_Report.md |
| 马老师审稿后确认 Phase 2B | 待定 | — |

---

*本文档由 Civilization-Oracle Agent Team 自动生成*
*验证时间: 2026-05-31*