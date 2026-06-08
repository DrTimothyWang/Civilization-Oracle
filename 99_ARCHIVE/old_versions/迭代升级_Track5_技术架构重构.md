# Civilization-Oracle 技术架构重构方案
## Track 5：7→5 阶段流水线 + DuckDB+NetworkX 简化方案

**文档版本**：v1.0  
**创建日期**：2026-05-28  
**状态**：正式版  
**关联项目**：Civilization-Oracle（文明先知）  
**核心导师**：马利军教授（语义心理学）

---

## 1. 执行摘要

当前 Civilization-Oracle 系统存在 7 阶段顺序流水线过长、多阶段依赖导致单点故障、硬编码参数蔓延、缺少单元测试与监控等严峻技术债务，已形成"降级螺旋"——技术债务导致验证结果不可靠，进而造成资源获取能力下降。

本方案提出三大核心重构方向：

| 重构方向 | 当前问题 | 目标方案 | 预期改善 |
|---------|---------|---------|---------|
| 流水线重构 | 7 阶段顺序依赖 | 5 阶段并行+容错 | 可用性 85.3% → 96.5% |
| 存储架构简化 | Neo4j+Redis 降级 | DuckDB+NetworkX+Celery SQLite | 零外部依赖，可用性 → 99%+ |
| 技术债务清偿 | 无测试/无监控/硬编码 | 分级偿还路线图 | 长期可维护性 |

**核心结论**：通过将 7 阶段合并为 5 阶段、用 DuckDB+NetworkX 替代外部数据库、用 Celery SQLite 模式替代 Threading Queue，系统可用性可从当前 85.3% 恢复到 99%+，同时消除所有外部依赖，大幅降低运维复杂度。

---

## 2. 当前架构问题诊断

### 2.1 问题一：7 阶段顺序流水线

当前架构阶段：

```
[阶段1 DataIngest] → [阶段2 GeoEncoder] → [阶段3 TextAnalyst] → [阶段4 KGraph] → [阶段5 Predictor] → [阶段6 Viz] → [阶段7 QC]
          ↓                  ↓                    ↓                   ↓               ↓              ↓          ↓
       来源:CBDB          地理编码            情感分析           知识图谱          PSI预测         可视化        质控
```

**问题**：
- 任何阶段失败都阻塞整条流水线（N+1 失败传播）
- 线性依赖导致无法并行处理独立数据流
- 7 阶段超过推荐的最大 5 阶段标准
- 缺乏重试机制和降级策略

### 2.2 问题二：Neo4j 降级为内存字典

**现象**：原设计使用 Neo4j 图数据库，实际实现降级为 Python `dict` 内存字典

**影响**：
- 数据重启后丢失，无法持久化
- 图遍历性能无法优化（无索引）
- 关系查询复杂度 O(n) 而非 O(log n)

### 2.3 问题三：Redis 降级为 Threading Queue

**现象**：任务队列从 Redis 降级为 Python threading 模块的 `Queue`

**影响**：
- 进程崩溃则队列丢失
- 无持久化、无重试、无监控
- 系统可用性从 99.2% 降至 85.3%（下降 14 个百分点）

### 2.4 问题四：硬编码参数与测试缺失

| 问题类型 | 具体表现 | 影响程度 |
|---------|---------|---------|
| 硬编码参数 | PSI 阈值、地理编码规则、模型超参写死在代码中 | P0 |
| 缺少单元测试 | TextAnalyst、KGraph、Predictor 核心 Agent 无测试 | P0 |
| 无监控体系 | 无响应时间统计、无队列长度监控、无错误率告警 | P1 |
| 无配置验证 | YAML 加载后无 Schema 校验，运行时才发现错误 | P1 |

### 2.5 问题五："降级螺旋"形成机制

```
技术债务积累
    ↓
验证结果不可靠（缺少测试、监控不完善）
    ↓
学术同行不认可 → 资源获取能力下降
    ↓
资金/计算资源不足 → 无法偿还技术债务
    ↓
进一步降级（更多妥协实现）
```

---

