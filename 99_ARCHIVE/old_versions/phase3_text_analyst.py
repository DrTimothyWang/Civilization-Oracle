# Civilization-Oracle — Phase 3 实现
# TextAnalystAgent（文本分析）+ CTEXT全文检索 + BERT情感分类 + 隐喻识别

"""
Phase 3 交付物说明：
- ctext_client.py：CTEXT（中国哲学书电子化计划）完整API客户端
- phase3_text_analyst.py：TextAnalystAgent可运行版本

核心能力：
1. CTEXT全文检索：3万+部古籍，50亿字，中英双语，完全免费
2. 情感分析：基于规则 + 可扩展为BERT模型
3. 隐喻识别：CPM-KB知识库驱动（心为火/水、家国为舟等）
4. PSI指数文本代理：MMP/EMP/SFD三个指标的文本计算

使用前准备：
- CTEXT：无需注册，直接使用 ctext.org
- BERT模型（可选）：pip install transformers torch
- CPM-KB：内嵌基础版本（可扩展）
"""
import json
import re
from pathlib import Path
from typing import Iterator, Optional
from dataclasses import dataclass
import logging

# ============================================================
# data_access/ctext_client.py
# CTEXT（中国哲学书电子化计划）完整客户端
# ============================================================
"""
CTEXT — Chinese Text Project
官网：https://ctext.org/zh
API文档：https://ctext.org/instructions/api/zh

特点：
- 完全免费，无需注册
- 3万+部古籍，50亿字
- 支持中英双语
- 提供RESTful API

API限制：
- 检索请求：建议间隔1秒以上
- 批量获取章节内容：需分页
- User-Agent必须设置（已内置）
"""
import requests
import time

logger = logging.getLogger("ctext_client")


