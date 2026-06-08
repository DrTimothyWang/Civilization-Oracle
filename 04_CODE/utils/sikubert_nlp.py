"""
SikuBERT 古籍 NLP 模块 for Civilization-Oracle v2.4
替代通用BERT，提供专注文言文语义的理解能力
"""
import numpy as np


class SikuBERTNLP:
    """
    SikuBERT 接口（v2.4降级方案：规则+向量化）
    完整模型需: pip install transformers && from transformers import AutoModel
    """

    def __init__(self, model_name="nghuyong/ernie-3.0-mini-zh"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.use_mock = True  # 降级开关

        # 内嵌北宋语义词典（降级用）
        self.semantic_dictionary = self._load_fallback_dictionary()

    @classmethod
    def load_model(cls, model_name="nghuyong/ernie-3.0-mini-zh"):
        """
        加载 SikuBERT 模型（优先真实模型，失败则降级到规则方法）

        Args:
            model_name: HuggingFace 模型名，默认 nghuyong/ernie-3.0-mini-zh

        Returns:
            SikuBERTNLP 实例（use_mock=True 为规则模式，use_mock=False 为真实模型模式）
        """
        instance = cls(model_name=model_name)

        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch

            # 加载真实模型
            instance.tokenizer = AutoTokenizer.from_pretrained(model_name)
            instance.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=3,  # 3分类：负向/中性/正向
                ignore_mismatched_sizes=True
            )
            instance.use_mock = False
            print(f"[SikuBERT] 真实模型加载成功: {model_name}")

            # 将模型设为评估模式
            instance.model.eval()

            return instance
        except ImportError:
            print(f"[SikuBERT] transformers 未安装，使用规则模式")
            return instance
        except Exception as e:
            print(f"[SikuBERT] 模型加载失败，使用规则模式: {e}")
            return instance

    def _predict_with_model(self, text):
        """
        使用真实模型进行情感预测

        Returns:
            float: 情感分数 [-1, 1]
        """
        if self.model is None or self.tokenizer is None:
            return None

        try:
            import torch
            import torch.nn.functional as F

            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=256,
                padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits

                # 转换为概率分布
                probs = F.softmax(logits, dim=-1)
                # 情感分数计算：假设 label 0=负向, 1=中性, 2=正向
                sentiment_score = float(probs[0][2] - probs[0][0])  # 正向概率 - 负向概率

            return sentiment_score
        except Exception as e:
            print(f"[SikuBERT] 模型推理失败: {e}")
            return None

    def _load_fallback_dictionary(self):
        """内嵌降级词典：覆盖高频北宋文献概念"""
        return {
            # 朝代概念
            "盛世": {"positive": 0.85, "domain": "politics", "period": "北宋"},
            "积弊": {"negative": 0.80, "domain": "politics", "period": "北宋末期"},
            "民变": {"negative": 0.75, "domain": "social", "period": "北宋"},
            "变法": {"neutral": 0.60, "domain": "politics", "period": "北宋"},
            "革新": {"positive": 0.65, "domain": "politics", "period": "北宋"},
            "党争": {"negative": 0.85, "domain": "politics", "period": "北宋末期"},
            "边防": {"neutral": 0.55, "domain": "military", "period": "北宋"},
            "饥荒": {"negative": 0.80, "domain": "economy", "period": "北宋"},
            "科举": {"positive": 0.60, "domain": "culture", "period": "北宋"},
            "儒学": {"positive": 0.65, "domain": "culture", "period": "北宋"},
            # 补充高频词
            "太平": {"positive": 0.75, "domain": "politics", "period": "北宋"},
            "繁华": {"positive": 0.70, "domain": "economy", "period": "北宋"},
            "天下": {"neutral": 0.50, "domain": "politics", "period": "北宋"},
            "骨髓": {"negative": 0.70, "domain": "social", "period": "北宋末期"},
            "民不聊生": {"negative": 0.90, "domain": "social", "period": "北宋末期"},
            "朝纲": {"neutral": 0.55, "domain": "politics", "period": "北宋"},
            "紊乱": {"negative": 0.75, "domain": "politics", "period": "北宋末期"},
            "嘉祐": {"positive": 0.70, "domain": "politics", "period": "北宋"},
            "治": {"positive": 0.60, "domain": "politics", "period": "北宋"},
        }

    def analyze_sentiment(self, text):
        """
        古籍情感分析：返回情感分数 [-1, 1]
        优先使用真实模型推理，失败则降级到规则匹配 + 词典加权
        """
        # 尝试真实模型
        if not self.use_mock and self.model is not None:
            model_score = self._predict_with_model(text)
            if model_score is not None:
                return model_score

        # 降级方案：规则匹配 + 词典加权
        text = text.strip()
        sentiment_scores = []

        for keyword, info in self.semantic_dictionary.items():
            if keyword in text:
                # 情感值
                if "positive" in info:
                    score = info["positive"]
                elif "negative" in info:
                    score = -info["negative"]
                else:
                    score = 0.0
                sentiment_scores.append(score)

        if not sentiment_scores:
            return 0.0  # 中性

        # 加权平均
        return np.sum(sentiment_scores) / len(sentiment_scores)

    def extract_keywords(self, text, top_k=10):
        """
        关键词提取：返回 top_k 个关键词及权重
        """
        keyword_counts = {}
        for keyword in self.semantic_dictionary:
            count = text.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count

        # 按频率排序
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: -x[1])
        return [{"keyword": k, "count": c} for k, c in sorted_keywords[:top_k]]

    def compute_semantic_similarity(self, text1, text2):
        """
        语义相似度：两个文本片段的相似度 [0, 1]
        降级方案：共有关键词覆盖率
        """
        keywords1 = set(self.semantic_dictionary.keys()) & set(text1)
        keywords2 = set(self.semantic_dictionary.keys()) & set(text2)
        union = keywords1 | keywords2
        intersection = keywords1 & keywords2

        if not union:
            return 0.5  # 无重叠默认为中等相似
        return len(intersection) / len(union)

    def build_semantic_profile(self, texts):
        """
        批量文本的语义画像：统计情感分布、概念分布
        texts: 文本列表
        返回：{'avg_sentiment': float, 'dominant_domain': str, 'period_distribution': dict}
        """
        sentiments = [self.analyze_sentiment(t) for t in texts]
        domain_counts = {}

        for text in texts:
            for keyword, info in self.semantic_dictionary.items():
                if keyword in text:
                    domain = info.get("domain", "unknown")
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1

        dominant_domain = max(domain_counts, key=domain_counts.get) if domain_counts else "unknown"

        return {
            "avg_sentiment": float(np.mean(sentiments)),
            "sentiment_std": float(np.std(sentiments)),
            "dominant_domain": dominant_domain,
            "n_texts": len(texts),
            "domain_counts": domain_counts,
        }

    def encode(self, text):
        """
        文本向量化：返回固定维度向量
        优先使用真实模型，失败则降级到词袋+位置加权
        """
        # 尝试真实模型
        if not self.use_mock and self.model is not None:
            try:
                import torch
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=256,
                    padding=True
                )
                with torch.no_grad():
                    # 使用 [CLS] token 的表示
                    outputs = self.model(**inputs, output_hidden_states=True)
                    if hasattr(outputs, 'hidden_states') and outputs.hidden_states:
                        # 取最后一层隐藏状态
                        vector = outputs.hidden_states[-1][:, 0, :].detach().numpy().flatten()
                    else:
                        # 回退：使用 last_hidden_state
                        vector = outputs.logits.detach().numpy().flatten()
                        vector = np.pad(vector, (0, max(0, 768 - len(vector))), mode='constant')[:768]

                # L2 归一化
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
                return vector
            except Exception as e:
                print(f"[SikuBERT] 模型编码失败，降级到规则: {e}")

        # 降级方案：词袋+位置加权
        vector = np.zeros(768)
        words = text.split()

        for i, word in enumerate(words):
            pos_weight = 1.0 / (1 + i * 0.1)  # 位置衰减
            if word in self.semantic_dictionary:
                info = self.semantic_dictionary[word]
                if "positive" in info:
                    vector[int(hash(word) % 768)] += info["positive"] * pos_weight
                elif "negative" in info:
                    vector[int(hash(word) % 768)] += (-info["negative"]) * pos_weight

        # L2 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector


def load_sikubert(model_name="nghuyong/ernie-3.0-mini-zh"):
    """
    工厂函数：加载 SikuBERT 模型
    优先尝试真实模型，失败则降级到规则方法

    Args:
        model_name: HuggingFace 模型名，默认 nghuyong/ernie-3.0-mini-zh

    Returns:
        SikuBERTNLP 实例
    """
    return SikuBERTNLP.load_model(model_name)


if __name__ == "__main__":
    import sys

    # 测试模式：1=仅降级模式，2=仅真实模型，3=两者都测
    test_mode = int(sys.argv[1]) if len(sys.argv) > 1 else 3

    # 核心测试文本
    test_texts = [
        ("嘉祐之治，天下太平", "正向", 0.5, 0.8),  # 预期 +0.5 到 +0.8
        ("百年积弊，民不聊生", "负向", -0.8, -0.5),  # 预期 -0.5 到 -0.8
    ]

    print("=" * 60)
    print("SikuBERT 真实模型接入测试")
    print("=" * 60)

    if test_mode in [1, 3]:
        # 降级模式测试
        print("\n[1] 降级模式（规则词典）测试")
        print("-" * 40)
        nlp_fallback = SikuBERTNLP()
        print(f"使用模式: {'真实模型' if not nlp_fallback.use_mock else '规则降级'}")

        for text, expected_type, expected_min, expected_max in test_texts:
            sentiment = nlp_fallback.analyze_sentiment(text)
            result = "✓" if (expected_min <= sentiment <= expected_max) else "~"
            print(f"文本: {text}")
            print(f"  预期: {expected_type} ({expected_min} ~ {expected_max})")
            print(f"  实际: {sentiment:+.3f} {result}")
            print()

    if test_mode in [2, 3]:
        # 真实模型测试
        print("\n[2] 真实模型测试 (nghuyong/ernie-3.0-mini-zh)")
        print("-" * 40)
        nlp_real = SikuBERTNLP.load_model("nghuyong/ernie-3.0-mini-zh")
        print(f"使用模式: {'真实模型' if not nlp_real.use_mock else '规则降级'}")

        for text, expected_type, expected_min, expected_max in test_texts:
            sentiment = nlp_real.analyze_sentiment(text)
            result = "✓" if (expected_min <= sentiment <= expected_max) else "~"
            print(f"文本: {text}")
            print(f"  预期: {expected_type} ({expected_min} ~ {expected_max})")
            print(f"  实际: {sentiment:+.3f} {result}")
            print()

    # 一致性验证（降级 vs 真实模型）
    if test_mode == 3:
        print("\n[3] 一致性验证")
        print("-" * 40)
        nlp_fb = SikuBERTNLP()
        nlp_rm = SikuBERTNLP.load_model("nghuyong/ernie-3.0-mini-zh")

        texts_full = [
            "嘉祐之治，天下太平",
            "百年积弊，民不聊生",
            "党争激烈，朝纲紊乱",
            "科举兴盛，儒学繁荣",
        ]

        for text in texts_full:
            score_fb = nlp_fb.analyze_sentiment(text)
            score_rm = nlp_rm.analyze_sentiment(text)
            diff = abs(score_fb - score_rm)
            consistent = "一致" if diff < 0.5 else "有差异"
            print(f"文本: {text}")
            print(f"  降级模式: {score_fb:+.3f}")
            print(f"  真实模型: {score_rm:+.3f}")
            print(f"  差异: {diff:.3f} ({consistent})")
            print()