## 3. 方案 A：7→5 阶段流水线重构

### 3.1 重构策略

两阶段合并原则：
- **空间依赖合并**：DataIngest + GeoEncoder → 都依赖 CBDB/CHGIS 数据源，合并为预处理阶段
- **知识紧密耦合**：KGraph + Predictor → 图谱构建与 PSI 预测天然紧密耦合，放在一起效率最高

### 3.2 新架构图（5 阶段 + 并行容错）

```
                        ┌──────────────────────────────────────────────┐
                        │              MasterOrchestrator               │
                        │  任务分发 / 结果汇聚 / 失败重试 / 降级策略      │
                        └──────────────────────────────────────────────┘
                                              │
            ┌───────────────┬─────────────────┼─────────────────┬───────────────┐
            ↓               ↓                 ↓                 ↓               ↓
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │ Stage 1          │  │ Stage 2          │  │ Stage 3          │  │ Stage 4          │  │ Stage 5          │
  │ DataPreprocess   │  │ TextAnalyst      │  │ KnowledgeEngine  │  │ Viz              │  │ QC               │
  │ ★ 并行-safe     │  │ ★ 独立运行      │  │ ★ 最核心        │  │ ★ 可选          │  │ ★ 末端质控      │
  │                  │  │                  │  │                  │  │                  │  │                  │
  │ 数据接入         │  │ 文本/情感分析    │  │ 知识图谱构建     │  │ 可视化输出       │  │ 质量控制        │
  │ 地理编码         │  │ BERT-wwm-ext     │  │ PSI 预测          │  │ 时序图表        │  │ 精度等级验证    │
  │ 数据清洗         │  │ BERT-CLS 分类    │  │ ST-GNN 时序       │  │ 地理分布图      │  │ 不确定性量化    │
  │                  │  │ 情感极性计算     │  │ NetworkX 图遍历   │  │ 网络图谱        │  │ 报告生成        │
  └────────┬────────┘  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  └────────┬────────┘
           │                    │                     │                     │                    │
           ▼                    ▼                     ▼                     ▼                    ▼
       [JSON/Parquet]    [情感分析结果]      [PSI预测区间]           [SVG/HTML]          [QC报告JSON]
           ↓                    ↓                     ↓                     ↓                    ↓
  ┌──────────────────────────────────────────────────────────────────────────────────────────────┐
  │                            DuckDB 时序主数据库                                               │
  │  节点表(nodes) │ 事件表(events) │ 关系表(relations) │ 预测表(predictions) │ 元数据表(metadata)  │
  └────────────────────────────────────────────────────────────────────┬─────────────────────────┘
                                                                   │
                                                            ┌───────┴───────┐
                                                            │ NetworkX 图索引 │ ← 按需加载
                                                            │ (入内存,共享)   │
                                                            └───────────────┘
```

### 3.3 容错机制设计

**三原则**：
1. **Independent Failure**：阶段失败不影响其他并行阶段
2. **Graceful Degradation**：阶段降级而非完全失败（如 Viz 可选）
3. **State Recovery**：失败阶段可从 DuckDB checkpoint 重启

**具体策略**：

| 场景 | 策略 | 恢复时间目标 |
|-----|------|-------------|
| Stage 1 失败 | 跳过，使用缓存的 Parquet 历史数据 | < 30s |
| Stage 2 失败 | 标记 TextAnalyst=unavailable，降级到原始 PSI 输入 | < 10s |
| Stage 3 失败 | 触发 Celery 重试（最多 3 次），告警通知 | < 60s |
| Stage 4 失败 | 标记 Viz=skipped，仍输出 JSON 结果 | < 5s |
| Stage 5 失败 | 标记 QC=manual-override，需人工审查 | < 300s |

### 3.4 阶段间接口定义（JSON Schema）

