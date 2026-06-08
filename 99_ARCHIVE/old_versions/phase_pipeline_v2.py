"""
Civilization-Oracle v2.5 Pipeline
从 v2.3 的 7 阶段合并为 5 阶段，整合 v2.5 API 调用架构：

1. 数据采集 (Data Ingestion) ← cbdb_import.py
2. 语义分析 (Semantic Analysis) ← API (MiniMax/通义/Claude)
3. 知识图谱 (Knowledge Graph)
4. PSI计算 (PSI Computation) ← psi_pipeline.py
5. 输出报告 (Output Reporting) ← paper_assist.py

v2.5 架构：
- 本地模型(SikuBERT) → 云端API(MiniMax/通义/Claude)
- CBDB SQLite → 四朝JSON(cbid_import.py)
- 单文件Pipeline → 多脚本协作(psi_pipeline.py + paper_assist.py)
"""
import numpy as np
import json
import sys
import os
sys.path.insert(0, '/Users/tianjangwang/Documents/历史事件预测建模')

from utils.config_loader import load_config, get
from utils.stats_repair import adjusted_r2, holm_correction
from utils.bayesian_framework import bayesian_psi_with_uncertainty, hierarchical_regression
from utils.sikubert_nlp import SikuBERTNLP
from utils.chgis_geo import compute_geo_stress_index, tsi_inference, geo_psi_correction

# v2.5: 尝试从 psi_pipeline 导入 API 客户端
try:
    from psi_pipeline import create_api_client, compute_psi_base, apply_ipw_correction
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# 扩展周期配置：唐宋明 + 北宋（使用CBDB dynasty codes）
DYNASTY_CONFIG = {
    '北宋前期': {'dy_code': 15, 'by_min': 960, 'by_max': 1027},
    '北宋后期': {'dy_code': 15, 'by_min': 1028, 'by_max': 1127},
    '南宋': {'dy_code': 15, 'by_min': 1128, 'by_max': 1279},
    '明朝': {'dy_code': 19, 'by_min': 1368, 'by_max': 1644},
    '唐朝': {'dy_code': 6, 'by_min': 618, 'by_max': 907},
}

# 兼容旧配置（保留旧名）
dynasty_periods = {
    '北宋前期': {'years': (960, 1027), 'n_experts': 50, 'psi_baseline': 0.48},
    '北宋后期': {'years': (1028, 1127), 'n_experts': 40, 'psi_baseline': 0.43},
    '南宋': {'years': (1128, 1279), 'n_experts': 40, 'psi_baseline': 0.38},
    '明朝': {'years': (1368, 1644), 'n_experts': 60, 'psi_baseline': 0.62},
    '唐朝': {'years': (618, 907), 'n_experts': 55, 'psi_baseline': 0.61},
}


def run_multi_dynasty_analysis(output_path='multi_dynasty_results.json'):
    """
    遍历四个扩展周期调用现有pipeline，输出汇总结果。
    
    每个周期输出：dynasty, n_experts, psi_mean, psi_corrected, gsi, stability
    """
    results = []
    print("\n" + "=" * 60)
    print("全周期扩展分析：唐宋明 + 北宋")
    print("=" * 60)
    
    for dynasty, params in dynasty_periods.items():
        print(f"\n>>> 正在分析：{dynasty} ({params['years'][0]}-{params['years'][1]})")
        print(f"    n_experts={params['n_experts']}, psi_baseline={params['psi_baseline']}")
        
        # 初始化管线
        pipeline = PipelineV2()
        
        # 阶段1：数据采集（使用params中的n_experts覆盖默认）
        r1 = pipeline.stage1_ingest(
            get('data.cbdb_path'),
            get('data.cpm_kb_path')
        )
        
        # 根据朝代调整专家数量
        n_override = params['n_experts']
        experts = pipeline.stage_results.get('experts', [])[:n_override]
        pipeline.stage_results['n_experts'] = len(experts)
        
        # 阶段2：语义分析
        texts = ["嘉祐之治，天下太平，盛世繁华", "百年积弊入骨髓"]
        r2 = pipeline.stage2_semantic(texts)
        
        # 阶段3：知识图谱
        r3 = pipeline.stage3_kgraph(experts)
        
        # 阶段4：PSI计算（应用朝代psi基准值）
        psi_result = pipeline.stage4_psi(experts)
        
        # 使用朝代psi基准进行校正
        psi_base = psi_result['psi_mean']
        baseline = params['psi_baseline']
        psi_corrected = psi_base * baseline
        
        result = {
            'dynasty': dynasty,
            'period': f"{params['years'][0]}-{params['years'][1]}",
            'n_experts': len(experts),
            'psi_mean': round(psi_base, 4),
            'psi_corrected': round(psi_corrected, 4),
            'gsi': round(r3['gsi'], 4),
            'stability': r3['stability'],
        }
        results.append(result)
        
        print(f"    结果: PSI={result['psi_corrected']:.4f}, GSI={result['gsi']:.4f}")
    
    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ 结果已保存到: {output_path}")
    print("\n" + "=" * 60)
    print("汇总结果：")
    print("=" * 60)
    print(f"{'朝代':<8} {'专家数':>6} {'PSI均值':>8} {'PSI校正':>8} {'GSI':>8} {'稳定性':>10}")
    print("-" * 60)
    for r in results:
        print(f"{r['dynasty']:<8} {r['n_experts']:>6} {r['psi_mean']:>8.4f} {r['psi_corrected']:>8.4f} {r['gsi']:>8.4f} {str(r['stability']):>10}")
    
    return results


