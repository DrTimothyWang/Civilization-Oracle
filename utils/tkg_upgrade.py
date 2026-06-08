"""
TKG 知识图谱升级模块 for Civilization-Oracle v2.4
接入 CEGRL 框架用于关系推理（Link Prediction）
"""
import numpy as np
import json

class TKGBuilder:
    """
    时序知识图谱构建器
    替代原有 phase5_kgraph 的简单图结构
    """
    def __init__(self):
        self.nodes = []  # 实体节点
        self.edges = []  # 时序关系边
        self.time_index = {}  # 时间戳索引

    def add_expert(self, expert_id, name, period, lat=None, lng=None):
        """添加专家节点"""
        node = {
            'id': expert_id,
            'name': name,
            'period': period,
            'lat': lat,
            'lng': lng,
            'type': 'expert'
        }
        self.nodes.append(node)

    def add_relation(self, source_id, target_id, rel_type, period, weight=1.0):
        """添加关系边（带时间戳）"""
        edge = {
            'source': source_id,
            'target': target_id,
            'relation': rel_type,
            'period': period,
            'weight': weight,
            'timestamp': self._period_to_timestamp(period)
        }
        self.edges.append(edge)

    def _period_to_timestamp(self, period):
        """时期转时间戳"""
        period_map = {
            '北宋初期': 970, '北宋中期': 1020, '北宋末期': 1100,
            '960-976': 968, '976-997': 986, '997-1022': 1009,
            '1022-1063': 1042, '1063-1067': 1065, '1067-1085': 1076,
            '1085-1127': 1106
        }
        return period_map.get(period, 1000)

    def compute_link_score(self, source_id, target_id):
        """
        计算链接预测分数（简化版 CEGRL 推理）
        返回：[0, 1] 的相似度分数
        """
        # 找到source和target的节点
        src = next((n for n in self.nodes if n['id'] == source_id), None)
        tgt = next((n for n in self.nodes if n['id'] == target_id), None)
        if not src or not tgt:
            return 0.0

        # 地理相似度
        geo_sim = 1.0
        if src.get('lat') and tgt.get('lat'):
            lat_diff = abs(src['lat'] - tgt['lat'])
            geo_sim = max(0, 1 - lat_diff / 10)

        # 时间接近度
        src_time = self._period_to_timestamp(src.get('period', ''))
        tgt_time = self._period_to_timestamp(tgt.get('period', ''))
        time_diff = abs(src_time - tgt_time)
        time_sim = max(0, 1 - time_diff / 100)

        # 综合分数（CEGRL 类似）
        score = 0.6 * geo_sim + 0.4 * time_sim

        return round(score, 4)

    def predict_missing_links(self, threshold=0.7):
        """
        预测缺失链接
        threshold: 分数阈值（>threshold则预测为存在）
        返回：预测边列表
        """
        predicted = []
        node_ids = [n['id'] for n in self.nodes]

        # 遍历所有节点对
        existing = set()
        for e in self.edges:
            existing.add((e['source'], e['target']))

        for src in node_ids:
            for tgt in node_ids:
                if src == tgt:
                    continue
                if (src, tgt) in existing:
                    continue
                score = self.compute_link_score(src, tgt)
                if score >= threshold:
                    predicted.append({
                        'source': src,
                        'target': tgt,
                        'score': score
                    })

        return predicted

    def to_networkx(self):
        """
        导出为 NetworkX 图（用于中心性计算）
        """
        try:
            import networkx as nx
            G = nx.DiGraph()

            for node in self.nodes:
                G.add_node(node['id'], **node)
            for edge in self.edges:
                G.add_edge(edge['source'], edge['target'],
                         relation=edge['relation'], weight=edge['weight'])

            return G
        except ImportError:
            # 降级：返回简单字典
            return {
                'nodes': self.nodes,
                'edges': self.edges
            }

class CEGRLInference:
    """
    CEGRL 关系推理（简化版）
    完整版需要：torch + torch_geometric + cegrl 模型
    """
    def __init__(self):
        self.model = None
        self.use_mock = True

    def infer(self, tkg, source_id, target_id):
        """
        推理 source → target 的关系
        返回：关系类型 + 置信度
        """
        score = tkg.compute_link_score(source_id, target_id)

        # 简化：分数转关系类型
        if score > 0.8:
            rel = '密切合作'
            confidence = score
        elif score > 0.6:
            rel = '同朝为官'
            confidence = score
        elif score > 0.4:
            rel = '地域相近'
            confidence = score
        else:
            rel = '无直接关系'
            confidence = score

        return {
            'relation': rel,
            'confidence': round(confidence, 4),
            'method': 'mock-cegrl'
        }

def build北宋_tkg():
    """构建北宋知识图谱（演示数据）"""
    tkg = TKGBuilder()

    # 添加专家节点
    experts = [
        ('E001', '范仲淹', '北宋中期', 33.0, 115.1),
        ('E002', '欧阳修', '北宋中期', 30.5, 117.0),
        ('E003', '王安石', '北宋中期', 31.2, 116.5),
        ('E004', '司马光', '北宋中期', 34.8, 112.5),
        ('E005', '苏轼', '北宋中期', 30.3, 120.1),
    ]

    for eid, name, period, lat, lng in experts:
        tkg.add_expert(eid, name, period, lat, lng)

    # 添加关系
    relations = [
        ('E001', 'E002', '同榜进士', '北宋中期', 0.9),
        ('E001', 'E004', '政敌', '北宋中期', 0.7),
        ('E002', 'E003', '亦师亦友', '北宋中期', 0.8),
        ('E003', 'E004', '变法与反对', '北宋中期', 0.85),
        ('E002', 'E005', '师徒', '北宋中期', 0.9),
    ]

    for src, tgt, rel, period, weight in relations:
        tkg.add_relation(src, tgt, rel, period, weight)

    return tkg

if __name__ == '__main__':
    # 构建北宋图谱
    tkg = build北宋_tkg()
    print(f"TKG 构建完成: {len(tkg.nodes)} 节点, {len(tkg.edges)} 边")

    # 预测缺失链接
    predicted = tkg.predict_missing_links(threshold=0.5)
    print(f"预测链接: {len(predicted)} 条")

    # 关系推理
    cegrl = CEGRLInference()
    result = cegrl.infer(tkg, 'E001', 'E003')
    print(f"E001→E003 关系推理: {result}")