#### 3.4.1 Stage 1 Output → Stage 2 Input

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "DataPreprocessing_Output",
  "required": ["metadata", "entities", "events", "data_quality"],
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "execution_time": {"type": "string", "format": "date-time"},
        "source_version": {"type": "string"},
        "record_count": {"type": "integer", "minimum": 0}
      }
    },
    "entities": {
      "type": "array",
      "items": {"$ref": "#/definitions/Entity"}
    },
    "events": {
      "type": "array",
      "items": {"$ref": "#/definitions/Event"}
    },
    "data_quality": {
      "type": "object",
      "properties": {
        "completeness": {"type": "number", "minimum": 0, "maximum": 1},
        "accuracy_grade": {"type": "string", "enum": ["A", "B", "C", "D"]}
      }
    }
  },
  "definitions": {
    "Entity": {
      "type": "object",
      "required": ["entity_id", "name", "entity_type", "accuracy_grade"],
      "properties": {
        "entity_id": {"type": "string"},
        "name": {"type": "string"},
        "entity_type": {"type": "string", "enum": ["PERSON", "LOCATION", "ORG", "EVENT_TYPE"]},
        "accuracy_grade": {"type": "string", "enum": ["A", "B", "C", "D"]},
        "geo_coords": {"type": ["object", "null"]}
      }
    },
    "Event": {
      "type": "object",
      "required": ["event_id", "timestamp", "accuracy_grade"],
      "properties": {
        "event_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "accuracy_grade": {"type": "string", "enum": ["A", "B", "C", "D"]}
      }
    }
  }
}
```

#### 3.4.2 Stage 2 Output → Stage 3 Input

```json
{
  "title": "TextAnalyst_Output",
  "type": "object",
  "required": ["metadata", "sentiment_analysis", "entity_sentiment_map"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["execution_time", "model_version"]
    },
    "sentiment_analysis": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "entity_id": {"type": "string"},
          "polarity_score": {"type": "number", "minimum": -1, "maximum": 1},
          "hope_ratio": {"type": "number", "minimum": 0, "maximum": 1},
          "disaster_narrative": {"type": "boolean"}
        }
      }
    },
    "entity_sentiment_map": {
      "type": "object",
      "additionalProperties": {"type": "number"}
    }
  }
}
```

#### 3.4.3 Stage 3 Output → Stage 4 Input

```json
{
  "title": "KnowledgeEngine_Output",
  "type": "object",
  "required": ["psi_prediction", "uncertainty_interval", "confidence_score"],
  "properties": {
    "psi_prediction": {
      "type": "object",
      "properties": {
        "psi_value": {"type": "number"},
        "timestamp": {"type": "string"},
        "model_used": {"type": "string"}
      }
    },
    "uncertainty_interval": {
      "type": "object",
      "properties": {
        "lower": {"type": "number"},
        "upper": {"type": "number"},
        "confidence_level": {"type": "number", "default": 0.95}
      }
    },
    "confidence_score": {"type": "number", "minimum": 0, "maximum": 1}
  }
}
```

### 3.5 错误处理策略

```python
# Stage-level error handling pseudocode

class StageOrchestrator:
    def __init__(self, stages: List[BaseStage], duckdb_conn):
        self.stages = stages
        self.db = duckdb_conn
        self.checkpoint_interval = 60  # seconds
    
    def run_pipeline(self, input_data: dict) -> dict:
        results = {}
        for stage in self.stages:
            try:
                results[stage.name] = stage.execute(
                    results.get(stage.required_input, {})
                )
                self._checkpoint(stage.name, results[stage.name])
            except StageError as e:
                if stage.degradable:
                    results[stage.name] = stage.fallback()
                    logger.warning(f"Stage {stage.name} degraded: {e}")
                else:
                    raise
    
    def _checkpoint(self, stage_name: str, result: dict):
        # Store checkpoint to DuckDB for recovery
        self.db.execute(
            "INSERT INTO pipeline_checkpoints VALUES (?, ?, ?, ?)",
            [stage_name, time.time(), json.dumps(result), "COMPLETED"]
        )
