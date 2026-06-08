Civilization-Oracle v2.5 — Mini Max Agent 团队研究指令（轻资产快速推进版）
发件：王滇让（项目负责人） 收件：Mini Max 桌面 AI 多 Agent 自我迭代团队 版本：v2.4 → v2.5 日期：2026-05-30 核心原则：轻资产 · 预训练模型优先 · 云端重算力 · 不重复造轮子
【核心理念】三句话指导所有技术决策
能用 API 就不用本地模型 — 调用预训练模型的云端接口最快最省
能租就算力就不买硬件 — 需要GPU时云端按小时租用，用完即释放
能用现成工具就不自己写 — 绝不从头训练模型，绝不自建基础设施
本地（Mac Mini M4 16GB）只干三件事： - 跑Python数据处理脚本（pandas/sqlite，纯CPU） - 调用云端API（模型推理、向量化、知识图谱查询） - 协调整个管线（当指挥官，不当苦力）
一、任务分层：什么在本地、什么上云端
本地层（Mac Mini M4 16GB）— 只做”指挥官”
任务
方式
为什么本地
CBDB数据下载+SQLite导入
Python + sqlite3
纯IO操作，不需要GPU
数据清洗/筛选/聚合
pandas
CPU足够，M4很快
脚本协调/调度
Python主脚本
本地控制逻辑
API调用封装
requests库
轻量HTTP请求
结果整合/可视化
matplotlib + 本地渲染
数据量小
论文Markdown编辑
任意文本编辑器
纯文本
本地不做的（全部上云）： - ❌ 任何模型推理（&gt;100M参数）→ 走API - ❌ 任何模型训练/微调 → 走云端租用 - ❌ 向量数据库服务 → 走云端托管 - ❌ 知识图谱存储 → 走云端托管 - ❌ 大规模并行计算 → 走云端
云端API层（按token/按调用付费）— “即插即用”
服务
用途
推荐供应商
预估费用
大模型API（中文）
情感分析、文本理解、论文润色
Mini Max / 通义千问 / 文心
¥0.5-2/千token
大模型API（英文）
论文翻译、英文润色
Claude / GPT-4o / Gemini
$0.5-5/百万token
Embedding API
文本向量化（知识图谱用）
Mini Max Embedding / 通义Embedding
¥0.1/千token
Hugging Face Inference API
开源模型推理（SikuBERT等）
Hugging Face
免费额度+$0.012/次
云端租算力层（按小时租用）— “临时重型装备”
场景
推荐平台
配置
费用
使用方式
TKG小规模实验
Google Colab T4
T4 GPU 16GB
免费
Jupyter笔记本
正式TKG训练/批量处理
Google Colab A100
A100 40GB
~$10-15/次
用完即关
长时间训练(&gt;4小时)
AutoDL
A100 40GB
~¥1.5/小时
用完即释放
超大规模并行
RunPod
A100/H100
~$1-2/小时
按需创建
租用原则：
1. 先用Colab免费T4做实验验证2. 验证通过后再用Colab A100做正式运行3. 需要&gt;4小时的任务才用AutoDL/RunPod4. 用完立即释放实例，不要挂着不用5. 每次租用前问：&quot;这个任务能不能用API替代？&quot;
二、预训练模型清单（不重复造轮子清单）
2.1 直接调用API（最优先）
这些任务不需要本地跑模型，直接调用API：
任务
API方案
为什么不用本地
古籍文本情感分析
Mini Max API / 通义千问API
7B+模型本地慢，API更快更准
文言文理解/翻译
Mini Max API / 文心API
云端模型持续更新，效果更好
隐喻识别/提取
GPT-4o / Claude API
强模型做复杂推理任务
论文润色/扩写
Claude 3.5 Sonnet API
英文论文润色最强
代码生成/调试
Claude / GPT-4o API
比本地7B模型代码能力强
文本Embedding
Mini Max Embedding API
向量化走API最省事
API调用模板：
import requests# Mini Max API示例（情感分析）def analyze_sentiment_api(text: str) -&gt; float:    &quot;&quot;&quot;调用云端API做情感分析，不在本地跑模型&quot;&quot;&quot;    response = requests.post(        &quot;https://api.minimax.chat/v1/text/chatcompletion_v2&quot;,        headers={&quot;Authorization&quot;: f&quot;Bearer {API_KEY}&quot;},        json={            &quot;model&quot;: &quot;MiniMax-Text-01&quot;,            &quot;messages&quot;: [                {&quot;role&quot;: &quot;system&quot;, &quot;content&quot;: &quot;你是一个古籍文本情感分析专家。请分析以下文本的情感极性，返回-1.0到+1.0之间的数值。只返回数字，不要解释。&quot;},                {&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: text}            ]        }    )    result = response.json()    # 解析返回的情感分数    return parse_sentiment(result)# 批量处理时加入重试和缓存from functools import lru_cache@lru_cache(maxsize=10000)def cached_sentiment(text: str) -&gt; float:    &quot;&quot;&quot;缓存避免重复API调用&quot;&quot;&quot;    return analyze_sentiment_api(text)
2.2 Hugging Face Inference API（免费额度内）
SikuBERT等开源模型，不需要下载到本地，直接用Hugging Face的免费推理API：
import requests# SikuBERT via Hugging Face Inference API（免费）def sikubert_inference(text: str) -&gt; dict:    &quot;&quot;&quot;调用Hugging Face免费API，不下载模型到本地&quot;&quot;&quot;    API_URL = &quot;https://api-inference.huggingface.co/models/nghuyong/ernie-3.0-mini-zh&quot;    headers = {&quot;Authorization&quot;: f&quot;Bearer {HF_API_TOKEN}&quot;}    response = requests.post(API_URL, headers=headers, json={&quot;inputs&quot;: text})    return response.json()# 注意：免费API有速率限制（约10-50请求/秒）# 大批量处理时：加time.sleep(0.1)避免限流# 或者升级付费：$0.012/次，依然很便宜
2.3 云端租算力（极少数场景）
只有以下情况才租用GPU：
场景
为什么必须租
替代方案
TKG因果图谱训练
需要GPU加速图计算
先用Colab免费T4实验
批量Embedding（&gt;10万条）
本地CPU太慢
分批走API
7B模型微调
需要GPU训练
不建议微调，直接用预训练
绝大多数场景下，问这三个问题后都能找到不需要租GPU的方案：
这个任务能不能走API？
能不能用更小的模型替代？
能不能减少数据量先做验证？
三、v2.5 迭代任务（轻资产版）
🔴 P0-1：CBDB真实数据接入（本地完成，纯CPU）
方式：Python + sqlite3 + pandas，全部本地
# 本地SQLite方案（轻量，不需要PostgreSQL）import sqlite3import pandas as pd# 1. 下载CBDB数据（HTTP下载，纯网络）# 2. 导入SQLite（本地文件，不需要服务器）conn = sqlite3.connect(&quot;cbdb_local.db&quot;)# 3. 四朝筛选（pandas，CPU足够）df = pd.read_sql(&quot;&quot;&quot;    SELECT c_personid, c_name_chn, c_birthyear, c_deathyear, c_index_addr_id    FROM biog_main    WHERE c_birthyear BETWEEN 618 AND 907  -- 唐朝       OR c_deathyear BETWEEN 618 AND 907&quot;&quot;&quot;, conn)# 4. IPW校正 + PSI计算（numpy/scipy，纯CPU）# 5. 结果保存JSON
验收：四朝28周期PSI + 95%CI
🔴 P0-2：NLP情感分析（走API，不走本地模型）
方式：Mini Max API / 通义千问API做情感分析
# 批量情感分析走APIimport requestsimport timefrom concurrent.futures import ThreadPoolExecutordef batch_sentiment_api(texts: list) -&gt; list:    &quot;&quot;&quot;批量调用API，本地只负责协调&quot;&quot;&quot;    results = []    with ThreadPoolExecutor(max_workers=5) as executor:        futures = [executor.sentiment_api(t) for t in texts]        for f in futures:            results.append(f.result())            time.sleep(0.1)  # 避免限流    return results# 预估费用：1000条文本 × 平均50字 × ¥0.5/千token ≈ ¥25
为什么不本地跑SikuBERT？ - 云端API模型更强（7B-100B参数 vs 本地108M） - 不需要安装transformers/torch - 不需要处理MPS兼容性问题 - API费用极低（¥25处理1000条）
验收：1000+条四朝文本情感分数
🔴 P0-3：论文扩展（API辅助写作，人工把关）
方式：Claude API辅助扩写 + 人工审核修改
论文部分
人工写骨架
API辅助填充
API用途
文献综述
写大纲+框架
Claude扩写
文献总结、学术表达
方法论
写公式+流程
Claude润色
英文表达优化
结果
写数据+图表
Claude描述
结果描述文字
讨论
写核心论点
Claude扩展
论述展开
API调用策略：
# 用Claude API扩写论文段落def expand_section(bullet_points: str, target_words: int) -&gt; str:    &quot;&quot;&quot;输入要点大纲，输出扩写后的学术段落&quot;&quot;&quot;    response = requests.post(        &quot;https://api.anthropic.com/v1/messages&quot;,        headers={&quot;Authorization&quot;: f&quot;Bearer {ANTHROPIC_KEY}&quot;},        json={            &quot;model&quot;: &quot;claude-3-5-sonnet-20241022&quot;,            &quot;max_tokens&quot;: 2000,            &quot;system&quot;: &quot;你是一个Digital Humanities领域的学术写作专家。请将以下要点扩写为正式的英文学术段落，使用学术英语风格，包含适当的引用格式。&quot;,            &quot;messages&quot;: [{&quot;role&quot;: &quot;user&quot;, &quot;content&quot;: f&quot;请扩写以下内容至约{target_words}词：\n\n{bullet_points}&quot;}]        }    )    return response.json()[&quot;content&quot;][0][&quot;text&quot;]
预估API费用：论文全程辅助约 ¥200-500
验收：8000词英文学术论文
🟡 P1-1：CPM-KB扩展（API辅助 + 人工审核）
方式：用API自动提取隐喻 + 人工审核
# 1. API自动提取隐喻模式def extract_metaphors_api(text_batch: list) -&gt; list:    &quot;&quot;&quot;调用GPT-4o API从古籍文本中抽取隐喻&quot;&quot;&quot;    prompt = &quot;&quot;&quot;    请从以下古籍文本中提取所有隐喻表达，格式如下：    - 隐喻模式: [X为Y]    - 源域: [具体类别]    - 目标域: [具体类别]    - 例句: [原文]    - 情感极性: [正面/负面/中性]    &quot;&quot;&quot;    # 调用API...# 2. 人工审核（项目负责人或团队成员）# 审核标准：每条隐喻是否有文献出处、分类是否合理
预估费用：1000条隐喻提取 ≈ ¥100-200
🟡 P1-2：敏感性分析（本地完成，纯CPU）
Bootstrap、先验敏感性、交叉验证 — 全部是数值计算，本地pandas+numpy足够。
🟢 P2：TKG评估（Colab免费T4）
只在Google Colab免费T4上跑实验，验证TransFIR/TGL-LLM的可行性，不需要租用A100。
四、成本预估（v2.5全阶段）
项目
方式
预估费用
CBDB数据处理
本地Python
¥0
情感分析（1000条）
Mini Max API
¥25
隐喻提取（1000条）
GPT-4o API
¥150
论文辅助写作
Claude API
¥300
TKG实验
Colab T4免费
¥0
Embedding向量化
API免费额度
¥0
论文翻译
Claude API
¥100
v2.5总费用
≈ ¥575
如果需要Colab A100（正式TKG训练时）： - 每次$10-15，预计2-3次 = $30-45（约¥220-330）
v2.5全阶段总预算：≤ ¥1000
五、技术决策权（完全自主）
以下决策不需要汇报，团队自行判断：
决策
原则
选哪个API
哪个便宜+效果好就用哪个，随时可换
要不要租GPU
先问能不能用API替代，能就不用
代码怎么写
团队自己定，只要轻资产就行
论文怎么写
框架人工定，文字API辅助
数据处理策略
本地pandas能处理的就不上云
需要汇报的（仅三种情况）： 1. 月度API费用超过¥500 2. 需要单次租用GPU超过¥100 3. 遇到技术阻塞超过3天无法解决
六、每周汇报格式（极简）
# Week N 汇报## 完成- [任务] [一句话结果]## 费用- API费用：X元（月度X%）- 云端租用：X元## 下周- [任务]## 阻塞- 有/无
轻资产 · 快推进 · 不造轮子。本地当指挥官，云端当重型装备，API当即插即用工具。