class CTextClient:
    """
    CTEXT API客户端

    提供的方法：
    - search_texts()：全文检索
    - get_text_info()：获取古籍元信息
    - get_chapters()：获取章节列表
    - get_text_content()：获取古籍正文
    - batch_search()：批量检索（自动限速）
    """

    BASE_URL = "https://ctext.org/api"
    USER_AGENT = "Civilization-Oracle/1.0 (Academic Research)"

    def __init__(self, rate_limit: float = 1.0):
        """
        参数：
            rate_limit: 每次API调用间隔（秒），默认1秒避免触发限制
        """
        self.rate_limit = rate_limit
        self.last_call = 0
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json",
        })
        self.request_count = 0

    def _rate_limit(self):
        """限速控制"""
        elapsed = time.time() - self.last_call
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_call = time.time()
        self.request_count += 1

    # ── 核心API方法 ──────────────────────────────────────

    def search_texts(
        self,
        keywords: list[str] = None,
        keyword: str = None,
        time_range: tuple[int, int] = None,
        scope: str = "all",
        page: int = 1,
        per_page: int = 100,
    ) -> dict:
        """
        全文检索古籍

        参数：
            keywords: 关键词列表（空格分隔，隐式AND）
            keyword: 单一关键词（与keywords互斥）
            time_range: [start_year, end_year]，用于过滤结果
            scope: 检索范围
                "all" — 全部
                "pre-qin" — 先秦
                "han" — 两汉
                "three-kingdoms" — 三国
                "jin" — 两晋
                "sui-tang" — 隋唐
                "song" — 宋
                "yuan" — 元
                "ming" — 明
                "qing" — 清
                "modern" — 近代
            page: 页码
            per_page: 每页结果数（最大100）

        返回：
            {
                "total": int,
                "page": int,
                "per_page": int,
                "results": [ ... ]   # 每项含id, title, year, excerpt
            }
        """
        if keywords:
            query = " ".join(keywords)
        elif keyword:
            query = keyword
        else:
            raise ValueError("必须提供 keywords 或 keyword")

        self._rate_limit()
        params = {
            "search": query,
            "scope": scope,
            "page": page,
            "results": per_page,
        }

        resp = self.session.get(f"{self.BASE_URL}/search/zh", params=params)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])

        # 按时间过滤
        if time_range and results:
            results = [
                r for r in results
                if self._in_time_range(r.get("year"), time_range)
            ]
            data["results"] = results

        return data

    def search_and_iterate(
        self,
        keywords: list[str] = None,
        keyword: str = None,
        time_range: tuple[int, int] = None,
        scope: str = "all",
        max_results: int = 500,
    ) -> Iterator[dict]:
        """
        自动翻页遍历所有检索结果
        """
        page = 1
        total_yielded = 0
        per_page = 100

        while total_yielded < max_results:
            result = self.search_texts(
                keywords=keywords,
                keyword=keyword,
                time_range=time_range,
                scope=scope,
                page=page,
                per_page=per_page,
            )

            results = result.get("results", [])
            if not results:
                break

            for item in results:
                if total_yielded >= max_results:
                    return
                yield item
                total_yielded += 1

            # 检查是否还有更多
            if len(results) < per_page:
                break
            page += 1

        logger.info(f"CTEXT检索完成，共获取{total_yielded}条结果，API调用{self.request_count}次")

    def get_text_info(self, text_id: str) -> dict:
        """
        获取古籍元信息

        text_id格式：如 "zhozu"（左传）、"zz"（论语）、"mengzi"（孟子）
        """
        self._rate_limit()
        resp = self.session.get(f"{self.BASE_URL}/text/{text_id}/zh")
        resp.raise_for_status()
        return resp.json()

    def get_chapters(self, text_id: str) -> list[dict]:
        """获取古籍章节列表"""
        self._rate_limit()
        resp = self.session.get(f"{self.BASE_URL}/chapters/{text_id}/zh")
        resp.raise_for_status()
        return resp.json()

    def get_text_content(
        self,
        text_id: str,
        chapter: str = None,
        paragraph_range: tuple[int, int] = None,
    ) -> dict:
        """
        获取古籍正文

        参数：
            text_id: 古籍ID
            chapter: 章节名（如"公孙丑上"），None=整本
            paragraph_range: [start, end]，段落范围
        """
        self._rate_limit()

        if chapter:
            url = f"{self.BASE_URL}/{text_id}/{chapter}/zh"
        else:
            url = f"{self.BASE_URL}/text/{text_id}/zh"

        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()

        # 段落范围过滤
        if paragraph_range and "paragraphs" in data:
            start, end = paragraph_range
            data["paragraphs"] = data["paragraphs"][start:end]

        return data

    def batch_search(
        self,
        queries: list[dict],
        time_range: tuple[int, int] = None,
    ) -> list[dict]:
        """
        批量检索多个关键词

        参数：
            queries: [{"keyword": "王安石", "scope": "song"}, ...]
            time_range: 全局时间过滤
        """
        results = []
        for q in queries:
            try:
                result = self.search_texts(
                    keyword=q.get("keyword"),
                    scope=q.get("scope", "all"),
                    time_range=time_range,
                    page=1,
                    per_page=20,
                )
                results.append({
                    "query": q,
                    "total": result.get("total", 0),
                    "top_results": result.get("results", [])[:5],
                })
            except Exception as e:
                logger.warning(f"CTEXT批量检索失败：{q.get('keyword')} → {e}")

        return results

    def get_author_texts(self, author_name: str, max_results: int = 50) -> list[dict]:
        """
        获取某作者的全部著作

        参数：
            author_name: 作者名（如"韩愈"、"柳宗元"）
            max_results: 最大返回条数
        """
        # 搜索作者相关文本
        search_result = self.search_texts(
            keyword=author_name,
            scope="all",
            per_page=max_results,
        )

        # 过滤出作者相关的
        relevant = []
        for item in search_result.get("results", []):
            title = item.get("title", "")
            if author_name in title:
                relevant.append(item)

        return relevant

    def _in_time_range(self, year: Optional[int], time_range: tuple[int, int]) -> bool:
        if year is None:
            return True
        return time_range[0] <= year <= time_range[1]

    def close(self):
        logger.info(f"CTEXT客户端关闭，共发起{self.request_count}次API请求")