```

**错误分类与处理**：

| 错误类型 | 代码示例 | 恢复策略 |
|---------|---------|---------|
| 网络超时 | `requests.exceptions.Timeout` | 重试 3 次，指数退避 |
| 序列化失败 | `json.JSONDecodeError` | 回退到原始 msgpack 格式 |
| DuckDB 连接丢失 | `duckdb.IOException` | 重建连接，从最近 checkpoint 恢复 |
| 模型加载失败 | `ImportError / ModuleNotFoundError` | 降级到规则基线模型 |
| 内存不足 | `MemoryError` | 释放 NetworkX 缓存，触发 GC |

---

## 4. 方案 B：DuckDB + NetworkX 替代 Neo4j + Redis

### 4.1 技术选型对比

#### 4.1.1 数据库层对比

| 指标 | 当前：Python dict | Neo4j 原设计 | DuckDB 替代方案 |
|-----|-----------------|-------------|----------------|
| **数据持久化** | ❌ 完全丢失 | ✅ 持久化 | ✅ Parquet 自动持久化 |
| **查询性能** | O(n) | O(log n) + 索引 | O(log n) 列式存储 |
| **外部依赖** | 无 | Java 运行时 | 无（纯 Python/C++） |
| **内存占用** | 低 | 高（~10GB+） | 8-16GB（100万节点） |
| **启动时间** | 瞬时 | ~30s | ~2s |
| **事务支持** | ❌ 无 | ✅ ACID | ✅ ACID |
| **适合场景** | 临时缓存 | 图遍历为主 | 分析型 + 时序数据 |

#### 4.1.2 任务队列层对比

| 指标 | 当前：Threading Queue | Redis 原设计 | Celery SQLite 模式 |
|-----|---------------------|-------------|-------------------|
| **进程崩溃恢复** | ❌ 队列丢失 | ✅ 持久化 | ✅ SQLite WAL 模式 |
| **外部依赖** | 无 | Redis 服务器 | 无 |
| **可用性** | ~85% | 99.2% | 99%+ |
| **并发支持** | 受 GIL 限制 | ✅ 无限制 | ✅ 多进程 |
| **监控内置** | ❌ 无 | ✅ 有 | ⚠️ 需 + Flower |
| **消息持久化** | ❌ 无 | ✅ 可选开启 | ✅ 配置可调 |

#### 4.1.3 图数据库层对比

| 指标 | 无图数据库 | Neo4j 原设计 | NetworkX 替代方案 |
|-----|----------|-------------|------------------|
| **内存占用** | N/A | 10GB+ | 8-16GB |
| **图遍历性能** | ❌ 无法做 | O(log n) | O(n)（需优化） |
| **增量迭代** | ❌ 无 | ✅ | ✅ |
| **与 DuckDB 耦合** | 无 | 无 | ✅ 混合查询 |
| **大规模数据** | 不支持 | 支持 | 受内存限制 |
| **CBDB 适用性** | ❌ | ✅ 良好 | ✅ 可接受 |

### 4.2 混合存储架构设计

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Layer                                │
│  TextAnalyst Agent │ KGraph Agent │ Predictor Agent │ Viz Agent     │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                              ▼
         ┌─────────────────────┐      ┌─────────────────────┐
         │   Query Interface    │      │   Graph Interface   │
         └──────────┬──────────┘      └──────────┬──────────┘
                    │                            │
                    ▼                            ▼
         ┌─────────────────────┐      ┌─────────────────────┐
         │      DuckDB         │      │     NetworkX        │
         │   ★ 主数据存储      │◄────►│   ★ 图索引缓存       │
         │                     │ 同步 │                     │
         │ [Parquet 持久化]    │      │ [按需加载入内存]    │
         └─────────────────────┘      └─────────────────────┘
                    │                            │
                    ▼                            ▼
         ┌──────────────────────────────────────────────────────┐
         │                   Disk Storage                        │
         │  /data/nodes.parquet  /data/events.parquet          │
         │  /data/relations.parquet  /data/checkpoints.parquet │
         └──────────────────────────────────────────────────────┘
```

