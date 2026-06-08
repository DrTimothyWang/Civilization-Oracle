"""
Civilization-Oracle v3.0: TKG Stack Upgrade
=============================================
Target: MRR 29.63% → 36-40%

三大升级方向：
1. DiMNet (ACL 2025): 多跨度解耦策略，活跃/稳定特征分离
2. TransFIR (ICLR 2026): VQ码本新兴实体处理
3. TGL-LLM: 时序图学习+LLM深度融合

Baseline (v2.6): MRR = 29.63%
Expected (v3.0): MRR = 36-40%
"""

from .dimnet import DiMNetEngine
from .transfir import TransFIREngine
from .tgl_llm import TGLLLMEngine
from .tkg_predictor import TKGv3Predictor

__all__ = [
    "DiMNetEngine",
    "TransFIREngine",
    "TGLLLMEngine",
    "TKGv3Predictor",
]
