# Track 2：数据工程与知识库
**版本**：v1.0 | **日期**：2026-05-28 | **负责人**：Mavis（直接研究）
**对应报告章节**：第9章迭代升级路线图，9.1.2 数据质量提升

---

## 2A. CHGIS 时态地理信息系统集成方案

### 核心问题
北宋 3,564 条专家记录中：
- 94.9%（3,380条）无法分类区域
- 北方仅 19 人（0.5%），南方 165 人（4.6%）

→ 任何基于地理分布的结论都无效。

### CHGIS 数据模型研究

CHGIS（China Historical GIS）由哈佛-北大联合项目维护：
- **数据模型**：时态 Gazetteer（时态地名辞典）
  - 每一个地理实体（府/州/县）有 `start_time` 和 `end_time` 字段
  - 支持查询特定历史时期（如1102年）的行政区划覆盖
- **API 接入**：CHGIS 2020 Release 提供 Shapefile 下载（免费学术使用）
  - 文件：chgis_v6_polygons.shp（含约 30,000+ 历史行政单元）
  - 包含：GEO_NAME（地名）、START_DATE、END_DATE、MODERN_NAME（现代名称）

### 地理编码推理算法

```python
import geopandas as gpd
from shapely.geometry import Point

def infer_geocode(expert_record, chgis_gdf):
    """
    利用 CHGIS 时态 Gazetteer 推断专家地理编码
    expert_record: {'name': str, 'birth_year': int, 'death_year': int, 'place_of_office': str}
    """
    # Step 1: 提取任职地点的现代地名（需 NLP 或字典映射）
    modern_place = place_name_map[expert_record['place_of_office']]
    
    # Step 2: 筛选有效历史时段
    effective_year = (expert_record['birth_year'] + expert_record['death_year']) / 2
    candidate_regions = chgis_gdf[
        (chgis_gdf['START_DATE'] <= effective_year) & 
        (chgis_gdf['END_DATE'] >= effective_year) &
        (chgis_gdf['MODERN_NAME'].str.contains(modern_place, na=False))
    ]
    
    # Step 3: 判断南北（秦岭-淮河分界线：北纬34°）
    if not candidate_regions.empty:
        centroid = candidate_regions.geometry.iloc[0].centroid
        region = '北方' if centroid.y >= 34 else '南方'
        return {'region': region, 'lat': centroid.y, 'lon': centroid.x, 'confidence': 0.7}
    
    # Step 4: 回退策略：使用籍贯（如果有）
    if expert_record.get('native_place'):
        native_place = place_name_map.get(expert_record['native_place'])
        # 再次查询 CHGIS...
    
    return {'region': 'Unknown', 'confidence': 0.1}

def batch_infer_geocode(experts_df, chgis_gdf):
    """批量推理，带进度报告"""
    results = []
    for idx, row in experts_df.iterrows():
        result = infer_geocode(row, chgis_gdf)
        results.append(result)
        if idx % 500 == 0:
            print(f"进度: {idx}/{len(experts_df)}")
    return pd.DataFrame(results)
```

**地名映射表**（部分北宋府州）：
```python
place_name_map = {
    '东京开封府': '开封', '西京河南府': '洛阳', '南京应天府': '商丘',
    '北京大名府': '大名', '永兴军路': '西安', '秦凤路': '天水',
    '京东东路': '济南', '京西南路': '襄阳', '荆湖北路': '江陵',
    '两浙路': '杭州', '福建路': '福州', '成都府路': '成都',
}
```

**预期效果**：
- CHGIS 可覆盖北宋 96 个府/州（北宋全境）
- 预计地理编码成功率：从 5.1%（19+165/3584）提升至 **60-70%**
- 目标：缺失率从 94.9% 降至 **30-40%**

**实施时间线**：约 2-3 周工时（需人工建立地名映射表）

---

## 2B. CPM-KB 隐喻知识库扩展方案

### 核心问题
- CPM-KB 当前仅 **10 条**条目
- CMDAG 学术数据集：**27,989 条**标注隐喻
- 差距：三个数量级
- 目标：4-6 周内扩展至 **1,000 条**

### TSI 半自动框架

**TSI（Textual Semantic Induction）框架**：

```
古籍文本语料
    ↓ CTEXT API / 本地 JSON
候选隐喻抽取（SikuBERT + 规则）
    ↓ 候选集（约 5,000-10,000 条）
人工审核（标注员培训 + 质量控制）
    ↓ 审核后（约 1,000-2,000 条）
结构化编码（CPM-KB 三元组格式）
    ↓ 定期更新
CPM-KB 知识库
```

**步骤 1：候选隐喻自动抽取**
```python
# 基于 SikuBERT 的隐喻候选抽取
from transformers import AutoModel, AutoTokenizer
sikubert = AutoModel.from_pretrained('model/sikubert')
tokenizer = AutoTokenizer.from_pretrained('model/sikubert')

def extract_metaphor_candidates(text, sikubert_model, threshold=0.75):
    """抽取古籍文本中的隐喻候选"""
    # 1. 依存句法分析（使用 spaCy 古文模型）
    doc = nlp(text)
    
    # 2. 概念隐喻模式匹配（基于 Lakoff & Johnson 理论）
    metaphor_patterns = [
        ('国家', '人体'),   # 例："朝廷为身体"
        ('社会', '有机体'), # 例："民为邦本"
        ('时间', '空间'),   # 例："前程"
        ('情感', '天气'),   # 例："心寒"
    ]
    
    candidates = []
    for src, tgt in metaphor_patterns:
        # 3. BERT 相似度匹配
        src_embedding = sikubert_model(**tokenizer(src, return_tensors='pt'))
        # 在文本中搜索高相似度词对
        ...
    return candidates
```