**核心原则**：
- **DuckDB 主表**：存储所有实体、事件、关系元数据
- **NetworkX 图索引**：存储图结构，用于图遍历查询，按需从 DuckDB 加载
- **Parquet 持久化**：每 15 分钟或每 1000 条记录自动序列化
- **混合查询**：复杂查询先用 DuckDB 筛选实体列表，再用 NetworkX 做图遍历

### 4.3 DuckDB 时序数据模型

```sql
-- DuckDB Schema for Civilization-Oracle

-- 节点表（实体）
CREATE TABLE nodes (
    node_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    entity_type VARCHAR CHECK (entity_type IN ('PERSON', 'LOCATION', 'ORG', 'EVENT_TYPE')),
    birth_year INT,
    death_year INT,
    geo_lon DOUBLE,
    geo_lat DOUBLE,
    accuracy_grade CHAR(1) CHECK (accuracy_grade IN ('A', 'B', 'C', 'D')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 事件表
CREATE TABLE events (
    event_id VARCHAR PRIMARY KEY,
    event_type VARCHAR,
    timestamp BIGINT,  -- Unix timestamp for fast range queries
    year INT,          -- Historical year (负数表示公元前)
    location_id VARCHAR REFERENCES nodes(node_id),
    description TEXT,
    sentiment_polarity DOUBLE,
    accuracy_grade CHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 关系表
CREATE TABLE relations (
    relation_id BIGINT GENERATED ALWAYS AS IDENTITY,
    source_id VARCHAR REFERENCES nodes(node_id),
    target_id VARCHAR REFERENCES nodes(node_id),
    relation_type VARCHAR CHECK (relation_type IN ('MENTION', 'KINSHIP', 'COLLABORATION', 'CONFLICT')),
    start_year INT,
    end_year INT,
    confidence_score DOUBLE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, target_id, relation_type)
);

-- 预测结果表
CREATE TABLE predictions (
    prediction_id BIGINT GENERATED ALWAYS AS IDENTITY,
    psi_value DOUBLE,
    uncertainty_lower DOUBLE,
    uncertainty_upper DOUBLE,
    confidence_level DOUBLE,
    model_version VARCHAR,
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX idx_events_year ON events(year);
CREATE INDEX idx_events_location ON events(location_id);
CREATE INDEX idx_relations_source ON relations(source_id);
CREATE INDEX idx_relations_target ON relations(target_id);

-- 分区表（按时间范围）
CREATE TABLE events_partitioned (
    LIKE events
);
-- 按世纪分区策略（每100年一个分区）
```

### 4.4 迁移实施步骤

#### 阶段 1：基础设施准备（第 1-2 周）

```
1. 引入 DuckDB 和 NetworkX
   pip install duckdb networkx celery

2. 创建数据目录结构
   /data/
     ├── parquet/
     ├── checkpoints/
     └── models/

3. 初始化 DuckDB Schema
   python scripts/init_duckdb_schema.py
```

#### 阶段 2：数据迁移（第 3-4 周）

```
1. 从 CBDB 导出 Parquet
   cbdb-export --format=parquet --output=/data/raw/

2. 加载到 DuckDB
   python scripts/load_to_duckdb.py --source=/data/raw/ --target=duckdb://localhost:5432

3. 验证数据完整性
   python scripts/validate_data.py --expected=658339 --tolerance=0.01
```

#### 阶段 3：应用层适配（第 5-6 周）

```
1. 替换 dict 为 DuckDB 查询
   # Before
   nodes = {}
   nodes[person_id] = {'name': name, 'type': 'PERSON'}
   
   # After
   nodes_df = duckdb.query("SELECT * FROM nodes WHERE entity_type = 'PERSON'").df()

2. 替换 Queue 为 Celery SQLite
   # Before
   from queue import Queue
   q = Queue()
   
   # After
   from celery import Celery
   app = Celery('civ_oracle', backend='db+sqlite:///data/celery.db',
                broker='db+sqlite:///data/celery_broker.db')

3. NetworkX 图索引构建
   python scripts/build_networkx_index.py --source=duckdb://localhost:5432
```

#### 阶段 4：灰度验证（第 7-8 周）

