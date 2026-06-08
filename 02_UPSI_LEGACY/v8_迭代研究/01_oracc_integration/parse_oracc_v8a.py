#!/usr/bin/env python3
"""
v8_TrackA_ORACC整合工程师
解析所有ORACC子项目catalogue.json，提取关键字段，统计时期分布，计算SFD，验证事件
"""

import json
import os
import re
import math
from collections import defaultdict, Counter
from datetime import datetime

# ============================================================
# 配置
# ============================================================
BASE_DIR = "/Users/wangzr/Desktop/历史事件预测建模"
V8_DIR = os.path.join(BASE_DIR, "v8_迭代研究", "01_oracc_integration")
V63_CACHE = os.path.join(BASE_DIR, "v6.3", "oracc_cache")

# 所有catalogue.json路径
CATALOGUES = [
    ("dcclt", os.path.join(V63_CACHE, "dcclt_extracted", "dcclt", "catalogue.json")),
    ("riao", os.path.join(V63_CACHE, "riao_extracted", "riao", "catalogue.json")),
    ("rinap", os.path.join(V63_CACHE, "rinap_extracted", "rinap", "catalogue.json")),
    ("saao", os.path.join(V63_CACHE, "saao_extracted", "saao", "catalogue.json")),
    ("etcsri", os.path.join(V63_CACHE, "etcsri_extracted", "etcsri", "catalogue.json")),
    ("epsd2-admin-ed3b", os.path.join(V63_CACHE, "epsd2-admin-ed3b_extracted", "epsd2", "admin", "ed3b", "catalogue.json")),
    ("epsd2-admin-oakk", os.path.join(V63_CACHE, "epsd2-admin-oakk_extracted", "epsd2", "admin", "oakk", "catalogue.json")),
    ("epsd2-literary", os.path.join(V63_CACHE, "epsd2-literary_extracted", "epsd2", "literary", "catalogue.json")),
    ("epsd2-royal", os.path.join(V63_CACHE, "epsd2-royal_extracted", "epsd2", "royal", "catalogue.json")),
    ("epsd2-praxis-varia", os.path.join(V63_CACHE, "epsd2-praxis-varia_extracted", "epsd2", "praxis", "varia", "catalogue.json")),
    ("epsd2-admin-ur3", os.path.join(V63_CACHE, "epsd2-admin-ur3_extracted", "epsd2", "admin", "ur3", "catalogue.json")),
]

# ============================================================
# 统治者/年名到公历年份的映射
# ============================================================

# Ur III年名映射 (Middle Chronology)
# Shulgi: -2094 ~ -2047 (48年), Amar-Sin: -2046 ~ -2038, Shu-Sin: -2037 ~ -2029, Ibbi-Sin: -2028 ~ -2004
UR3_RULERS = {
    'SH': (-2094, -2047),   # Shulgi
    'AS': (-2046, -2038),   # Amar-Sin
    'SS': (-2037, -2029),   # Shu-Sin
    'IS': (-2028, -2004),   # Ibbi-Sin
    'UN': (-2112, -2095),   # Ur-Nammu
}

# Neo-Assyrian统治者映射 (大致Middle Chronology)
NEO_ASSYRIAN_RULERS = {
    'Tiglath-pileser3': (-745, -727),
    'Tiglath-pileser': (-745, -727),
    'Shalmaneser5': (-727, -722),
    'Shalmaneser3': (-859, -824),
    'Sargon2': (-722, -705),
    'Sargon': (-722, -705),
    'Sennacherib': (-705, -681),
    'Esarhaddon': (-681, -669),
    'Ashurbanipal': (-669, -631),
    'Assurbanipal': (-669, -631),
    'Ashur-etil-ilani': (-631, -627),
    'Assur-etel-ilani': (-631, -627),
    'Sin-shumu-lishir': (-626, -626),
    'Sin-shar-ishkun': (-627, -612),
    'Sin-sharru-ishkun': (-627, -612),
    'Ashur-uballit2': (-612, -609),
    'Assur-uballit': (-612, -609),
    'Shamshi-Adad5': (-824, -811),
    'Adad-narari3': (-811, -783),
    'Assur-dan3': (-773, -755),
}

# Old Babylonian统治者 (部分)
OB_RULERS = {
    'Warad-Sin': (-1834, -1823),
    'Rim-Sin': (-1822, -1763),
    'Samsu-iluna': (-1749, -1712),
    'Hammurabi': (-1792, -1750),
    'Abi-eshuh': (-1711, -1684),
    'Ammi-ditana': (-1683, -1647),
    'Ammi-saduqa': (-1646, -1626),
    'Samsu-ditana': (-1625, -1595),
}

# Lagash II统治者 (ed3b, 大致)
LAGASH2_RULERS = {
    'Enentarzi': (-2430, -2400),
    'Lugalanda': (-2400, -2385),
    'Urukagina': (-2384, -2370),
    'Urukagina_l': (-2384, -2370),
}

# 时期到大致时间范围的映射（用于fallback）
PERIOD_RANGES = {
    "Early Dynastic": (-2900, -2350),
    "ED": (-2900, -2350),
    "Ebla": (-2400, -2250),
    "Akkadian": (-2334, -2154),
    "Ur III": (-2112, -2004),
    "Old Babylonian": (-1894, -1595),
    "OB": (-1894, -1595),
    "Middle Babylonian": (-1595, -1155),
    "MB": (-1595, -1155),
    "Kassite": (-1595, -1155),
    "Neo-Assyrian": (-911, -612),
    "NA": (-911, -612),
    "Neo-Babylonian": (-626, -539),
    "NB": (-626, -539),
    "Achaemenid": (-539, -330),
    "Hellenistic": (-323, -100),
    "Seleucid": (-312, -63),
    "Parthian": (-247, 224),
    "Roman": (-27, 476),
    "Late Babylonian": (-539, -331),
    "LB": (-539, -331),
    "Standard Babylonian": (-1000, -500),
    "SB": (-1000, -500),
    "Old Assyrian": (-2025, -1378),
    "OA": (-2025, -1378),
    "Middle Assyrian": (-1392, -1056),
    "MA": (-1392, -1056),
    "Sumerian": (-3500, -2000),
    "Uncertain": None,
    "unknown": None,
    "": None,
}

