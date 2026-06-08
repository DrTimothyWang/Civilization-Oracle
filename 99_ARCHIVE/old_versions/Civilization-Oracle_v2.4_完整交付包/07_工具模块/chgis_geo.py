"""
CHGIS 地理编码模块 for Civilization-Oracle v2.4
提供：北南分区、地理压力指数（GeoStress Index）、TSI推理
"""
import numpy as np
import json

# 秦岭-淮河分界线（北南分区阈值）
NORTH_SOUTH_THRESHOLD = 34.0  # 北纬34度

# 历史地理参数
GEO_PARAMS = {
    'qinling_huaihe': 34.0,      # 秦岭-淮河分界线
    'huang_huai': 33.0,          # 黄淮平原南界
    'song_capital_lat': 34.26,   # 北宋都城开封（开封）纬度
    'hangzhou_lat': 30.25,       # 南宋都城杭州
    'north_weight': 1.4,          # 北方压力系数
    'south_weight': 0.8,          # 南方压力系数
    'border_weight': 1.2,        # 边疆压力系数
}


def classify_region(latitude, longitude):
    """
    区域分类：北方/南方/边疆
    基于秦岭-淮河分界线
    """
    lat = float(latitude)
    lng = float(longitude)
    # 边疆判断（西起甘肃，东到东北）
    if lng < 105 or (lng > 115 and lat > 42):
        return 'border'
    elif lat >= NORTH_SOUTH_THRESHOLD:
        return 'north'
    else:
        return 'south'


def compute_geo_stress_index(expert_data):
    """
    地理压力指数（GeoStress Index, GSI）
    整合：专家分布密度 + 区域压力 + 地理稳定性

    参数：
        expert_data: [{'person_id': str, 'lat': float, 'lng': float, 'role': str}, ...]
    返回：{'gsi': float, 'north_ratio': float, 'avg_lat': float, 'regional_breakdown': dict}
    """
    if not expert_data:
        return {'gsi': 0.0, 'north_ratio': 0.0, 'avg_lat': 0.0, 'regional_breakdown': {}}

    latitudes = [float(e.get('lat', 35)) for e in expert_data]
    longitudes = [float(e.get('lng', 115)) for e in expert_data]

    # 区域分类
    regions = [classify_region(lat, lng) for lat, lng in zip(latitudes, longitudes)]
    region_counts = {r: regions.count(r) for r in set(regions)}
    n_total = len(regions)

    # 北方占比
    north_ratio = region_counts.get('north', 0) / n_total

    # 平均纬度（地理中心）
    avg_lat = np.mean(latitudes)

    # 地理压力指数公式
    # GSI = (北方专家压力系数 × 北方占比 + 南方压力系数 × 南方占比 + 边疆压力系数 × 边疆占比)
    gsi = (
        GEO_PARAMS['north_weight'] * (region_counts.get('north', 0) / n_total) +
        GEO_PARAMS['south_weight'] * (region_counts.get('south', 0) / n_total) +
        GEO_PARAMS['border_weight'] * (region_counts.get('border', 0) / n_total)
    )

    # 区域密度修正（专家越密集，GSI放大）
    density_factor = 1.0 + np.log1p(n_total) * 0.1
    gsi = gsi * density_factor

    return {
        'gsi': round(gsi, 4),
        'north_ratio': round(north_ratio, 4),
        'avg_lat': round(avg_lat, 2),
        'n_experts': n_total,
        'regional_breakdown': region_counts,
        'density_factor': round(density_factor, 4)
    }


def tsi_inference(gsi, north_ratio, crisis_threshold=0.15):
    """
    地缘压力推理（TSI Inference）
    基于 GeoStress Index 推断区域稳定性

    参数：
        gsi: 地理压力指数
        north_ratio: 北方专家占比
        crisis_threshold: 危机阈值（默认0.15）
    返回：{'stability': str, 'tsi_score': float, 'recommendation': str}
    """
    # 北宋历史：北方占比>20%时通常对应内战或边疆危机
    if north_ratio > 0.20:
        stability = 'crisis'
        tsi_score = min(gsi * 1.5, 1.0)
    elif north_ratio > 0.15:
        stability = 'warning'
        tsi_score = gsi * 1.2
    else:
        stability = 'stable'
        tsi_score = gsi * 0.8

    # 推荐行动
    recommendations = {
        'crisis': '建议触发 CR-002（北方异常），进行 PSI 异常校正',
        'warning': '建议增加南方专家权重，降低北方偏差',
        'stable': '当前区域分布稳定，无需干预'
    }

    return {
        'stability': stability,
        'tsi_score': round(tsi_score, 4),
        'recommendation': recommendations[stability],
        'crisis_threshold': crisis_threshold
    }


def get_expert_geographic_distribution(expert_ids, cbdb_data=None):
    """
    从 CBDB 数据获取专家的地理分布
    cbdb_data: CBDB CSV 数据（DataFrame或列表）
    返回：专家地理信息列表
    """
    # 模拟：实际应从 CBDB 读取
    fallback_data = [
        {'person_id': '001', 'name': '范仲淹', 'lat': 33.0, 'lng': 115.1, 'role': 'politician'},
        {'person_id': '002', 'name': '欧阳修', 'lat': 30.5, 'lng': 117.0, 'role': 'scholar'},
        {'person_id': '003', 'name': '王安石', 'lat': 31.2, 'lng': 116.5, 'role': 'politician'},
    ]

    # 如果有真实CBDB数据，使用它；否则降级到内嵌数据
    if cbdb_data is not None and len(cbdb_data) > 0:
        return cbdb_data[:len(expert_ids)] if len(cbdb_data) >= len(expert_ids) else cbdb_data
    else:
        return fallback_data[:len(expert_ids)] if len(expert_ids) <= len(fallback_data) else fallback_data


def geo_psi_correction(base_psi, gsi, tsi_score=None):
    """
    基于地理压力指数的 PSI 校正
    地理压力高时，PSI 应上调（风险更高）
    """
    # 校正公式：PSI' = PSI × (1 + (GSI - 1) × 0.5)
    correction_factor = 1 + (gsi - 1) * 0.5
    corrected_psi = base_psi * correction_factor

    return {
        'base_psi': base_psi,
        'corrected_psi': round(max(0.0, min(1.0, corrected_psi)), 4),
        'gsi': gsi,
        'correction_factor': round(correction_factor, 4)
    }


if __name__ == '__main__':
    # 测试地理编码
    expert_data = [
        {'person_id': '001', 'lat': 36.5, 'lng': 116.0},
        {'person_id': '002', 'lat': 35.2, 'lng': 115.5},
        {'person_id': '003', 'lat': 34.8, 'lng': 117.2},
        {'person_id': '004', 'lat': 33.5, 'lng': 116.8},
        {'person_id': '005', 'lat': 31.0, 'lng': 117.5},
    ]

    gsi_result = compute_geo_stress_index(expert_data)
    print(f"地理压力指数: {gsi_result}")

    tsi = tsi_inference(gsi_result['gsi'], gsi_result['north_ratio'])
    print(f"地缘压力推理: {tsi}")

    corrected = geo_psi_correction(0.65, gsi_result['gsi'], tsi['tsi_score'])
    print(f"PSI地理校正: {corrected}")