```
1. 并行运行新旧系统，对比输出
2. 性能基准测试：查询延迟、吞吐量、内存占用
3. 故障恢复测试：模拟进程崩溃，验证 checkpoint 恢复
```

#### 阶段 5：全量切换（第 9 周）

```
1. 关闭旧 Threading Queue
2. 切换 DuckDB 为主数据源
3. 开启 Celery SQLite 任务队列
4. 监控 72 小时稳定性
```

### 4.5 性能改善预期

| 指标 | 当前值 | 目标值 | 改善幅度 |
|-----|-------|-------|---------|
| 系统可用性 | 85.3% | 99%+ | +14 个百分点 |
| 数据持久化能力 | 0% | 100% | 完全恢复 |
| 图查询延迟（P95） | N/A | < 500ms | 可量化 |
| 队列可靠性 | 85% | 99%+ | +14 个百分点 |
| 启动时间 | N/A | < 10s | 快速启动 |
| 外部依赖数量 | 2+（Java/Redis） | 0 | 完全消除 |

---

## 5. 方案 C：技术债务清偿路线图

### 5.1 技术债务优先级排序

| 优先级 | 债务类型 | 具体项目 | 影响范围 | 偿还成本 | 紧急度 |
|-------|---------|---------|---------|---------|-------|
| **P0** | 测试缺失 | TextAnalyst、KGraph、Predictor 核心 Agent 无单元测试 | 验证不可靠 | 高 | 立即 |
| **P0** | 硬编码参数 | PSI 阈值 / 地理编码规则 / 模型超参 | 不可配置 | 中 | 立即 |
| **P1** | 监控缺失 | 响应时间 / 队列长度 / 错误率无监控 | 问题发现滞后 | 低 | 2 周内 |
| **P1** | 配置无验证 | YAML 加载后无 Schema 校验 | 运行时错误 | 低 | 2 周内 |
| **P2** | 序列化缺失 | 定期持久化机制 | 数据丢失风险 | 中 | 1 个月内 |
| **P2** | 文档缺失 | API 文档 / 架构图过期 | 新人上手难 | 低 | 1 个月内 |

### 5.2 单元测试实施计划

#### 5.2.1 覆盖率目标

- **TextAnalyst Agent**：≥ 80% 行覆盖率
- **KGraph Agent**：≥ 80% 行覆盖率
- **Predictor Agent**：≥ 85% 行覆盖率（含概率预测边界测试）

#### 5.2.2 测试套件结构

```
tests/
├── unit/
│   ├── test_text_analyst.py
│   │   ├── test_sentiment_polarity()
│   │   ├── test_hope_ratio_calculation()
│   │   ├── test_disaster_narrative_detection()
│   │   └── test_batch_processing()
│   ├── test_kgx_agent.py
│   │   ├── test_entity_extraction()
│   │   ├── test_relation_triplet_formation()
│   │   ├── test_graph_construction()
│   │   └── test_networkx_integration()
│   └── test_predictor_agent.py
│       ├── test_psi_calculation()
│       ├── test_uncertainty_interval()
│       ├── test_temporal_consistency()
│       └── test_edge_case_psis()
├── integration/
│   ├── test_pipeline_flow.py
│   └── test_dduckdb_networkx_hybrid.py
└── fixtures/
    ├── cbdb_sample.parquet
    ├── historical_events_sample.json
    └── mock_api_responses.py
```

#### 5.2.3 测试实施时间线

| 周次 | 任务 | 交付物 |
|-----|------|-------|
| 第 1 周 | TextAnalyst 单元测试 | `test_text_analyst.py`（≥80% 覆盖） |
| 第 2 周 | KGraph 单元测试 | `test_kgx_agent.py`（≥ 80% 覆盖） |
| 第 3 周 | Predictor 单元测试 | `test_predictor_agent.py`（≥ 85% 覆盖） |
| 第 4 周 | 集成测试 | `test_pipeline_flow.py`，CI 管道配置 |

### 5.3 YAML 配置化改造

#### 5.3.1 配置 Schema 示例