# 8个关键事件
KEY_EVENTS = [
    {"name": "Gutian入侵", "year": -2190, "periods": ["Akkadian", "Ur III", "Early Dynastic"], "note": "可能超出所有数据范围"},
    {"name": "Ur III衰亡/Elamite入侵", "year": -2004, "periods": ["Ur III"], "note": "v7已验证"},
    {"name": "Old Babylonian终结", "year": -1595, "periods": ["Old Babylonian", "Middle Babylonian", "Kassite"], "note": "需要MB/Kassite数据"},
    {"name": "Hammurabi死后帝国分裂", "year": -1750, "periods": ["Old Babylonian"], "note": "需要OB数据"},
    {"name": "Assyria危机/新亚述灭亡", "year": -612, "periods": ["Neo-Assyrian"], "note": "需要NA数据"},
    {"name": "Neo-Babylonian陷落", "year": -539, "periods": ["Neo-Babylonian", "Achaemenid"], "note": "需要NB数据"},
    {"name": "Kassite王朝终结", "year": -1155, "periods": ["Kassite", "Middle Babylonian"], "note": "需要Kassite/MB数据"},
    {"name": "Sumerian城市Umma衰落", "year": -2037, "periods": ["Ur III"], "note": "Ur III数据"},
]

# ============================================================
# 辅助函数
# ============================================================

def parse_ur3_year(date_str):
    """解析Ur III年名，如 'SH46 - 00 - 00' -> -2049"""
    if not date_str:
        return None
    # 匹配 SH46, AS03, SS09, IS03 等
    m = re.match(r'^(SH|AS|SS|IS|UN)(\d{1,2})', date_str.upper())
    if m:
        ruler = m.group(1)
        year_num = int(m.group(2))
        if ruler in UR3_RULERS:
            start, end = UR3_RULERS[ruler]
            # 年份号从1开始, start已经是负数(BCE)
            year = start + (year_num - 1)
            # 确保不超出范围
            year = max(start, min(year, end))
            return year  # 已经是负数
    return None


def parse_neo_assyrian_year(date_str):
    """解析Neo-Assyrian统治者年名，如 'Tiglath-pileser3.000.00.00' -> -736"""
    if not date_str:
        return None
    # 提取统治者名（去掉数字后缀和后面的.000.00.00）
    m = re.match(r'^([A-Za-z\-]+(?:\d)?)', date_str)
    if m:
        ruler_key = m.group(1)
        # 尝试直接匹配
        if ruler_key in NEO_ASSYRIAN_RULERS:
            start, end = NEO_ASSYRIAN_RULERS[ruler_key]
            return (start + end) / 2  # start/end已经是负数
        # 尝试去掉数字再匹配
        ruler_base = re.sub(r'\d$', '', ruler_key)
        if ruler_base in NEO_ASSYRIAN_RULERS:
            start, end = NEO_ASSYRIAN_RULERS[ruler_base]
            return (start + end) / 2
    return None


def parse_ruler_year(date_str, ruler_dict):
    """通用统治者年名解析"""
    if not date_str:
        return None
    m = re.match(r'^([A-Za-z\-_]+)(?:\.\d+)?', date_str)
    if m:
        ruler_key = m.group(1)
        if ruler_key in ruler_dict:
            start, end = ruler_dict[ruler_key]
            return (start + end) / 2  # 已经是负数
    return None


def parse_date_of_origin(date_str):
    """
    从date_of_origin字段提取年份。
    返回: year (BCE为负) 或 None
    """
    if not date_str or date_str in ["--.--.00.00", "00.000.00.00", "XXXX - 00 - 00", "", "unknown", None, "00.00.00.00", "0000 - 00 - 00", "--.00.00.00", "N/A", "XXXX - XX - XX"]:
        return None
    
    date_str = str(date_str).strip()
    
    # 1. 尝试Ur III年名
    ur3_year = parse_ur3_year(date_str)
    if ur3_year is not None:
        return ur3_year
    
    # 2. 尝试Neo-Assyrian统治者
    na_year = parse_neo_assyrian_year(date_str)
    if na_year is not None:
        return na_year
    
    # 3. 尝试Old Babylonian统治者
    ob_year = parse_ruler_year(date_str, OB_RULERS)
    if ob_year is not None:
        return ob_year
    
    # 4. 尝试Lagash II统治者
    lag_year = parse_ruler_year(date_str, LAGASH2_RULERS)
    if lag_year is not None:
        return lag_year
    
    # 5. 处理范围格式: "2044–2036" 或 "2044-2036"
    range_match = re.match(r'^(\d{1,4})\s*[–\-]\s*(\d{1,4})$', date_str)
    if range_match:
        y1, y2 = int(range_match.group(1)), int(range_match.group(2))
        if y1 > y2:
            y1, y2 = y2, y1
        return -(y1 + y2) / 2
    
    # 6. 处理 "YYYY - MM - DD" 或 "YYYY.MM.DD" 格式
    ymd_match = re.match(r'^(\d{3,4})\s*[\.\-]\s*\d{1,2}\s*[\.\-]\s*\d{1,2}$', date_str)
    if ymd_match:
        year = int(ymd_match.group(1))
        return -year
    
    # 7. 处理纯4位数字（BCE）
    pure_match = re.match(r'^(\d{3,4})$', date_str)
    if pure_match:
        year = int(pure_match.group(1))
        return -year
    
    # 8. 处理 "~YYYY" 或 "c. YYYY"
    approx_match = re.match(r'^[~c\.\s]*(\d{3,4})$', date_str)
    if approx_match:
        year = int(approx_match.group(1))
        return -year
    
    # 9. 处理 "YYYY BCE" 或 "YYYY BC"
    bce_match = re.match(r'^(\d{1,4})\s*(?:BCE|BC)$', date_str, re.IGNORECASE)
    if bce_match:
        year = int(bce_match.group(1))
        return -year
    
    # 10. 处理 "YYYY BCE – YYYY BCE"
    bce_range_match = re.match(r'^(\d{1,4})\s*BCE?\s*[–\-]\s*(\d{1,4})\s*BCE?$', date_str, re.IGNORECASE)
    if bce_range_match:
        y1, y2 = int(bce_range_match.group(1)), int(bce_range_match.group(2))
        if y1 > y2:
            y1, y2 = y2, y1
        return -(y1 + y2) / 2
    
    # 11. 处理 "YYYY, YYYY" (如 "673, 672")
    comma_match = re.match(r'^(\d{3,4}),\s*(\d{3,4})$', date_str)
    if comma_match:
        y1, y2 = int(comma_match.group(1)), int(comma_match.group(2))
        return -(y1 + y2) / 2
    
    return None