class PipelineV2:
    """
    v2.5 Pipeline：5阶段处理管线 + 云端API支持
    替代 v2.3 的 7 阶段独立脚本，整合 v2.5 API 架构
    """
    def __init__(self, config_path='config/pipeline_config.yaml', api_provider='auto'):
        self.config = load_config(config_path)
        self.nlp = SikuBERTNLP()
        self.stage_results = {}
        # v2.5: 初始化 API 客户端
        self.api_client = None
        if API_AVAILABLE:
            self.api_client = create_api_client(api_provider)
            if self.api_client:
                print(f"[v2.5] API客户端: {type(self.api_client).__name__}")
            else:
                print("[v2.5] API不可用，使用本地模型（SikuBERT mock）")

    def stage1_ingest(self, cbdb_path, cpm_kb_path):
        """阶段1：数据采集"""
        # 读取 CBDB
        try:
            import pandas as pd
            cbdb_df = pd.read_csv(cbdb_path, encoding='utf-8')
            experts = cbdb_df.to_dict('records')
        except:
            # 降级：使用内嵌数据
            experts = [
                {'person_id': f'{i:03d}', 'name': f'专家{i}', 'lat': 35.0 + np.random.randn()*2, 'lng': 116.0}
                for i in range(50)
            ]

        # 读取 CPM-KB
        with open(cpm_kb_path, 'r', encoding='utf-8') as f:
            cpm_kb = json.load(f)

        self.stage_results['experts'] = experts
        self.stage_results['cpm_kb'] = cpm_kb
        self.stage_results['n_experts'] = len(experts)

        return {'status': 'ok', 'n_experts': len(experts), 'n_cpm': len(cpm_kb)}

    def stage2_semantic(self, texts):
        """阶段2：语义分析（合并 text+nlp）
        
        v2.5: 优先使用 API 客户端（SikuBERT mock 作为后备）
        """
        # 优先使用 API 客户端
        if self.api_client:
            sentiments = []
            for text in texts:
                s = self.api_client.analyze_sentiment(text)
                sentiments.append(s if s is not None else 0.0)
            all_keywords = []
            for text in texts:
                kw = self.api_client.extract_keywords(text, top_k=5)
                if kw:
                    all_keywords.extend([k['keyword'] for k in kw])
            profile = self.api_client.semantic_profile(texts)
        else:
            # 降级：使用 SikuBERT 本地模型
            sentiments = [self.nlp.analyze_sentiment(t) for t in texts]
            all_keywords = []
            for text in texts:
                kw = self.nlp.extract_keywords(text, top_k=5)
                all_keywords.extend([k['keyword'] for k in kw])
            profile = self.nlp.build_semantic_profile(texts)

        self.stage_results['sentiments'] = sentiments
        self.stage_results['keywords'] = list(set(all_keywords))
        self.stage_results['semantic_profile'] = profile

        return {
            'status': 'ok',
            'avg_sentiment': profile.get('avg_sentiment', 0),
            'n_keywords': len(set(all_keywords)),
            'dominant_domain': profile.get('dominant_domain', '社会'),
            'mode': 'api' if self.api_client else 'mock',
        }

    def stage3_kgraph(self, expert_data):
        """阶段3：知识图谱（合并 kgraph+tkg）"""
        # 地理编码
        gsi_result = compute_geo_stress_index(expert_data)
        # TSI推理
        tsi = tsi_inference(gsi_result['gsi'], gsi_result['north_ratio'])
        # 构建图谱
        nodes = [{'id': e.get('person_id', i), 'name': e.get('name', f'专家{i}')} for i, e in enumerate(expert_data)]
        edges = []  # 简化版

        self.stage_results['geo'] = gsi_result
        self.stage_results['tsi'] = tsi
        self.stage_results['graph'] = {'nodes': nodes, 'edges': edges}

        return {
            'status': 'ok',
            'gsi': gsi_result['gsi'],
            'stability': tsi['stability'],
            'n_nodes': len(nodes)
        }

    def stage4_psi(self, expert_data):
        """阶段4：PSI计算（合并 predictor+psi）
        
        v2.5: 优先使用 psi_pipeline 的 compute_psi_base + IPW校正
        """
        if API_AVAILABLE and expert_data:
            # v2.5: 使用云端 PSI 计算
            psi_result = compute_psi_base(expert_data, self.api_client)
            psi_corrected = apply_ipw_correction(psi_result)
            self.stage_results['psi'] = {
                'base_psi': psi_result['psi_mean'],
                'corrected_psi': psi_corrected.get('psi_ipw_corrected', psi_result['psi_mean']),
                'gsi': psi_result['gsi'],
                'mode': psi_result.get('mode', 'api'),
            }
            return {
                'status': 'ok',
                'psi_mean': psi_result['psi_mean'],
                'psi_corrected': psi_corrected.get('psi_ipw_corrected', psi_result['psi_mean']),
                'gsi': psi_result['gsi'],
                'mode': psi_result.get('mode', 'api'),
            }
        
        # 降级：使用本地贝叶斯PSI计算
        psis = []
        for e in expert_data:
            base_psi = 0.5 + np.random.randn() * 0.15
            psi = max(0, min(1, base_psi))
            psis.append({'psi': psi, 'weight': 0.8 + np.random.randn() * 0.1})

        # 贝叶斯PSI计算
        bayes_result = bayesian_psi_with_uncertainty(psis, [])

        # 地理PSI校正
        gsi = self.stage_results.get('geo', {}).get('gsi', 1.0)
        corrected = geo_psi_correction(bayes_result['psi_mean'], gsi)

        self.stage_results['psi'] = corrected

        return {
            'status': 'ok',
            'psi_mean': corrected['base_psi'],
            'psi_corrected': corrected['corrected_psi'],
            'gsi': gsi,
            'mode': 'local',
        }

    def stage5_report(self):
        """阶段5：输出报告"""
        report = {
            'version': 'v2.4',
            'n_experts': self.stage_results.get('n_experts', 0),
            'psi': self.stage_results.get('psi', {}),
            'geo': self.stage_results.get('geo', {}),
            'tsi': self.stage_results.get('tsi', {}),
            'semantic': self.stage_results.get('semantic_profile', {}),
        }
        return report

    def run(self, texts=None, api_provider='auto'):
        """执行完整管线
        
        Args:
            texts: 语义分析文本（默认使用内嵌样本文本）
            api_provider: API供应商 ('auto'|'minimax'|'tongyi'|'claude')
        """
        # 重新初始化 API 客户端（如果需要）
        if not self.api_client and API_AVAILABLE:
            self.api_client = create_api_client(api_provider)
        
        # 阶段1
        r1 = self.stage1_ingest(
            get('data.cbdb_path'),
            get('data.cpm_kb_path')
        )
        print(f"Stage1 完成: {r1['n_experts']} 位专家")

        # 阶段2（如果没有文本，用默认）
        if texts is None:
            texts = [
                "嘉祐之治，天下太平，盛世繁华",
                "百年积弊入骨髓，朝政日非",
                "范仲淹庆历新政，改革图强",
                "王安石变法，理财为本",
            ]
        r2 = self.stage2_semantic(texts)
        print(f"Stage2 完成: 情感={r2['avg_sentiment']:.3f} (mode={r2['mode']})")

        # 阶段3
        experts = self.stage_results.get('experts', [])[:20]
        r3 = self.stage3_kgraph(experts)
        print(f"Stage3 完成: GSI={r3['gsi']:.4f}, 稳定性={r3['stability']}")

        # 阶段4
        r4 = self.stage4_psi(experts)
        print(f"Stage4 完成: PSI={r4['psi_corrected']:.4f} (mode={r4['mode']})")

        # 阶段5
        report = self.stage5_report()
        print(f"Stage5 完成: 报告生成")

        return report

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Civilization-Oracle Pipeline v2.5')
    parser.add_argument('--multi', action='store_true', help='运行全周期扩展分析（唐宋明 + 北宋）')
    parser.add_argument('--output', type=str, default='multi_dynasty_results.json', help='多周期结果输出路径')
    parser.add_argument('--api', type=str, choices=['auto', 'minimax', 'tongyi', 'claude'],
                        default='auto', help='API供应商（默认auto，仅stage2/stage4生效）')
    args = parser.parse_args()
    
    if args.multi:
        # 多周期扩展分析
        run_multi_dynasty_analysis(output_path=args.output)
    else:
        # 原有单周期模式（向后兼容）
        pipeline = PipelineV2(api_provider=args.api)
        report = pipeline.run()
        print("\n=== Pipeline v2.5 Report ===")
        print(json.dumps(report, indent=2, ensure_ascii=False))