# ============================================================
# phase3_text_analyst.py
# TextAnalystAgent — 可运行完整版本
# ============================================================
"""
TextAnalystAgent — 文本分析Agent

核心功能：
1. 情感分析：基于规则的情感极性计算（-1到+1）
2. 隐喻识别：CPM-KB知识库驱动
3. PSI文本代理：MMP/EMP/SFD三个指标的文本计算
4. CTEXT集成：古籍文本检索 + 自动分析

学术背景（CPM-KB）：
- 隐喻模式 → 心理状态映射
- 例如：心为火 → 焦虑/愤怒（负）
- 心为水 → 平静/超脱（正）
- 家国为舟 → 希望/焦虑（语境依赖）
- 来源：马利军教授语义心理学研究框架

行业代码：
- 儒 RU / 医 ME / 农 AG / 工 IN / 商 MER / 兵 MI / 艺 AR / 道 DAO / 佛 FO
"""


# ── CPM-KB：隐喻-心理知识库（内嵌基础版本）─────────────────────────────

CPM_KB = {
    # 核心隐喻映射：source_domain → target_psychological_state
    "心为火": {
        "psychological_state": "焦虑/愤怒",
        "polarity": -1,
        "domain": "情绪",
        "typical_context": "唐诗/盛唐",
        "keywords": ["心火", "怒火", "焦心", "燎原"],
    },
    "心为水": {
        "psychological_state": "平静/超脱",
        "polarity": 1,
        "domain": "情绪",
        "typical_context": "宋诗/道家文人",
        "keywords": ["心水", "静水", "心如止水", "清心"],
    },
    "家国为舟": {
        "psychological_state": "语境依赖",
        "polarity": 0,
        "domain": "社会",
        "typical_context": "全朝/杜甫诗",
        "keywords": ["同舟", "覆舟", "舟载", "舟行"],
    },
    "天地不仁": {
        "psychological_state": "绝望/虚无",
        "polarity": -1,
        "domain": "哲学",
        "typical_context": "战乱期/晚明",
        "keywords": ["不仁", "天意", "天道", "造化"],
    },
    "春风得意": {
        "psychological_state": "乐观/自豪",
        "polarity": 1,
        "domain": "成就",
        "typical_context": "科举/治世",
        "keywords": ["得意", "春风", "及第", "金榜"],
    },
    "民生凋敝": {
        "psychological_state": "悲观/忧虑",
        "polarity": -1,
        "domain": "社会",
        "typical_context": "乱世/末世",
        "keywords": ["凋敝", "民不聊生", "哀鸿", "满目疮痍"],
    },
    "改革图强": {
        "psychological_state": "希望/进取",
        "polarity": 1,
        "domain": "政治",
        "typical_context": "改革期/宋代",
        "keywords": ["改革", "图强", "变法", "革新", "新政"],
    },
    "党争激烈": {
        "psychological_state": "焦虑/不安",
        "polarity": -1,
        "domain": "政治",
        "typical_context": "宋代/明代",
        "keywords": ["党争", "新旧", "君子小人", "门户"],
    },
    "天命在我": {
        "psychological_state": "自信/豪迈",
        "polarity": 1,
        "domain": "天命",
        "typical_context": "开国/盛世",
        "keywords": ["天命", "天授", "真龙", "奉天"],
    },
    "大厦将倾": {
        "psychological_state": "绝望/危机",
        "polarity": -1,
        "domain": "政治",
        "typical_context": "末世/晚明",
        "keywords": ["将倾", "末路", "崩塌", "危局"],
    },
}


# ── PSI文本代理词汇表 ─────────────────────────────────────────────────

PSI_LEXICON = {
    # MMP指标：群众动员潜力
    "MMP": {
        "positive": [
            "民变", "起义", "造反", "揭竿", "流民", "饥荒",
            "赋税", "加税", "重赋", "搜刮", "民怨", "沸腾",
            "暴动", "抗争", "叛乱", "蜂起", "思乱",
        ],
        "negative": [
            "丰年", "免税", "减赋", "休养生息", "太平",
        ],
        "weight": {
            "暴动": 1.0, "起义": 0.9, "民变": 0.8, "造反": 0.9,
            "赋税": 0.7, "加税": 0.8, "饥荒": 0.8, "流民": 0.8,
        },
    },
    # EMP指标：精英动员潜力
    "EMP": {
        "positive": [
            "党争", "内斗", "科举", "竞争", "精英", "士人",
            "文官", "宰相", "权臣", "朋党", "纷争", "对立",
        ],
        "negative": [
            "和谐", "共识", "协力", "团结", "一心",
        ],
        "weight": {
            "党争": 0.9, "内斗": 0.9, "权臣": 0.7,
            "科举": 0.6, "士人": 0.5, "文官": 0.6,
        },
    },
    # SFD指标：国家财政压力
    "SFD": {
        "positive": [
            "财政", "赤字", "匮乏", "空虚", "军费",
            "战费", "赔款", "债台", "加派", "横征",
            "粮价", "暴涨", "物价", "通胀",
        ],
        "negative": [
            "盈余", "充盈", "富足", "宽裕",
        ],
        "weight": {
            "赤字": 1.0, "债台": 0.9, "军费": 0.8,
            "粮价暴涨": 0.9, "战费": 0.8, "赔款": 0.9,
        },
    },
}