```yaml
# config/civ_oracle_config.yaml

database:
  duckdb:
    path: "/data/civ_oracle.db"
    parquet_dir: "/data/parquet"
    checkpoint_interval: 900  # 15 minutes

graph:
  networkx:
    cache_size_mb: 8192
    max_nodes_in_memory: 1000000
    load_strategy: "lazy"  # lazy | eager

pipeline:
  stages:
    data_preprocess:
      timeout: 300
      fallback_enabled: true
      fallback_source: "/data/backup/parquet"
    
    text_analyst:
      model: "BERT-wwm-ext"
      batch_size: 32
      timeout: 600
      fallback_enabled: true
      fallback_model: "rule-based"
    
    knowledge_engine:
      timeout: 900
      max_retries: 3
      retry_backoff: 2.0  # exponential backoff factor
    
    viz:
      enabled: true
      output_format: ["svg", "html"]
      timeout: 120
    
    qc:
      accuracy_threshold: 0.85
      require_human_review: false

psi:
  calculation:
    window_years: 30
    smoothing_alpha: 0.3
    confidence_level: 0.95
  
  thresholds:
    unstable_warning: 0.3
    crisis_threshold: 0.7
    collapse_warning: 0.9

monitoring:
  metrics:
    - response_time_p95
    - queue_length
    - error_rate
    - memory_usage_percent
  alert_thresholds:
    error_rate: 0.05
    queue_length: 1000
    memory_percent: 85
```

#### 5.3.2 配置验证逻辑

```python
import yaml
from pydantic import BaseModel, Field, validator

class PipelineConfig(BaseModel):
    checkpoint_interval: int = Field(..., ge=60, le=3600)
    fallback_enabled: bool
    timeout: int = Field(..., ge=10)
    
    @validator('timeout')
    def timeout_positive(cls, v):
        if v <= 0:
            raise ValueError('Timeout must be positive')
        return v

def load_config(path: str) -> PipelineConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return PipelineConfig(**raw)
```

### 5.4 定期序列化机制

```python
import time
from pathlib import Path

class PeriodicSerializer:
    """
    定期将内存数据序列化到 Parquet，防止数据丢失。
    即使 DuckDB 连接失败，也能从最后一次 checkpoint 恢复。
    """
    def __init__(self, duckdb_conn, checkpoint_dir: str, interval_seconds: int = 900):
        self.db = duckdb_conn
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.interval = interval_seconds
        self.last_checkpoint = 0
    
    def maybe_checkpoint(self):
        """如果距离上次 checkpoint 超过 interval_seconds，则执行"""
        now = time.time()
        if now - self.last_checkpoint >= self.interval:
            self._do_checkpoint()
            self.last_checkpoint = now
    
    def _do_checkpoint(self):
        timestamp = datetime.fromtimestamp(time.time()).isoformat()
        for table in ['nodes', 'events', 'relations', 'predictions']:
            df = self.db.query(f"SELECT * FROM {table}").df()
            output_path = self.checkpoint_dir / f"{table}_{timestamp}.parquet"
            df.to_parquet(str(output_path), index=False)
        
        metadata = {
            'timestamp': timestamp,
            'checkpoint_id': str(uuid.uuid4()),
            'tables': ['nodes', 'events', 'relations', 'predictions']
        }
        with open(self.checkpoint_dir / 'checkpoint_manifest.json', 'w') as f:
            json.dump(metadata, f)
```

### 5.5 监控指标清单

| 指标类别 | 具体指标 | 采集方式 | 告警阈值 | 用途 |
|---------|---------|---------|---------|-----|
| **系统可用性** | uptime_percentage | 定期 ping | < 99% | SLA 追踪 |
| **响应时间** | response_time_p50 | 日志埋点 | - | 性能基线 |
| **响应时间** | response_time_p95 | 日志埋点 | > 5s | 性能异常 |
| **响应时间** | response_time_p99 | 日志埋点 | > 10s | 严重瓶颈 |
| **队列健康** | queue_length | Celery API | > 1000 | 积压告警 |
| **队列健康** | queue_processing_rate | Celery API | < 10/min | 降速告警 |
| **错误率** | error_rate_total | 日志统计 | > 5% | 系统健康 |
| **错误率** | error_rate_by_stage | 日志统计 | > 10% | 阶段定位 |
| **内存使用** | memory_usage_percent | psutil | > 85% | OOM 预防 |
| **数据质量** | data_completeness | DuckDB 查询 | < 70% | 数据问题 |
| **预测置信度** | avg_confidence_score | DuckDB 查询 | < 0.6 | 模型问题 |