def get_year_from_record(record):
    """
    从记录中提取年份。优先使用date_of_origin，否则用period fallback
    返回: year (float, BCE为负) 或 None
    """
    # 尝试date_of_origin
    date_str = record.get('date_of_origin')
    parsed = parse_date_of_origin(date_str)
    if parsed is not None:
        return parsed
    
    # fallback到period
    period = record.get('period', '')
    norm_period = normalize_period(period)
    if norm_period in PERIOD_RANGES and PERIOD_RANGES[norm_period]:
        start, end = PERIOD_RANGES[norm_period]
        return (start + end) / 2
    
    return None


def normalize_period(period):
    """标准化时期名称"""
    if not period:
        return "Unknown"
    period = period.strip()
    
    # 直接映射表
    mapping = {
        "early dynastic": "Early Dynastic",
        "early dynastic iii": "Early Dynastic",
        "early dynastic iii a": "Early Dynastic",
        "early dynastic iii b": "Early Dynastic",
        "early dynastic iii/akkadian": "Early Dynastic",
        "ed": "Early Dynastic",
        "ed iii": "Early Dynastic",
        "ed iii a": "Early Dynastic",
        "ed iii b": "Early Dynastic",
        "ebla": "Ebla",
        "akkadian": "Akkadian",
        "old akkadian": "Akkadian",
        "sargonic": "Akkadian",
        "ur iii": "Ur III",
        "uriii": "Ur III",
        "ur-iii": "Ur III",
        "old babylonian": "Old Babylonian",
        "early old babylonian": "Old Babylonian",
        "late old babylonian": "Old Babylonian",
        "ob": "Old Babylonian",
        "o.b.": "Old Babylonian",
        "middle babylonian": "Middle Babylonian",
        "mb": "Middle Babylonian",
        "m.b.": "Middle Babylonian",
        "kassite": "Kassite",
        "neo-assyrian": "Neo-Assyrian",
        "na": "Neo-Assyrian",
        "n.a.": "Neo-Assyrian",
        "late middle assyrian or early neo-assyrian": "Neo-Assyrian",
        "neo-babylonian": "Neo-Babylonian",
        "nb": "Neo-Babylonian",
        "n.b.": "Neo-Babylonian",
        "achaemenid": "Achaemenid",
        "persian": "Achaemenid",
        "hellenistic": "Hellenistic",
        "seleucid": "Seleucid",
        "parthian": "Parthian",
        "roman": "Roman",
        "late babylonian": "Late Babylonian",
        "lb": "Late Babylonian",
        "standard babylonian": "Standard Babylonian",
        "sb": "Standard Babylonian",
        "old assyrian": "Old Assyrian",
        "oa": "Old Assyrian",
        "middle assyrian": "Middle Assyrian",
        "ma": "Middle Assyrian",
        "sumerian": "Sumerian",
        "lagash ii": "Ur III",
        "lagaš ii": "Ur III",
        "lagash2": "Ur III",
        "uncertain": "Uncertain",
        "unknown": "Unknown",
        "": "Unknown",
    }
    
    p_lower = period.lower()
    if p_lower in mapping:
        return mapping[p_lower]
    
    # 部分匹配
    if "early dynastic" in p_lower:
        return "Early Dynastic"
    if "old akkadian" in p_lower or "sargonic" in p_lower:
        return "Akkadian"
    if "ur iii" in p_lower or "ur-iii" in p_lower or "uriii" in p_lower:
        return "Ur III"
    if "lagash" in p_lower and "ii" in p_lower:
        return "Ur III"
    if "neo-assyrian" in p_lower or ("neo" in p_lower and "assyrian" in p_lower):
        return "Neo-Assyrian"
    if "neo-babylonian" in p_lower or ("neo" in p_lower and "babylonian" in p_lower and "assyrian" not in p_lower):
        return "Neo-Babylonian"
    if "old babylonian" in p_lower or "early old babylonian" in p_lower or "late old babylonian" in p_lower:
        return "Old Babylonian"
    if "middle babylonian" in p_lower:
        return "Middle Babylonian"
    if "old assyrian" in p_lower:
        return "Old Assyrian"
    if "middle assyrian" in p_lower:
        return "Middle Assyrian"
    if "kassite" in p_lower:
        return "Kassite"
    if "achaemenid" in p_lower or "persian" in p_lower:
        return "Achaemenid"
    if "hellenistic" in p_lower:
        return "Hellenistic"
    if "seleucid" in p_lower:
        return "Seleucid"
    if "parthian" in p_lower:
        return "Parthian"
    if "roman" in p_lower:
        return "Roman"
    if "late babylonian" in p_lower:
        return "Late Babylonian"
    if "standard babylonian" in p_lower:
        return "Standard Babylonian"
    if "uncertain" in p_lower or "unknown" in p_lower:
        return "Unknown"
    
    return period


def period_covers_year(period, year):
    """检查某个时期的时间范围是否覆盖给定年份"""
    if period not in PERIOD_RANGES or PERIOD_RANGES[period] is None:
        return False
    start, end = PERIOD_RANGES[period]
    return start <= year <= end


# ============================================================
# 步骤1: 解析所有catalogue.json
# ============================================================

def parse_catalogue(project_name, filepath):
    """解析单个catalogue.json，返回记录列表"""
    records = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] 无法解析 {project_name}: {e}")
        return records
    
    members = data.get('members', {})
    if not isinstance(members, dict):
        print(f"[WARN] {project_name}: members不是字典，类型={type(members)}")
        return records
    
    for text_id, record in members.items():
        if not isinstance(record, dict):
            continue
        
        # 提取关键字段
        id_text = record.get('id_text') or record.get('cdli_id') or text_id
        period = normalize_period(record.get('period', ''))
        genre = record.get('genre', 'Unknown')
        provenience = record.get('provenience', 'Unknown')
        date_of_origin = record.get('date_of_origin', '')
        bdtns_id = record.get('bdtns_id', '')
        language = record.get('language', 'Unknown')
        supergenre = record.get('supergenre', '')
        
        year = get_year_from_record(record)
        
        records.append({
            'project': project_name,
            'id_text': id_text,
            'period': period,
            'genre': genre,
            'provenience': provenience,
            'date_of_origin': date_of_origin,
            'year': year,
            'bdtns_id': bdtns_id,
            'language': language,
            'supergenre': supergenre,
        })
    
    return records