# ── TextAnalystAgent实现 ──────────────────────────────────────────────

@dataclass
class TextAnalystInput:
    documents: list[dict]   # [{"id": "", "text": "", "source": "", "year": 1069}, ...]
    analysis_types: list[str]   # ["sentiment", "metaphor", "psi_index"]
    context: dict = None         # {"dynasty": "宋", "year_range": [960, 1279]}


@dataclass
class TextAnalystOutput:
    status: str
    results: list[dict]
    model_version: str
    metadata: dict


class TextAnalystAgent:
    """
    文本分析Agent

    输入：
    - 古籍文本（来自CTEXT或其他古籍库）
    - 分析类型：情感 / 隐喻 / PSI指数

    输出：
    - 每篇文本的：情感极性、隐喻模式、PSI文本代理指标
    - hope_ratio（希望叙事比）、disaster_narrative（灾难叙事）
    """

    def __init__(self, ctext_client=None):
        self.ctext = ctext_client or CTextClient()
        self._metaphor_cache = {}

    def run(self, input_data: TextAnalystInput) -> TextAnalystOutput:
        """执行文本分析"""
        results = []

        for doc in input_data.documents:
            result = {"doc_id": doc.get("id", f"doc_{len(results)}")}

            if "sentiment" in input_data.analysis_types:
                result["sentiment"] = self._analyze_sentiment(doc["text"])

            if "metaphor" in input_data.analysis_types:
                result["metaphors"] = self._detect_metaphors(doc["text"])

            if "psi_index" in input_data.analysis_types:
                result["psi_inputs"] = self._compute_psi_from_text(doc["text"])

            # 灾难叙事与希望叙事
            result["hope_ratio"] = self._compute_hope_ratio(doc["text"])
            result["disaster_narrative"] = self._compute_disaster_narrative(doc["text"])

            results.append(result)

        return TextAnalystOutput(
            status="success",
            results=results,
            model_version="TextAnalyst-v3.1 (rule-based + CPM-KB)",
            metadata={
                "docs_analyzed": len(results),
                "analysis_types": input_data.analysis_types,
                "ctext_requests": self.ctext.request_count,
            },
        )

    def analyze_ctext_results(
        self,
        search_keyword: str,
        scope: str = "song",
        time_range: tuple[int, int] = None,
        max_results: int = 50,
    ) -> TextAnalystOutput:
        """
        一站式：CTEXT检索 → 文本分析

        参数：
            search_keyword: 检索关键词
            scope: 朝代范围
            time_range: 时间范围
            max_results: 最大分析条数
        """
        docs = []

        for item in self.ctext.search_and_iterate(
            keyword=search_keyword,
            scope=scope,
            time_range=time_range,
            max_results=max_results,
        ):
            docs.append({
                "id": item.get("id", item.get("title", "")),
                "text": item.get("excerpt", ""),
                "title": item.get("title", ""),
                "year": item.get("year"),
                "source": "CTEXT",
                "scope": scope,
            })

        return self.run(TextAnalystInput(
            documents=docs,
            analysis_types=["sentiment", "metaphor", "psi_index"],
        ))

    # ── 情感分析 ──────────────────────────────────────

    POSITIVE_WORDS = {
        "希望", "光明", "盛世", "太平", "繁荣", "富强", "安康", "祥和",
        "喜悦", "欢欣", "庆贺", "祝福", "吉祥", "如意", "成功", "胜利",
        "进步", "发展", "改革", "创新", "中兴", "复兴", "崛起",
        "仁政", "贤明", "清明", "有序", "安定", "和乐",
    }

    NEGATIVE_WORDS = {
        "哀", "悲", "叹", "忧", "愁", "怨", "恨", "怒",
        "乱", "祸", "灾", "凶", "危", "亡", "灭", "败",
        "凋敝", "颓废", "腐败", "黑暗", "动荡", "纷争",
        "民不聊生", "生灵涂炭", "满目疮痍", "哀鸿遍野",
    }

    INTENSITY_WORDS = {
        "极": 1.5, "甚": 1.3, "非常": 1.3,
        "稍": 0.7, "略": 0.7, "微": 0.5,
    }

    def _analyze_sentiment(self, text: str) -> dict:
        """
        情感极性分析

        返回：
            {
                "polarity": float（-1到+1）,
                "positive_score": float,
                "negative_score": float,
                "dominant_emotion": str,
                "intensity": str ("高" / "中" / "低"),
            }
        """
        pos_count = 0
        neg_count = 0
        total_count = 0

        for word in self.POSITIVE_WORDS:
            count = text.count(word)
            pos_count += count
            total_count += count

        for word in self.NEGATIVE_WORDS:
            count = text.count(word)
            neg_count += count
            total_count += count

        if total_count == 0:
            polarity = 0.0
        else:
            polarity = round((pos_count - neg_count) / (pos_count + neg_count + 1), 3)

        # 情绪标签
        if polarity >= 0.5:
            dominant = "乐观/积极"
        elif polarity >= 0.1:
            dominant = "希望/平和"
        elif polarity > -0.1:
            dominant = "中性/客观"
        elif polarity > -0.5:
            dominant = "悲观/忧虑"
        else:
            dominant = "绝望/消极"

        # 强度
        intensity_sum = 0
        intensity_count = 0
        for word, weight in self.INTENSITY_WORDS.items():
            if word in text:
                intensity_sum += weight
                intensity_count += 1
        intensity = "高" if intensity_count > 0 and intensity_sum / intensity_count > 1.2 else \
                    "低" if intensity_count > 0 and intensity_sum / intensity_count < 0.8 else "中"

        return {
            "polarity": polarity,
            "positive_score": round(pos_count / (total_count + 1), 3),
            "negative_score": round(neg_count / (total_count + 1), 3),
            "dominant_emotion": dominant,
            "intensity": intensity,
        }

    # ── 隐喻识别 ──────────────────────────────────────

    def _detect_metaphors(self, text: str) -> list[dict]:
        """
        隐喻识别：基于CPM-KB知识库

        返回：检测到的隐喻列表，每项含模式、极性、心理状态
        """
        detected = []

        for metaphor_id, metaphor_data in CPM_KB.items():
            for keyword in metaphor_data["keywords"]:
                if keyword in text:
                    # 检查是否有修饰词调整极性
                    adjusted_polarity = self._adjust_metaphor_polarity(
                        text, keyword, metaphor_data["polarity"]
                    )

                    detected.append({
                        "pattern": metaphor_id,
                        "keyword": keyword,
                        "psychological_state": metaphor_data["psychological_state"],
                        "base_polarity": metaphor_data["polarity"],
                        "adjusted_polarity": adjusted_polarity,
                        "domain": metaphor_data["domain"],
                        "typical_context": metaphor_data["typical_context"],
                    })
                    break  # 每个隐喻模式只记录一次

        return detected

    def _adjust_metaphor_polarity(self, text: str, keyword: str, base_polarity: float) -> float:
        """根据上下文调整隐喻极性"""
        # 双重否定（如"不仁"）保持负极性但减轻
        if "不" in text[max(0, text.find(keyword) - 3):text.find(keyword)]:
            return base_polarity * 0.8
        return base_polarity

    # ── PSI文本代理 ──────────────────────────────────────

    def _compute_psi_from_text(self, text: str) -> dict:
        """
        从文本计算PSI三个输入指标（MMP/EMP/SFD）

        方法：基于词汇统计的代理指标（0-1范围）
        """
        mmp = self._compute_sub_index(text, "MMP")
        emp = self._compute_sub_index(text, "EMP")
        sfd = self._compute_sub_index(text, "SFD")

        # PSI简化为三者乘积（归一化）
        psi_proxy = mmp * emp * sfd * 3  # 乘3使范围约在0-1

        return {
            "MMP": round(mmp, 3),
            "EMP": round(emp, 3),
            "SFD": round(sfd, 3),
            "PSI_proxy": round(psi_proxy, 3),
            "method": "lexicon_based_text_proxy",
        }

    def _compute_sub_index(self, text: str, index_name: str) -> float:
        """计算单个PSI子指标"""
        lex = PSI_LEXICON[index_name]
        pos_weighted = 0
        neg_weighted = 0

        for word in lex["positive"]:
            count = text.count(word)
            w = lex["weight"].get(word, 0.7)
            pos_weighted += count * w

        for word in lex["negative"]:
            count = text.count(word)
            w = lex["weight"].get(word, 0.7)
            neg_weighted += count * w

        total = pos_weighted + neg_weighted
        if total == 0:
            return 0.3  # 默认中间值

        # 正向词越多→指标越高（0.3-1.0范围）
        return min(1.0, 0.3 + (pos_weighted - neg_weighted) * 0.1)

    # ── 叙事分析 ──────────────────────────────────────

    HOPE_MARKERS = [
        "希望", "期盼", "期待", "曙光", "黎明", "复兴", "中兴",
        "盛世", "太平", "有望", "将兴", "必胜", "有望", "前途光明",
        "改革", "变法", "革新", "振作", "图强", "励精",
    ]

    DISASTER_MARKERS = [
        "灾难", "浩劫", "天灾", "人祸", "大乱", "将亡", "末日",
        "崩塌", "崩溃", "满目疮痍", "哀鸿遍野", "生灵涂炭",
        "大厦将倾", "危局", "末路", "绝望", "无力回天",
    ]

    def _compute_hope_ratio(self, text: str) -> float:
        """计算希望叙事占比（0-1）"""
        hope_count = sum(text.count(w) for w in self.HOPE_MARKERS)
        disaster_count = sum(text.count(w) for w in self.DISASTER_MARKERS)
        total = hope_count + disaster_count

        if total == 0:
            return 0.5  # 中性
        return round(hope_count / total, 3)

    def _compute_disaster_narrative(self, text: str) -> float:
        """计算灾难叙事占比（0-1）"""
        disaster_count = sum(text.count(w) for w in self.DISASTER_MARKERS)
        hope_count = sum(text.count(w) for w in self.HOPE_MARKERS)
        total = hope_count + disaster_count

        if total == 0:
            return 0.5  # 中性
        return round(disaster_count / total, 3)

    # ── 批量分析工具 ──────────────────────────────────────

    def analyze_author_corpus(
        self,
        author_name: str,
        dynasty: str = "song",
        max_texts: int = 100,
    ) -> dict:
        """
        分析某作者的全部文本（批量操作）

        返回：情感时序、隐喻分布、PSI指标聚合
        """
        search_result = self.ctext.search_texts(
            keyword=author_name,
            scope=dynasty,
            per_page=max_texts,
        )

        yearly_sentiment = {}
        all_metaphors = {}
        all_psi = []

        for item in search_result.get("results", [])[:max_texts]:
            year = item.get("year", 0)
            excerpt = item.get("excerpt", "")

            if not excerpt:
                continue

            # 情感
            sentiment = self._analyze_sentiment(excerpt)
            polarity = sentiment["polarity"]

            # 隐喻
            metaphors = self._detect_metaphors(excerpt)

            # PSI
            psi = self._compute_psi_from_text(excerpt)

            # 按年聚合
            if year:
                year_key = year // 10 * 10  # 按十年分组
                if year_key not in yearly_sentiment:
                    yearly_sentiment[year_key] = []
                yearly_sentiment[year_key].append(polarity)

            # 隐喻全局统计
            for m in metaphors:
                pattern = m["pattern"]
                all_metaphors[pattern] = all_metaphors.get(pattern, 0) + 1

            all_psi.append(psi)

        # 计算年均情感
        yearly_avg = {
            year: sum(pols) / len(pols)
            for year, pols in yearly_sentiment.items()
        }

        # 计算PSI均值
        avg_psi = {
            "MMP": sum(p["MMP"] for p in all_psi) / max(len(all_psi), 1),
            "EMP": sum(p["EMP"] for p in all_psi) / max(len(all_psi), 1),
            "SFD": sum(p["SFD"] for p in all_psi) / max(len(all_psi), 1),
        }
        avg_psi["PSI_proxy"] = (
            avg_psi["MMP"] * avg_psi["EMP"] * avg_psi["SFD"] * 3
        )

        return {
            "author": author_name,
            "dynasty": dynasty,
            "texts_analyzed": len(all_psi),
            "yearly_avg_sentiment": dict(sorted(yearly_avg.items())),
            "top_metaphors": sorted(
                all_metaphors.items(), key=lambda x: -x[1]
            )[:10],
            "avg_psi": {k: round(v, 3) for k, v in avg_psi.items()},
        }


