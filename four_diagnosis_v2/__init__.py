"""
四诊合参 2.0 模块
包含：CNHGIS 地理编码 + 四诊交叉验证框架
"""

from .cnhgis import CNHGISClient, GeoHeatMapper
from .four_diagnosis import (
    FourDiagnosisValidator,
    DiagnosisResult,
    CrossValidationResult,
    compute_four_diagnoses,
)

__all__ = [
    "CNHGISClient",
    "GeoHeatMapper",
    "FourDiagnosisValidator",
    "DiagnosisResult",
    "CrossValidationResult",
    "compute_four_diagnoses",
]