**步骤 2：人工审核工作流**
- 招募 2-3 名历史/中文专业标注员
- 每条标注：源域、目标域、古文例句、历史语境、情感极性
- 标注规范手册（CPM-KB Annotation Guide v1.0）
- 每日标注量：每人 20-30 条，2-3 周完成 1,000 条

**步骤 3：CPM-KB 三元组格式**
```json
{
  "id": "cpm_001",
  "source_domain": "人体",
  "target_domain": "国家",
  "metaphor_label": "朝廷如身体",
  "canonical_form": "身体_为_朝廷",
  "example": "今天下犹一身矣",
  "source_text": "《宋史·司马光传》",
  "period": "北宋中期",
  "sentiment": "negative",
  "psi_weight": 0.8,
  "quality_tag": "verified",
  "_fallback": false
}
```

**CPM-KB 扩展路线图**：
| 阶段 | 条目数 | 时间 | 方法 |
|------|--------|------|------|
| v0.1 | 10 | 当前 | 手动编码 |
| v0.2 | 100 | 1周 | TSI 冷启动 |
| v0.3 | 1,000 | 4-6周 | TSI 扩展 |
| v1.0 | 10,000 | 6-12个月 | 多朝代扩展 |

---

## 2C. CBDB 系统性偏差量化框架

### 三大偏差来源

| 偏差类型 | 表现 | 来源 | 量化指标 |
|----------|------|------|----------|
| **精英偏向** | CBDB 明确包含"更丰富的高官精英男性传记数据" | 史料本身（二十四史、正史） | 高官占比 / 总记录数 |
| **北方政治中心偏向** | 北方仅 0.5%（19人），南方 4.6%（165人） | 首都开封、政治资源集中 | 南北记录比 |
| **时期集中偏向** | 唐宋时期数据占 75%+ | 文献保存率不均匀 | 各时期记录密度 |

### 倾向评分加权（Propensity Score Weighting）

```python
def propensity_score_weighting(df, treatment_var, confounders):
    """
    建模每个单位被记录的概率（逆概率加权）
    df: CBDB 人物记录
    treatment_var: 处理变量（如地区）
    confounders: 混淆变量（如官员品级、时期）
    """
    from sklearn.linear_model import LogisticRegression
    
    # 构建混淆变量矩阵
    X = df[confounders].values
    y = df[treatment_var].values
    
    # 倾向评分模型
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    propensity_scores = model.predict_proba(X)[:, 1]
    
    # 逆概率加权（IPTW）
    weights = np.where(y == 1, 1 / propensity_scores, 1 / (1 - propensity_scores))
    
    # 归一化
    weights = weights / weights.mean()
    
    return weights

# 使用示例
confounders = ['dynasty_period', 'official_rank', 'family_background_score']
df['ipw'] = propensity_score_weighting(df, df['region_north'], confounders)

# 加权后的统计分析
weighted_mean_psi_north = np.average(df['psi'], weights=df['ipw'] * (df['region_north']==1))
weighted_mean_psi_south = np.average(df['psi'], weights=df['ipw'] * (df['region_south']==1))
```

### Seshat 三层质量控制参照

| 层级 | Seshat 机制 | CBDB 适配 |
|------|-------------|-----------|
| L1 数据层 | 来源引用、版本控制 | CBDB 已实现（cbdb_id 溯源） |
| L2 编码层 | 双人独立编码、Krippendorff α ≥ 0.80 | **需引入**（当前无） |
| L3 解释层 | 历史学家复核、不确定性标注 | **需引入**（当前无） |

### 偏差监控仪表盘指标
```
1. 地理覆盖度 = 有地理标签记录数 / 总记录数（目标 ≥ 60%）
2. 性别比 = 男性记录数 / 女性记录数（CBDB 当前约 50:1）
3. 时期分布 = 各朝代记录数 / 预期比例（使用 CHGIS 人口估计作为基准）
4. 精英比例 = 高官（品级 ≥ 3）记录数 / 总记录数（CBDB 当前 > 80%）
5. 记录饱和度 = 实际记录数 / 估计历史人物总数（需外部基准）
```

---

## 执行清单

**P0（1-3个月）**：
- [ ] CHGIS 数据接入 + 地名映射表建立
- [ ] 地理编码推理脚本 → 缺失率 94.9%→40%
- [ ] CPM-KB v0.2（100条，TSI 冷启动）
- [ ] 偏差评估报告（首版）

**P1（3-6个月）**：
- [ ] CPM-KB v0.3（1,000条，全量 TSI 扩展）
- [ ] 倾向评分加权纳入 PSI 计算管线
- [ ] Seshat L2/L3 质量控制机制引入

---

*交叉引用：CBDB 数据特征见 Civilization-Oracle_完整技术文档_v2.3.md §3.1*