# ============================================================
# 测试入口
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("Civilization-Oracle Phase 3 — TextAnalystAgent 快速测试")
    print("=" * 70)

    # 测试语料
    TEST_TEXTS = [
        {
            "id": "song_shu_wuzhi_001",
            "text": "王安石拜相，推行新法，整顿吏治，天下有望。",
            "source": "宋史",
            "year": 1069,
        },
        {
            "id": "song_shu_wuzhi_002",
            "text": "新旧党争，门户势如水火，朝野纷争不已。",
            "source": "宋史",
            "year": 1073,
        },
        {
            "id": "dufu_poem_001",
            "text": "国破山河在，城春草木深。感时花溅泪，恨别鸟惊心。",
            "source": "杜甫诗",
            "year": 757,
        },
        {
            "id": "mingshi_001",
            "text": "明季赋税日重，民不聊生，流民四起，大厦将倾。",
            "source": "明史",
            "year": 1630,
        },
        {
            "id": "li_bai_poem_001",
            "text": "长风破浪会有时，直挂云帆济沧海。",
            "source": "李白诗",
            "year": 725,
        },
        {
            "id": "mengzi_001",
            "text": "民为贵，社稷次之，君为轻。",
            "source": "孟子",
            "year": -300,
        },
    ]

    # 初始化Agent
    agent = TextAnalystAgent()

    # 测试1：单篇文本分析
    print("\n[1] 单篇文本分析测试")
    print("-" * 50)
    for text_item in TEST_TEXTS:
        result = agent.run(TextAnalystInput(
            documents=[text_item],
            analysis_types=["sentiment", "metaphor", "psi_index"],
        ))

        r = result.results[0]
        sent = r["sentiment"]
        print(f"\n📄 {text_item['id']}")
        print(f"   文本：{text_item['text'][:40]}...")
        print(f"   情感极性：{sent['polarity']}（{sent['dominant_emotion']}，强度{sent['intensity']}）")
        print(f"   希望叙事：{r['hope_ratio']} | 灾难叙事：{r['disaster_narrative']}")

        if r["metaphors"]:
            for m in r["metaphors"]:
                print(f"   🔮 隐喻：{m['pattern']} → {m['psychological_state']}（极性{m['adjusted_polarity']}）")

        psi = r["psi_inputs"]
        print(f"   PSI代理：MMP={psi['MMP']} EMP={psi['EMP']} SFD={psi['SFD']} → PSI={psi['PSI_proxy']}")

    # 测试2：批量文本分析
    print("\n\n[2] 批量文本分析测试")
    print("-" * 50)
    result = agent.run(TextAnalystInput(
        documents=TEST_TEXTS,
        analysis_types=["sentiment", "metaphor", "psi_index"],
    ))

    # 统计聚合
    polarities = [r["sentiment"]["polarity"] for r in result.results]
    avg_polarity = sum(polarities) / len(polarities)
    hope_ratios = [r["hope_ratio"] for r in result.results]
    disaster_ratios = [r["disaster_narrative"] for r in result.results]
    all_mmp = [r["psi_inputs"]["MMP"] for r in result.results]
    all_emp = [r["psi_inputs"]["EMP"] for r in result.results]
    all_sfd = [r["psi_inputs"]["SFD"] for r in result.results]

    print(f"  分析文本数：{len(result.results)}")
    print(f"  平均情感极性：{round(avg_polarity, 3)}（{'乐观' if avg_polarity > 0 else '悲观'}）")
    print(f"  平均希望叙事比：{round(sum(hope_ratios)/len(hope_ratios), 3)}")
    print(f"  平均灾难叙事比：{round(sum(disaster_ratios)/len(disaster_ratios), 3)}")
    print(f"  平均MMP：{round(sum(all_mmp)/len(all_mmp), 3)}")
    print(f"  平均EMP：{round(sum(all_emp)/len(all_emp), 3)}")
    print(f"  平均SFD：{round(sum(all_sfd)/len(all_sfd), 3)}")

    # 隐喻全局统计
    all_metas = {}
    for r in result.results:
        for m in r["metaphors"]:
            pattern = m["pattern"]
            all_metas[pattern] = all_metas.get(pattern, 0) + 1
    print(f"\n  全局隐喻分布：{dict(sorted(all_metas.items(), key=lambda x: -x[1]))}")

    print(f"\n  模型版本：{result.model_version}")
    print(f"  CTEXT API调用次数：{result.metadata['ctext_requests']}")

    # 测试3：CTEXT检索（需要网络）
    print("\n\n[3] CTEXT全文检索测试")
    print("-" * 50)
    print("  正在检索关键词'王安石'相关文本...")
    try:
        ctext_result = agent.ctext.search_texts(
            keyword="王安石",
            scope="song",
            per_page=10,
        )
        print(f"  检索到{text_result.get('total', 0)}条结果，显示前5条：")
        for item in ctext_result.get("results", [])[:5]:
            print(f"  • {item.get('title', '未知')}（{item.get('year', '?')}年）")
            excerpt = item.get("excerpt", "")
            if excerpt:
                print(f"    {excerpt[:60]}...")
        print("\n  ✅ CTEXT检索测试通过")
    except Exception as e:
        print(f"  ⚠️ CTEXT检索失败（网络问题）：{e}")
        print("  提示：CTEXT为完全免费API，可直接访问 https://ctext.org")

    # 测试4：作者语料分析
    print("\n\n[4] 作者语料分析测试（杜甫）")
    print("-" * 50)
    try:
        author_result = agent.analyze_author_corpus("杜甫", dynasty="song", max_texts=30)
        print(f"  分析杜甫唐代相关文本：{author_result['texts_analyzed']}篇")

        if author_result["yearly_avg_sentiment"]:
            print(f"  十年均值情感：")
            for year, pol in sorted(author_result["yearly_avg_sentiment"].items()):
                bar = "█" * int(abs(pol) * 10)
                sign = "+" if pol > 0 else "-"
                print(f"    {year}年代：{sign}{bar} {round(pol, 2)}")

        if author_result["top_metaphors"]:
            print(f"  高频隐喻模式：")
            for pattern, count in author_result["top_metaphors"][:5]:
                meta_info = CPM_KB.get(pattern, {})
                print(f"    {pattern} ×{count}次 → {meta_info.get('psychological_state', '未知')}")

        print(f"  全局PSI均值：MMP={author_result['avg_psi']['MMP']} "
              f"EMP={author_result['avg_psi']['EMP']} "
              f"SFD={author_result['avg_psi']['SFD']}")
        print(f"  PSI综合代理：{author_result['avg_psi']['PSI_proxy']}")

        print("\n  ✅ 作者语料分析测试完成")
    except Exception as e:
        print(f"  ⚠️ 作者分析失败：{e}")

    print("\n" + "=" * 70)
    print("Phase 3 测试完成")
    print("=" * 70)
    print("\n📌 下一步建议：")
    print("   1. 下载CBDB SQLite + 运行 phase2_data_ingest.py 验证数据流")
    print("   2. Phase 4：MasterOrchestrator 集成 DataIngestAgent + TextAnalystAgent")
    print("   3. Phase 5：KGraphAgent + Neo4j 时序知识图谱构建")
    print("   4. Phase 6：PredictorAgent + PSI计算 + 预测引擎")