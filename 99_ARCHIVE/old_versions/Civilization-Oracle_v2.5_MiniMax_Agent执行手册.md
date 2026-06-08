Civilization-Oracle v2.5 — Mini Max Agent 团队执行手册
版本：v2.5 轻资产快速推进版 日期：2026-05-30 核心原则：API优先 · 预训练模型 · 云端重算力 · 不造轮子
快速启动（10分钟上手）
# 1. 安装依赖（Mac Mini M4）pip install numpy pandas scipy scikit-learn statsmodels requests pymilvus# 2. 下载CBDB数据curl -L https://github.com/cbdb-project/cbdb_sqlite/releases/latest/download/cbdb.bi.db \  -o data/cbdb.db# 3. 运行四朝数据提取python scripts/cbdb_import.py# 输出：data/tang_psi.json, data/song_n_psi.json, data/song_s_psi.json, data/ming_psi.json# 4. 运行PSI分析python scripts/psi_pipeline.py --dynasty all# 5. 论文辅助写作（API）python scripts/paper_assist.py --section literature
一、技术架构：三层分离
1.1 架构总览
┌─────────────────────────────────────────────────────────────┐│                    本地层（Mac Mini M4 16GB）                  ││  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     ││  │ 数据脚本  │  │ API调用  │  │ 结果整合  │  │ 论文编辑  │     ││  │ Python   │  │ requests │  │ pandas   │  │ Markdown │     ││  └──────────┘  └──────────┘  └──────────┘  └──────────┘     ││        ↑              ↑              ↑              ↑        ││   sqlite3本地      HTTP请求      本地计算       纯文本编辑     │└─────────────────────────────────────────────────────────────┘        ↑                    ↑                    ↑        │                    │                    │┌───────▼────────┐  ┌──────▼───────┐  ┌────────▼─────────┐│   云端API层      │  │  云端向量DB   │  │   云端租算力层     ││ MiniMax/通义/   │  │ Zilliz Cloud │  │ Google Colab     ││ Claude/GPT     │  │ 免费5GB       │  │ T4免费/A100按需  │└────────────────┘  └──────────────┘  └──────────────────┘
1.2 各层职责
层级
做什么
不做什么
本地M4
数据下载、SQLite查询、调用API、整合结果、写论文
不跑大模型、不做训练、不存向量
云端API
所有模型推理（情感/翻译/润色）、Embedding
不存数据、不做训练
云端向量DB
存658K人物向量、语义检索、时序查询
不跑模型
云端租算力
TKG实验、批量处理（极少数场景）
不长期持有
1.3 费用总览
项目
方式
月费用
大模型API（中文）
通义千问 qwen-plus
~¥58
情感分析API
MiniMax M2.5
~¥38
论文润色API
Claude 3.5 Sonnet
~¥50（按需）
向量数据库
Zilliz Cloud 免费层
¥0
Embedding
BGE-M3（本地MPS）
¥0
TKG实验
Colab T4 免费
¥0
月度总计
~¥100-150
v2.5全阶段（3个月）
~¥300-450
二、向量数据库：Zilliz Cloud 免费层
2.1 为什么选Zilliz
658K历史人物 × 1024维向量 ≈ 4.7GB。Zilliz Cloud免费层给5GB存储 + 250万CU/月计算——完全够用且零费用。
方案
免费额度
够不够用
月费
Zilliz Cloud
5GB存储
✅ 够
¥0
Pinecone Starter
2GB存储
⚠️ 紧张
$0-$50
pgvector本地
无限制
16GB内存紧张
¥0
2.2 代码模板
# pip install pymilvusfrom pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection# 连接（免费注册 https://cloud.zilliz.com）connections.connect(    alias=&quot;default&quot;,    uri=&quot;https://your-cluster.zillizcloud.com&quot;,    token=&quot;your-api-key&quot;)# 定义集合fields = [    FieldSchema(name=&quot;id&quot;, dtype=DataType.INT64, is_primary=True, auto_id=True),    FieldSchema(name=&quot;person_id&quot;, dtype=DataType.INT64),  # CBDB人物ID    FieldSchema(name=&quot;name&quot;, dtype=DataType.VARCHAR, max_length=100),    FieldSchema(name=&quot;dynasty&quot;, dtype=DataType.VARCHAR, max_length=50),    FieldSchema(name=&quot;embedding&quot;, dtype=DataType.FLOAT_VECTOR, dim=1024),    FieldSchema(name=&quot;birth_year&quot;, dtype=DataType.INT64),]schema = CollectionSchema(fields, &quot;历史人物向量库&quot;)collection = Collection(&quot;historical_figures&quot;, schema)# 创建索引collection.create_index(&quot;embedding&quot;, {    &quot;metric_type&quot;: &quot;L2&quot;, &quot;index_type&quot;: &quot;IVF_FLAT&quot;, &quot;params&quot;: {&quot;nlist&quot;: 1024}})collection.load()# 语义搜索def search_persons(query_text, top_k=10, dynasty=None):    &quot;&quot;&quot;搜索相似历史人物，支持朝代过滤&quot;&quot;&quot;    embedding = get_embedding(query_text)  # BGE-M3本地生成    expr = f&quot;dynasty == &#39;{dynasty}&#39;&quot; if dynasty else None    results = collection.search(        data=[embedding], anns_field=&quot;embedding&quot;,        param={&quot;metric_type&quot;: &quot;L2&quot;, &quot;params&quot;: {&quot;nprobe&quot;: 128}},        limit=top_k, expr=expr,        output_fields=[&quot;name&quot;, &quot;dynasty&quot;, &quot;birth_year&quot;]    )    return results[0]
2.3 TKG替代方案：三层叠加（零训练）
不用训练TKG-LDG，用以下三层替代：
层级
技术
成本
作用
L1 向量语义搜索
BGE-M3 + Zilliz
¥0
找语义相似的历史人物/事件
L2 API推理
通义千问 qwen-plus
~¥0.003/次
关系推理、因果分析
L3 规则匹配
正则+历史模板
¥0
朝代、官职、学派等结构化查询
效果预估：MRR 25-30%，接近原TKG-LDG的29.63%，但零训练成本。
三、CBDB真实数据接入
3.1 下载与导入
# 下载CBDB SQLite数据库（~500MB）curl -L https://github.com/cbdb-project/cbdb_sqlite/releases/latest/download/cbdb.bi.db \  -o data/cbdb.db# 或者手动下载：https://github.com/cbdb-project/cbdb_sqlite/releases
3.2 四朝人物筛选SQL
import sqlite3import pandas as pdconn = sqlite3.connect(&quot;data/cbdb.db&quot;)# 唐朝筛选df_tang = pd.read_sql(&quot;&quot;&quot;    SELECT         m.c_personid, m.c_name_chn, m.c_birthyear, m.c_deathyear,        m.c_index_year, m.c_index_addr_id,        a.c_latitude, a.c_longitude    FROM biog_main m    LEFT JOIN biog_addr_data bad ON m.c_personid = bad.c_personid         AND bad.c_addr_type_code = 1    LEFT JOIN addr_codes a ON bad.c_addr_id = a.c_addr_id    WHERE (m.c_birthyear BETWEEN 618 AND 907)       OR (m.c_deathyear BETWEEN 618 AND 907)       OR (m.c_index_year BETWEEN 618 AND 907)&quot;&quot;&quot;, conn)# 北宋、南宋、明朝类似，修改年份范围# 北宋: 960-1127, 南宋: 1127-1279, 明朝: 1368-1644
3.3 预期数据量
朝代
预期人数
当前模拟
提升倍数
唐朝
~55,000
50
1100×
北宋
~38,000
50
760×
南宋
~42,000
50
840×
明朝
~95,000
50
1900×
总计
~230,000
190
1210×
3.4 IPW参数校准（基于真实数据自动计算）
# 基于真实CBDB数据自动校准IPW权重def calibrate_ipw_weights(df):    &quot;&quot;&quot;输入CBDB数据框，输出各朝代IPW权重参数&quot;&quot;&quot;        # 1. 职级分布（基于STATUS_DATA关联）    high_rank_pct = len(df[df[&#39;status_rank&#39;] &gt;= 3]) / len(df)    rank_weight = 1 / max(high_rank_pct, 0.01)        # 2. 地理分布（北方vs南方）    north_pct = len(df[df[&#39;latitude&#39;] &gt;= 34]) / len(df)    geo_weight = 1 / max(north_pct, 0.01)        # 3. 学派分布    confucian_pct = len(df[df[&#39;school&#39;] == &#39;confucian&#39;]) / len(df)    school_weight = 1 / max(confucian_pct, 0.01)        return {        &#39;rank_weight&#39;: rank_weight,        &#39;geo_weight&#39;: geo_weight,         &#39;school_weight&#39;: school_weight,        &#39;north_pct&#39;: north_pct,        &#39;high_rank_pct&#39;: high_rank_pct    }
3.5 数据质量预期
朝代
生年完整率
经纬度覆盖率
社会地位记录
唐朝
~65%
~65%
~60%
北宋
~75%
~78%
~70%
南宋
~80%
~82%
~75%
明朝
~85%
~87%
~80%
四、API选型与调用规范
4.1 中文NLP API推荐
用途
推荐API
费用
为什么
主力推理（关系/因果/文言文理解）
通义千问 qwen-plus
~¥58/月
中文理解最强，价格最低
情感分析（古诗文）
MiniMax M2.5
~¥38/月
情感维度丰富
论文润色（英文）
Claude 3.5 Sonnet
~¥50/月（按需）
英文学术写作最强
Embedding
BGE-M3 本地MPS
¥0
免费，效果足够
4.2 API调用模板
import requestsimport time# ========== 通义千问（主力中文推理） ==========def qwen_chat(system_prompt: str, user_prompt: str) -&gt; str:    &quot;&quot;&quot;通义千问API调用&quot;&quot;&quot;    response = requests.post(        &quot;https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation&quot;,        headers={&quot;Authorization&quot;: f&quot;Bearer {DASHSCOPE_API_KEY}&quot;},        json={            &quot;model&quot;: &quot;qwen-plus&quot;,            &quot;input&quot;: {&quot;messages&quot;: [                {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: system_prompt},                {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: user_prompt}            ]},            &quot;parameters&quot;: {&quot;result_format&quot;: &quot;message&quot;, &quot;max_tokens&quot;: 2000}        }    )    return response.json()[&quot;output&quot;][&quot;choices&quot;][0][&quot;message&quot;][&quot;content&quot;]# ========== MiniMax（情感分析） ==========def minimax_sentiment(text: str) -&gt; dict:    &quot;&quot;&quot;MiniMax情感分析&quot;&quot;&quot;    response = requests.post(        &quot;https://api.minimax.chat/v1/text/chatcompletion_v2&quot;,        headers={&quot;Authorization&quot;: f&quot;Bearer {MINIMAX_API_KEY}&quot;},        json={            &quot;model&quot;: &quot;MiniMax-Text-01&quot;,            &quot;messages&quot;: [                {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;分析以下古籍文本的情感，返回JSON格式：{\&quot;polarity\&quot;: -1到1, \&quot;emotions\&quot;: [\&quot;忧\&quot;, \&quot;怒\&quot;等]}&quot;},                {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: text}            ]        }    )    return parse_json_response(response)# ========== 批量调用（带重试和限流） ==========def batch_api_call(items, api_func, max_workers=5, delay=0.2):    &quot;&quot;&quot;批量API调用，带限流和错误重试&quot;&quot;&quot;    from concurrent.futures import ThreadPoolExecutor    results = []    with ThreadPoolExecutor(max_workers=max_workers) as ex:        futures = [ex.submit(api_func, item) for item in items]        for f in futures:            try:                results.append(f.result())            except Exception as e:                results.append(None)                print(f&quot;API错误: {e}&quot;)            time.sleep(delay)    return results
4.3 Embedding：BGE-M3（本地免费）
# BGE-M3在M4 MPS上运行from transformers import AutoTokenizer, AutoModelimport torchdevice = torch.device(&quot;mps&quot; if torch.backends.mps.is_available() else &quot;cpu&quot;)tokenizer = AutoTokenizer.from_pretrained(&quot;BAAI/bge-m3&quot;)model = AutoModel.from_pretrained(&quot;BAAI/bge-m3&quot;).to(device)def get_embedding(text: str) -&gt; list:    &quot;&quot;&quot;生成文本Embedding，本地免费&quot;&quot;&quot;    inputs = tokenizer(text, return_tensors=&quot;pt&quot;, truncation=True, max_length=512)    inputs = {k: v.to(device) for k, v in inputs.items()}    with torch.no_grad():        outputs = model(**inputs)    # Mean pooling    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().tolist()    return embedding
五、论文策略
5.1 目标期刊：Digital Humanities Quarterly (DHQ)
指标
数值
影响因子
0.82
录用率
28%（常规），55%（特刊）
审稿周期
~24周
APC
免费
特刊机会
“AI for DH”特刊（摘要截止2025-09-15）
投稿建议：走常规通道（特刊主题不完全匹配）。
5.2 论文8000词结构
摘要          200词    ← 研究背景+方法+发现+意义1. 引言       1000词   ← 历史预测两大困境+本研究定位+3个RQ2. 文献综述   1200词   ← Cliodynamics+语义心理+历史数据库偏差3. 方法论     2000词   ← PSI指标+贝叶斯推断+IPW+SikuBERT+MSEFF4. 数据       800词    ← CBDB 658K+CHGIS+CPM-KB5. 结果       1500词   ← 四朝PSI 28周期+一致性+IPW效果+敏感性6. 讨论       800词    ← 与Cliodynamics比较+局限+未来7. 结论       300词    ← 核心发现+意义+展望参考文献      40-60篇
5.3 审稿人Top 3质疑及应对
质疑
应对策略
“n=7太小”
四朝并行n=28 + 固定效应模型 + 定位为探索性先导研究
“R²=0.36太低”
转Cohen’s f²=0.56（大效应量）+ 领域基准比较
“历史数据不可靠”
IPW校正 + 7项敏感性分析 + Seshat项目对标
5.4 “四诊合参”英文包装
Multi-Source Evidence Fusion Framework (MSEFF)├── Visual Source (望): GIS spatial density (CHGIS)├── Environmental Source (闻): Climate data (REACHES)├── Textual Source (问): Sentiment analysis (SikuBERT/API)└── Comprehensive Source (切): PSI composite index
5.5 10周投稿时间线
周
任务
1-2
CBDB数据导入 + 四朝PSI计算
3-4
敏感性分析 + 统计补救
5-7
论文扩展至8000词
8-9
内部审稿 + 修改
10
投稿DHQ
六、商业化路径
6.1 三阶段递进
阶段
时间
模式
年收入目标
阶段一
0-6月
政策/博物馆咨询
100万
阶段二
6-18月
API数据服务
500万
阶段三
18-36月
SaaS平台
1500万
6.2 市场优先级
政策研究（文化政策量化评估）— TAM 50亿，政府付费意愿最强
游戏/影视（历史真实性验证）— 客单价最高
文旅数字化（博物馆/景区）— 国家专项资金支持
6.3 竞品空白
所有主要竞品（Seshat、CHGIS、WHG）均为纯学术基金驱动，零商业化。腾讯故宫是大厂文化战略布局，非独立盈利。Civilization-Oracle有机会成为全球首个商业化的历史智能基础设施。
6.4 投资人Pitch
“Civilization-Oracle是中华文明的’数字罗盘’——将五千年历史数据转化为可量化、可预测、可决策的文化智能基础设施。”
关键数据： - 数据壁垒：658K人物 + 全球唯一中华文明语义深度 - 市场空白：竞品零商业化，先发优势 - 轻资产：API优先，月运营成本仅¥100-150
6.5 融资路径
阶段
来源
额度
触发条件
阶段A
政府引导基金/学术转化基金
100-300万
论文投稿
阶段B
天使轮（文化科技专项基金）
500-1000万
首个百万级合同
七、执行检查清单
Week 1-2：数据
☐ CBDB数据库下载导入
☐ 四朝人物筛选SQL执行
☐ IPW参数自动校准
☐ 28周期PSI计算完成
Week 3-4：统计
☐ 跨朝代固定效应模型
☐ 7项敏感性分析
☐ 四朝一致性检验
Week 5-7：论文
☐ 8000词初稿
☐ 文献综述40-60篇
☐ API辅助润色
Week 8-10：投稿
☐ 内部审稿修改
☐ 格式检查
☐ DHQ投稿
本手册由技术架构师、数据工程师、学术策略师、商业化顾问4个专业Agent并行研究后整合。Mini Max Agent团队拥有完整技术决策权，请基于本手册自主迭代、自我优化、定期汇报。