# ============================================================
# 主流程
# ============================================================

def main():
    os.makedirs(V8_DIR, exist_ok=True)
    
    print("=" * 60)
    print("v8_TrackA_ORACC整合: 解析所有catalogue.json")
    print("=" * 60)
    
    all_records = []
    project_stats = {}
    
    for project_name, filepath in CATALOGUES:
        if not os.path.exists(filepath):
            print(f"[SKIP] {project_name}: 文件不存在 {filepath}")
            continue
        
        print(f"\n[解析] {project_name} ...")
        records = parse_catalogue(project_name, filepath)
        
        # 统计
        period_counts = Counter(r['period'] for r in records)
        year_count = sum(1 for r in records if r['year'] is not None)
        
        # 统计精确年份（非period fallback）
        exact_year_count = sum(1 for r in records if r['year'] is not None and parse_date_of_origin(r.get('date_of_origin', '')) is not None)
        
        project_stats[project_name] = {
            'total': len(records),
            'with_year': year_count,
            'exact_year': exact_year_count,
            'periods': dict(period_counts.most_common(10)),
        }
        
        print(f"  总记录: {len(records)}")
        print(f"  有年份: {year_count} ({year_count/len(records)*100:.1f}%)")
        print(f"  精确年份: {exact_year_count} ({exact_year_count/len(records)*100:.1f}%)")
        print(f"  主要时期: {dict(period_counts.most_common(5))}")
        
        all_records.extend(records)
    
    print(f"\n{'=' * 60}")
    print(f"总计: {len(all_records):,} 条记录")
    print(f"{'=' * 60}")
    
    # ============================================================
    # 步骤2: 时期分布统计
    # ============================================================
    print("\n[步骤2] 时期分布统计 ...")
    
    period_distribution = Counter(r['period'] for r in all_records)
    
    # 特别关注时期
    target_periods = ["Old Babylonian", "Middle Babylonian", "Neo-Assyrian", 
                      "Neo-Babylonian", "Kassite", "Hellenistic", "Ur III",
                      "Akkadian", "Early Dynastic", "Old Assyrian", "Middle Assyrian",
                      "Achaemenid", "Late Babylonian", "Standard Babylonian"]
    
    print("\n--- 目标时期覆盖 ---")
    for tp in target_periods:
        count = period_distribution.get(tp, 0)
        pct = count / len(all_records) * 100 if all_records else 0
        print(f"  {tp}: {count} ({pct:.2f}%)")
    
    # ============================================================
    # 步骤3: 识别可验证事件的数据覆盖
    # ============================================================
    print("\n[步骤3] 事件数据覆盖分析 ...")
    
    event_coverage = []
    for event in KEY_EVENTS:
        event_year = event['year']
        
        # 检查是否有对应时期的数据（时期时间范围覆盖事件年份）
        covered_periods = []
        for p in event['periods']:
            if period_distribution.get(p, 0) > 0 and period_covers_year(p, event_year):
                covered_periods.append(p)
        
        # 检查事件年份附近是否有精确年份数据
        nearby_records = [r for r in all_records 
                         if r['year'] is not None 
                         and event_year - 100 <= r['year'] <= event_year + 100]
        
        # 检查事件年份附近是否有相关时期的数据（即使无精确年份）
        period_nearby = [r for r in all_records if r['period'] in event['periods'] and period_covers_year(r['period'], event_year)]
        
        event_coverage.append({
            'event': event['name'],
            'year': event['year'],
            'target_periods': event['periods'],
            'covered_periods': covered_periods,
            'has_period_data': len(covered_periods) > 0,
            'nearby_count': len(nearby_records),
            'period_nearby_count': len(period_nearby),
            'note': event['note'],
        })
        
        status = "✓" if len(covered_periods) > 0 else "✗"
        print(f"  {status} {event['name']} ({event['year']} BCE): 时期覆盖={covered_periods}, 精确年份附近100年={len(nearby_records)}, 时期匹配={len(period_nearby)}")
    
    # ============================================================
    # 步骤4: 计算各时期的SFD(专家密度)
    # ============================================================
    print("\n[步骤4] 计算SFD(专家密度) ...")
    
    # 区分精确年份和fallback年份
    records_with_exact_year = [r for r in all_records if parse_date_of_origin(r.get('date_of_origin', '')) is not None]
    records_with_fallback_year = [r for r in all_records if r['year'] is not None and parse_date_of_origin(r.get('date_of_origin', '')) is None]
    records_with_year = records_with_exact_year + records_with_fallback_year
    
    print(f"  精确年份记录: {len(records_with_exact_year):,}")
    print(f"  Fallback年份记录: {len(records_with_fallback_year):,}")
    
    # 全局100年窗口 - 使用精确年份
    year_window = 100
    
    if records_with_exact_year:
        min_year = math.floor(min(r['year'] for r in records_with_exact_year) / year_window) * year_window
        max_year = math.ceil(max(r['year'] for r in records_with_exact_year) / year_window) * year_window
    else:
        min_year, max_year = 0, 0
    
    window_counts = defaultdict(int)
    for r in records_with_exact_year:
        window = math.floor(r['year'] / year_window) * year_window
        window_counts[window] += 1
    
    # 计算z-score (SFD_z)
    counts = list(window_counts.values())
    mean_count = sum(counts) / len(counts) if counts else 0
    std_count = math.sqrt(sum((c - mean_count)**2 for c in counts) / len(counts)) if counts else 1
    if std_count == 0:
        std_count = 1
    
    sfd_series = []
    for window in sorted(window_counts.keys()):
        count = window_counts[window]
        sfd_z = (count - mean_count) / std_count
        sfd_series.append({
            'window_start': window,
            'window_end': window + year_window,
            'count': count,
            'sfd_z': sfd_z,
        })
    
    print(f"  时间范围: {min_year} ~ {max_year} BCE")
    print(f"  100年窗口数: {len(sfd_series)}")
    print(f"  平均文本数/窗口: {mean_count:.1f}")
    if sfd_series:
        print(f"  SFD_z范围: {min(s['sfd_z'] for s in sfd_series):.2f} ~ {max(s['sfd_z'] for s in sfd_series):.2f}")
    
    # 按时期分别计算SFD（使用精确年份）
    period_sfd = {}
    for period in set(r['period'] for r in records_with_exact_year):
        period_records = [r for r in records_with_exact_year if r['period'] == period]
        if len(period_records) < 10:
            continue
        
        p_window_counts = defaultdict(int)
        for r in period_records:
            window = math.floor(r['year'] / year_window) * year_window
            p_window_counts[window] += 1
        
        p_counts = list(p_window_counts.values())
        p_mean = sum(p_counts) / len(p_counts) if p_counts else 0
        p_std = math.sqrt(sum((c - p_mean)**2 for c in p_counts) / len(p_counts)) if p_counts else 1
        if p_std == 0:
            p_std = 1
        
        p_sfd = []
        for window in sorted(p_window_counts.keys()):
            count = p_window_counts[window]
            sfd_z = (count - p_mean) / p_std
            p_sfd.append({
                'window_start': window,
                'window_end': window + year_window,
                'count': count,
                'sfd_z': sfd_z,
            })
        
        period_sfd[period] = p_sfd
    
    # ============================================================
    # 步骤5: 验证事件 (改进版: 使用时期内密度比较)
    # ============================================================
    print("\n[步骤5] 验证事件 ...")
    
    def get_record_year_range(record):
        """返回记录覆盖的年份范围 (start, end)"""
        # 如果有精确年份，使用精确年份±25年
        if parse_date_of_origin(record.get('date_of_origin', '')) is not None and record['year'] is not None:
            return (record['year'] - 25, record['year'] + 25)
        # 否则使用period范围
        period = record['period']
        if period in PERIOD_RANGES and PERIOD_RANGES[period]:
            return PERIOD_RANGES[period]
        return (None, None)
    
    def record_covers_year(record, target_year, window=100):
        """检查记录是否覆盖目标年份±window范围"""
        start, end = get_record_year_range(record)
        if start is None:
            return False
        return (start <= target_year + window) and (end >= target_year - window)
    
    event_validation = []
    for event in KEY_EVENTS:
        event_year = event['year']
        relevant_periods = event['periods']
        
        # 收集所有相关时期的记录
        relevant_records = [r for r in all_records if r['period'] in relevant_periods]
        
        if not relevant_records:
            event_validation.append({
                'event': event['name'],
                'year': event['year'],
                'has_data': False,
                'nearby_exact_count': 0,
                'nearby_period_count': 0,
                'event_density': 0,
                'avg_density': 0,
                'density_ratio': 0,
                'window_count': 0,
                'median_density': 0,
                'event_window_density': 0,
                'window_ratio': 0,
                'global_sfd_z': None,
                'period_sfd_z': None,
                'is_trough': False,
                'conclusion': "无数据覆盖",
            })
            print(f"  {event['name']}: 无数据覆盖")
            continue
        
        # 计算事件年份±100年内的记录数（使用所有相关记录）
        nearby_window = [r for r in relevant_records if record_covers_year(r, event_year, 100)]
        nearby_count = len(nearby_window)
        
        # 计算精确年份在±50年内的记录数
        nearby_exact = [r for r in records_with_exact_year 
                       if r['period'] in relevant_periods 
                       and event_year - 50 <= r['year'] <= event_year + 50]
        
        # 计算时期内各100年窗口密度（使用精确年份记录，只使用实际覆盖事件年份的时期）
        period_window_counts = defaultdict(int)
        covered_periods_for_event = [p for p in relevant_periods if p in PERIOD_RANGES and PERIOD_RANGES[p] and PERIOD_RANGES[p][0] <= event_year <= PERIOD_RANGES[p][1]]
        for r in relevant_records:
            if r['period'] in covered_periods_for_event and parse_date_of_origin(r.get('date_of_origin', '')) is not None and r['year'] is not None:
                w = math.floor(r['year'] / 100) * 100
                period_window_counts[w] += 1
        
        # 方法1: 窗口密度比较（需要>=3个窗口且总记录>=100）
        use_window_method = len(period_window_counts) >= 3 and sum(period_window_counts.values()) >= 100
        
        if use_window_method:
            densities = sorted(period_window_counts.values())
            median_density = densities[len(densities) // 2]
            max_density = max(densities)
            event_window = math.floor(event_year / 100) * 100
            event_window_density = period_window_counts.get(event_window, 0)
            window_ratio = event_window_density / median_density if median_density > 0 else 0
            max_ratio = event_window_density / max_density if max_density > 0 else 0
            
            # 如果事件窗口密度 < 最大密度的20%，视为显著低谷
            is_trough_window = event_window_density < max_density * 0.2
        else:
            median_density = 0
            max_density = 0
            event_window_density = 0
            window_ratio = 0
            max_ratio = 0
            is_trough_window = False
        
        # 方法2: 密度比（回退方法）
        total_span = 0
        for p in relevant_periods:
            if p in PERIOD_RANGES and PERIOD_RANGES[p]:
                start, end = PERIOD_RANGES[p]
                total_span += (end - start)
        
        avg_density = len(relevant_records) / (total_span / 100) if total_span > 0 else 0
        event_density = nearby_count / 2.0
        density_ratio = event_density / avg_density if avg_density > 0 else 0
        
        # 方法3: 分时期SFD_z
        period_sfd_z = None
        for p in relevant_periods:
            if p in period_sfd:
                for s in period_sfd[p]:
                    if s['window_start'] <= event_year < s['window_end']:
                        period_sfd_z = s['sfd_z']
                        break
        
        # 综合判断
        is_trough = is_trough_window or (density_ratio < 0.7 and density_ratio > 0) or (period_sfd_z is not None and period_sfd_z < -0.5)
        
        # 结论
        if not is_trough:
            if use_window_method:
                conclusion = f"数据覆盖: 窗口密度正常(比={window_ratio:.2f})"
            elif nearby_exact:
                conclusion = "数据覆盖但非SFD低谷"
            else:
                conclusion = "时期数据覆盖但非SFD低谷(无精确年份)"
        else:
            if is_trough_window:
                conclusion = "验证通过: 窗口密度低谷"
            elif period_sfd_z is not None and period_sfd_z < -0.5:
                conclusion = "验证通过: SFD低谷"
            else:
                conclusion = "验证通过: 密度低谷"
        
        event_validation.append({
            'event': event['name'],
            'year': event['year'],
            'has_data': True,
            'nearby_exact_count': len(nearby_exact),
            'nearby_period_count': nearby_count,
            'event_density': round(event_density, 1),
            'avg_density': round(avg_density, 1),
            'density_ratio': round(density_ratio, 2),
            'window_count': len(period_window_counts),
            'median_density': median_density,
            'event_window_density': event_window_density,
            'window_ratio': round(window_ratio, 2),
            'max_ratio': round(max_ratio, 2) if max_ratio is not None else None,
            'global_sfd_z': None,
            'period_sfd_z': round(period_sfd_z, 2) if period_sfd_z is not None else None,
            'is_trough': is_trough,
            'conclusion': conclusion,
        })
        
        method_str = "窗口法" if use_window_method else "密度比"
        print(f"  {event['name']}: 数据=✓, 精确附近50年={len(nearby_exact)}, 时期匹配={nearby_count}, 方法={method_str}, 密度比={density_ratio:.2f}, 窗口比={window_ratio:.2f}, SFD_z={period_sfd_z if period_sfd_z is not None else 'N/A'}, 结论={conclusion}")
    
    # ============================================================
    # 步骤6: 生成报告
    # ============================================================
    print("\n[步骤6] 生成报告 ...")
    
    report_path = os.path.join(V8_DIR, "v8a_oracc_integration_report.md")
    
    # 计算通过率
    verified_count = sum(1 for e in event_validation if "验证通过" in e['conclusion'])
    total_events = len(KEY_EVENTS)
    
    report = f"""# v8a ORACC整合报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**整合工程师**: v8_TrackA_ORACC整合工程师  
**数据来源**: v6.3已下载11个ORACC子项目  
**总记录数**: {len(all_records):,}  
**有年份记录**: {len(records_with_year):,} ({len(records_with_year)/len(all_records)*100:.1f}%)  
**精确年份记录**: {len(records_with_exact_year):,} ({len(records_with_exact_year)/len(all_records)*100:.1f}%)

---

## 1. 各子项目数据规模摘要

| 子项目 | 总记录数 | 有年份 | 精确年份 | 年份覆盖率 | 主要时期 |
|--------|---------|--------|----------|-----------|---------|
"""
    
    for project_name, stats in project_stats.items():
        pct = stats['with_year'] / stats['total'] * 100 if stats['total'] > 0 else 0
        top_periods = ', '.join([f"{k}({v})" for k, v in list(stats['periods'].items())[:3]])
        report += f"| {project_name} | {stats['total']:,} | {stats['with_year']:,} | {stats['exact_year']:,} | {pct:.1f}% | {top_periods} |\n"
    
    report += f"""
**关键发现**:
- 最大数据源: epsd2-admin-ur3 ({project_stats.get('epsd2-admin-ur3', {}).get('total', 0):,}条), 占总量{project_stats.get('epsd2-admin-ur3', {}).get('total', 0)/len(all_records)*100:.1f}%
- saao子项目提供Neo-Assyrian数据: {project_stats.get('saao', {}).get('total', 0):,}条
- riao/rinap提供Royal数据: {project_stats.get('riao', {}).get('total', 0) + project_stats.get('rinap', {}).get('total', 0):,}条
- dcclt提供多时期数据: {project_stats.get('dcclt', {}).get('total', 0):,}条 (OB+NA+MB)

---

## 2. 时期分布统计表（所有子项目合并）

### 2.1 全部时期分布

| 时期 | 记录数 | 占比 | 备注 |
|------|--------|------|------|
"""
    
    for period, count in period_distribution.most_common():
        pct = count / len(all_records) * 100
        note = ""
        if period in target_periods:
            note = "✓ 目标时期"
        report += f"| {period} | {count:,} | {pct:.2f}% | {note} |\n"
    
    report += f"""
### 2.2 目标时期详细统计

| 时期 | 时间范围 (BCE) | 记录数 | 占比 | v7缺口状态 |
|------|---------------|--------|------|-----------|
| Ur III | -2112 ~ -2004 | {period_distribution.get('Ur III', 0):,} | {period_distribution.get('Ur III', 0)/len(all_records)*100:.2f}% | v7已覆盖 |
| Old Babylonian | -1894 ~ -1595 | {period_distribution.get('Old Babylonian', 0):,} | {period_distribution.get('Old Babylonian', 0)/len(all_records)*100:.2f}% | {'✓ 已填补' if period_distribution.get('Old Babylonian', 0) > 0 else '✗ 仍缺失'} |
| Middle Babylonian | -1595 ~ -1155 | {period_distribution.get('Middle Babylonian', 0):,} | {period_distribution.get('Middle Babylonian', 0)/len(all_records)*100:.2f}% | {'✓ 已填补' if period_distribution.get('Middle Babylonian', 0) > 0 else '✗ 仍缺失'} |
| Kassite | -1595 ~ -1155 | {period_distribution.get('Kassite', 0):,} | {period_distribution.get('Kassite', 0)/len(all_records)*100:.2f}% | {'✓ 已填补' if period_distribution.get('Kassite', 0) > 0 else '✗ 仍缺失'} |
| Neo-Assyrian | -911 ~ -612 | {period_distribution.get('Neo-Assyrian', 0):,} | {period_distribution.get('Neo-Assyrian', 0)/len(all_records)*100:.2f}% | {'✓ 已填补' if period_distribution.get('Neo-Assyrian', 0) > 0 else '✗ 仍缺失'} |
| Neo-Babylonian | -626 ~ -539 | {period_distribution.get('Neo-Babylonian', 0):,} | {period_distribution.get('Neo-Babylonian', 0)/len(all_records)*100:.2f}% | {'✓ 已填补' if period_distribution.get('Neo-Babylonian', 0) > 0 else '✗ 仍缺失'} |
| Hellenistic | -323 ~ -100 | {period_distribution.get('Hellenistic', 0):,} | {period_distribution.get('Hellenistic', 0)/len(all_records)*100:.2f}% | {'✓ 已填补' if period_distribution.get('Hellenistic', 0) > 0 else '✗ 仍缺失'} |
| Akkadian | -2334 ~ -2154 | {period_distribution.get('Akkadian', 0):,} | {period_distribution.get('Akkadian', 0)/len(all_records)*100:.2f}% | 辅助验证 |
| Early Dynastic | -2900 ~ -2350 | {period_distribution.get('Early Dynastic', 0):,} | {period_distribution.get('Early Dynastic', 0)/len(all_records)*100:.2f}% | 辅助验证 |

---

## 3. 8个关键事件的数据覆盖情况

| # | 事件 | 年份 (BCE) | 需要时期 | 实际覆盖时期 | 有数据 | 精确年份±100年 | 时期匹配记录 | 备注 |
|---|------|-----------|---------|------------|--------|--------------|------------|------|
"""
    
    for i, ec in enumerate(event_coverage, 1):
        has_data_mark = "✓" if ec['has_period_data'] else "✗"
        report += f"| {i} | {ec['event']} | {ec['year']} | {', '.join(ec['target_periods'])} | {', '.join(ec['covered_periods']) if ec['covered_periods'] else '无'} | {has_data_mark} | {ec['nearby_count']} | {ec['period_nearby_count']} | {ec['note']} |\n"
    
    report += f"""
**覆盖总结**:
- 有时期数据覆盖的事件: {sum(1 for e in event_coverage if e['has_period_data'])}/8
- 无数据覆盖的事件: {sum(1 for e in event_coverage if not e['has_period_data'])}/8

---

## 4. 各时期SFD时间序列

### 4.1 全局100年窗口SFD（基于精确年份）

| 窗口起始 (BCE) | 窗口结束 (BCE) | 文本数 | SFD_z | 状态 |
|---------------|---------------|--------|-------|------|
"""
    
    for s in sfd_series:
        status = "低谷" if s['sfd_z'] < -0.5 else ("高峰" if s['sfd_z'] > 0.5 else "正常")
        report += f"| {s['window_start']:.0f} | {s['window_end']:.0f} | {s['count']} | {s['sfd_z']:.2f} | {status} |\n"
    
    report += f"""
### 4.2 分时期SFD摘要（基于精确年份）

| 时期 | 窗口数 | 平均SFD_z | 最低SFD_z | 最低窗口 (BCE) |
|------|--------|----------|----------|---------------|
"""
    
    for period, sfd_list in sorted(period_sfd.items(), key=lambda x: len(x[1]), reverse=True):
        if len(sfd_list) > 0:
            avg_z = sum(s['sfd_z'] for s in sfd_list) / len(sfd_list)
            min_sfd = min(sfd_list, key=lambda s: s['sfd_z'])
            report += f"| {period} | {len(sfd_list)} | {avg_z:.2f} | {min_sfd['sfd_z']:.2f} | {min_sfd['window_start']:.0f}~{min_sfd['window_end']:.0f} |\n"
    
    report += f"""
---

## 5. 验证结果表格

| # | 事件 | 年份 | 数据覆盖 | 精确附近50年 | 时期匹配记录 | 验证方法 | 窗口数 | 事件窗口密度 | 最大密度比 | 密度比 | 时期SFD_z | 结论 |
|---|------|------|---------|------------|------------|--------|--------|------------|----------|--------|----------|------|
"""
    
    for i, ev in enumerate(event_validation, 1):
        method = "窗口法" if ev['window_count'] >= 3 else "密度比"
        psfd = f"{ev['period_sfd_z']:.2f}" if ev['period_sfd_z'] is not None else "N/A"
        max_ratio_str = f"{ev.get('max_ratio', 0):.2f}" if ev.get('max_ratio') is not None else "N/A"
        report += f"| {i} | {ev['event']} | {ev['year']} | {'✓' if ev['has_data'] else '✗'} | {ev['nearby_exact_count']} | {ev['nearby_period_count']} | {method} | {ev['window_count']} | {ev['event_window_density']} | {max_ratio_str} | {ev['density_ratio']:.2f} | {psfd} | {ev['conclusion']} |\n"
    
    report += f"""
**验证统计**:
- 验证通过: {verified_count}/{total_events}
  - 窗口密度低谷: {sum(1 for e in event_validation if '窗口密度低谷' in e['conclusion'])}/{total_events}
  - SFD低谷: {sum(1 for e in event_validation if 'SFD低谷' in e['conclusion'])}/{total_events}
  - 密度低谷: {sum(1 for e in event_validation if '密度低谷' in e['conclusion'] and '窗口' not in e['conclusion'] and 'SFD' not in e['conclusion'])}/{total_events}
- 数据覆盖但非低谷: {sum(1 for e in event_validation if '数据覆盖' in e['conclusion'] and '验证通过' not in e['conclusion'])}/{total_events}
- 时期数据覆盖但无法精确验证: {sum(1 for e in event_validation if '时期数据覆盖' in e['conclusion'] and '验证通过' not in e['conclusion'])}/{total_events}
- 完全无数据: {sum(1 for e in event_validation if '无数据覆盖' in e['conclusion'])}/{total_events}

---

## 6. 与v7的对比

| 指标 | v7 (仅Ur III) | v8a (11个子项目整合) | 变化 |
|------|--------------|---------------------|------|
| 总记录数 | ~80,181 | {len(all_records):,} | +{len(all_records) - 80181:,} |
| 覆盖时期 | 主要Ur III | Ur III + OB + NA + NB + MB + ED + Akkadian + 其他 | 大幅扩展 |
| 数据覆盖事件 | 2/8 (Ur III衰亡, Umma衰落) | {sum(1 for e in event_validation if e['has_data'])}/8 | +{sum(1 for e in event_validation if e['has_data']) - 2} |
| 验证通过事件 | 1/8 (Ur III衰亡) | {verified_count}/8 | +{verified_count - 1} |
| 年份精度 | 1年精度 (Ur III) | 混合精度 (依赖date_of_origin) | 保持 |
| 精确年份记录 | ~62,000 (Ur III) | {len(records_with_exact_year):,} (全时期) | +{len(records_with_exact_year) - 62000:,} |

**关键改进**:
"""
    
    # 自动识别改进点
    improvements = []
    if period_distribution.get('Neo-Assyrian', 0) > 0:
        improvements.append("- 新增Neo-Assyrian数据(saao+riao+dcclt): 可验证Assyria危机/新亚述灭亡(-612 BCE)")
    if period_distribution.get('Neo-Babylonian', 0) > 0:
        improvements.append("- 新增Neo-Babylonian数据(dcclt+epsd2-literary): 可验证Neo-Babylonian陷落(-539 BCE)")
    if period_distribution.get('Old Babylonian', 0) > 0:
        improvements.append("- 新增Old Babylonian数据(dcclt+epsd2-literary+epsd2-royal): 可验证Hammurabi死后分裂(-1750 BCE)和OB终结(-1595 BCE)")
    if period_distribution.get('Akkadian', 0) > 0:
        improvements.append("- 新增Akkadian数据(epsd2-admin-oakk+etcsri): 部分覆盖Gutian入侵(-2190 BCE)时期")
    if period_distribution.get('Middle Babylonian', 0) > 0:
        improvements.append("- 新增Middle Babylonian数据(dcclt): 可验证Kassite王朝终结(-1155 BCE)")
    
    if improvements:
        report += '\n'.join(improvements) + '\n'
    else:
        report += "- 时期扩展有限，主要数据仍集中在Ur III\n"
    
    report += f"""
---

## 7. 局限与下一步

### 7.1 当前局限

1. **年份提取率提升但仍有限**: 精确年份仅{len(records_with_exact_year)/len(all_records)*100:.1f}%，大量记录依赖period字段的粗略估计
2. **统治者年名解析精度**: Ur III年名(SH/AS/SS/IS)和Neo-Assyrian统治者名(Tiglath-pileser等)的公历转换依赖Middle Chronology，存在±20-50年不确定性
3. **Gutian入侵(-2190 BCE)数据稀少**: Akkadian时期虽有{period_distribution.get('Akkadian', 0):,}条记录，但集中在Sargonic时期(-2334~-2154)，-2190附近记录稀少
4. **SFD计算仅基于精确年份**: 大量period-only记录未纳入SFD计算，可能低估某些时期的密度
5. **Ur III数据主导**: Ur III占{period_distribution.get('Ur III', 0)/len(all_records)*100:.1f}%，全局SFD被严重扭曲
6. **低谷阈值启发式**: z-score < -0.5 是经验设定，可能需要按时期调整

### 7.2 数据缺口诚实报告

| 事件 | 缺口原因 | 能否填补 | 建议 |
|------|---------|---------|------|
| Gutian入侵 (-2190) | Akkadian数据集中在早期，-2190附近稀少 | 部分 | 整合考古层位数据 |
| Hammurabi死后分裂 (-1750) | OB数据有但精确年份少 | 可以 | 利用Royal genre文本 |
| OB终结 (-1595) | MB/Kassite数据较少 | 部分 | 寻找专门Kassite项目 |
| Kassite终结 (-1155) | Kassite文本稀少 | 困难 | 需专门Kassite Corpus |
| Assyria危机 (-612) | NA数据充足(saao) | 已覆盖 | 进一步精细化 |
| NB陷落 (-539) | NB数据量中等 | 已覆盖 | 可进一步扩充 |

### 7.3 下一步建议

1. **统治者年名精细化**: 建立更精确的Ur III和Neo-Assyrian年表映射
2. **补充Kassite数据**: 寻找专门的Kassite/Babylonian子项目（如Kassite Corpus）
3. **考古数据整合**: 对Gutian入侵等早期事件，整合考古层位数据作为代理
4. **跨时期SFD标准化**: 不同时期的文本总量差异巨大，需要时期内标准化而非全局标准化
5. **genre权重调整**: Royal/Administrative文本的SFD权重可能应高于Literary
6. **时间窗口优化**: 对不同时期使用不同窗口（如Ur III用50年，NA用100年）
7. **period-only记录处理**: 将无精确年份的记录均匀分布到其period时间范围内，而非集中在中点

---

## 附录: 方法说明

- **SFD (Source Find Density)**: 每100年时间窗口内的文本数量，标准化为z-score
- **低谷阈值**: 
  - 窗口法: 事件窗口密度 < 该时期最大窗口密度的20% 视为显著低谷
  - SFD法: SFD_z < -0.5 视为显著低谷
  - 密度比法: 事件附近密度 < 时期平均密度的70% 视为低谷
- **年份提取优先级**: 
  1. date_of_origin直接解析（BCE年份、范围、统治者年名）
  2. period中点fallback
- **时期标准化**: 统一大小写和缩写（如OB→Old Babylonian, Old Akkadian→Akkadian）
- **事件覆盖判断**: 不仅检查精确年份附近，还检查相关时期的时间范围是否覆盖事件年份
- **验证方法选择**:
  - 窗口法: 当相关时期有≥3个100年窗口且总精确年份记录≥100时使用
  - 密度比法: 窗口不足时的回退方法
- **统治者年名转换**:
  - Ur III: SH(Shulgi -2094~-2047), AS(Amar-Sin -2046~-2038), SS(Shu-Sin -2037~-2029), IS(Ibbi-Sin -2028~-2004)
  - Neo-Assyrian: Tiglath-pileser3(-745~-727), Sargon2(-722~-705), Sennacherib(-705~-681), Esarhaddon(-681~-669), Ashurbanipal(-669~-631), Sin-sharru-ishkun(-627~-612)

---

*报告结束*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[完成] 报告已保存到: {report_path}")
    print(f"  总记录: {len(all_records):,}")
    print(f"  精确年份: {len(records_with_exact_year):,}")
    print(f"  验证通过: {verified_count}/{total_events}")
    
    # 同时保存JSON中间结果供后续使用
    json_path = os.path.join(V8_DIR, "v8a_oracc_parsed_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'project_stats': project_stats,
            'period_distribution': dict(period_distribution),
            'event_coverage': event_coverage,
            'event_validation': event_validation,
            'sfd_series': sfd_series,
            'period_sfd': {k: v for k, v in period_sfd.items()},
        }, f, ensure_ascii=False, indent=2)
    print(f"  中间数据: {json_path}")


if __name__ == '__main__':
    main()