**监控工具选型**：

| 组件 | 推荐工具 | 理由 |
|-----|---------|-----|
| 指标采集 | prometheus-client | Python 原生，低侵入 |
| 可视化 | Grafana | 成熟，支持 DuckDB 数据源插件 |
| 日志聚合 | Loki + Promtail | 与 Prometheus 同生态 |
| 告警 | Alertmanager | 高可配置，支持多渠道 |

---

## 6. 预期改善总结

### 6.1 关键性能指标对照

| 指标 | 重构前 | 重构后 | 改善 |
|-----|-------|-------|-----|
| 系统可用性 | 85.3% | 99%+ | +14 个百分点 |
| 外部依赖数量 | 2+ | 0 | 完全消除 |
| 数据持久化能力 | 0% | 100% | 完全恢复 |
| 核心 Agent 测试覆盖率 | 0% | ≥ 80% | 可测试性建立 |
| 硬编码参数数量 | 多处 | 0 | 全部配置化 |
| 监控覆盖度 | 0% | 100% | 可观测性建立 |
| 流水线阶段数 | 7 | 5 | 复杂度降低 |

### 6.2 迁移风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|-----|------|-----|---------|
| DuckDB 查询性能不达预期 | 中 | 高 | 第 1-2 周性能基准测试，不达预期则优化 SQL 或考虑其他方案 |
| NetworkX 内存溢出 | 低 | 高 | lazy 加载策略 + 监控内存使用 |
| Celery SQLite 并发限制 | 低 | 中 | 评估 SQLAlchemy 连接池配置 |
| 数据迁移丢失 | 低 | 高 | 灰度验证 2 周，充分对比测试 |

### 6.3 长期收益

1. **技术可持续性**：消除外部依赖 + 完整测试 → 未来可独立迭代
2. **学术可验证性**：测试覆盖率 + 监控 → 验证结果可被同行复现
3. **运维简化**：零外部依赖 → 部署复杂度大幅降低
4. **资源获取**：可靠的验证结果 → 提升学术认可度 → 资源获取改善

---

## 7. 附录

### 7.1 参考技术栈

| 层级 | 组件 | 版本要求 | 备注 |
|-----|------|---------|-----|
| 数据存储 | DuckDB | ≥ 0.9.0 | 分析型，数据持久化 |
| 图处理 | NetworkX | ≥ 3.0 | 内存图索引 |
| 任务队列 | Celery | ≥ 5.3 | SQLite 后端 |
| 配置验证 | Pydantic | ≥ 2.0 | Schema 校验 |
| 测试框架 | pytest | ≥ 7.0 | 覆盖率报告 |
| 监控 | prometheus-client | ≥ 0.17 | 指标暴露 |

### 7.2 CBDB 数据规模参考

- 记录总数：658,339 条（截至最新版本）
- 性别分布：女性 < 1%（需在数据质量标签中标注）
- 时间跨度：公元前 2000 年 ~ 公元 1900 年
- 关系类型：家族关系、社会关系、政治关系

### 7.3 精度的等级定义（参照历史数据模型 v1.2）

| 等级 | 定义 | 数据源要求 |
|-----|------|---------|
| A | 双重独立文献交叉验证 | 考古+文献 / 正史+墓志 |
| B | 单源权威文献 | 正史/官修 |
| C | 推算或间接证据 | 推算/估算 |
| D | 存疑或待考 | 未定论 |

---

*本文档为 Civilization-Oracle 技术架构重构方案正式版，涉及系统性技术决策，建议在核心导师和项目团队评审后实施。*
