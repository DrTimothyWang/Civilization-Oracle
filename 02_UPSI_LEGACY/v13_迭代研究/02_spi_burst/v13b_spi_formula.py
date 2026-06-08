#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v13b SPI (Sudden Pressure Indicator) Computation Engine

SPI is a velocity-based companion indicator to PSI (level-based).
- PSI = integral/smoothed level indicator (50-100 year windows)
- SPI = derivative/rate-of-change indicator (1-10 year windows)

Key design principles:
1. Same raw data as PSI (ORACC catalogues, financial bars, etc.)
2. Rate-of-change based, not level-based
3. Spike detection (upper tail), not trough detection (lower tail)
4. Adaptive temporal resolution based on data density
"""

import json
import math
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Any

# ============================================================
# Configuration
# ============================================================

# Genre weights inherited from v12 P0
GENRE_WEIGHTS = {
    'administrative': 0.6, 'Administrative': 0.6, 'admin': 0.6,
    'legal': 1.2, 'Legal': 1.2, 'law': 1.2,
    'royal': 0.8, 'Royal Inscription': 0.8, 'royal_inscription': 0.8,
    'literary': 1.2, 'Literary': 1.2,
    'letter': 1.0, 'Letter': 1.0,
    'lexical': 0.5, 'Lexical': 0.5,
    'mathematical': 0.5, 'Mathematical': 0.5, 'math': 0.5,
    'school': 0.7, 'School': 0.7, 'education': 0.7,
    'omen': 0.9, 'Omen': 0.9,
    'religious': 0.9, 'Religious': 0.9,
    'prayer': 0.9, 'hymn': 0.9,
    'medical': 0.8,
    'astronomical': 0.5,
    'economic': 0.6, 'Economic': 0.6,
}

SUBPROJECT_GENRE = {
    'dcclt': 'administrative',
    'riao': 'royal',
    'rinap': 'royal',
    'saao': 'letter',
    'etcsri': 'royal',
    'epsd2-admin-ed3b': 'administrative',
    'epsd2-admin-oakk': 'administrative',
    'epsd2-admin-ur3': 'administrative',
    'epsd2-literary': 'literary',
    'epsd2-royal': 'royal',
    'epsd2-praxis-varia': 'administrative',
}

# Ruler date mappings for interpolation
UR3_RULERS = {
    'SH': (-2094, -2047), 'AS': (-2046, -2038),
    'SS': (-2037, -2029), 'IS': (-2028, -2004),
    'UN': (-2112, -2095),
}

NEO_ASSYRIAN_RULERS = {
    'Tiglath-pileser3': (-745, -727), 'Tiglath-pileser': (-745, -727),
    'Shalmaneser5': (-727, -722), 'Shalmaneser3': (-859, -824),
    'Sargon2': (-722, -705), 'Sargon': (-722, -705),
    'Sennacherib': (-705, -681), 'Esarhaddon': (-681, -669),
    'Ashurbanipal': (-669, -631), 'Assurbanipal': (-669, -631),
    'Ashur-etil-ilani': (-631, -627), 'Assur-etel-ilani': (-631, -627),
    'Sin-shumu-lishir': (-626, -626), 'Sin-shar-ishkun': (-627, -612),
    'Sin-sharru-ishkun': (-627, -612), 'Ashur-uballit2': (-612, -609),
    'Assur-uballit': (-612, -609), 'Shamshi-Adad5': (-824, -811),
    'Adad-narari3': (-811, -783), 'Assur-dan3': (-773, -755),
}

OB_RULERS = {
    'Warad-Sin': (-1834, -1823), 'Rim-Sin': (-1822, -1763),
    'Samsu-iluna': (-1749, -1712), 'Hammurabi': (-1792, -1750),
    'Abi-eshuh': (-1711, -1684), 'Ammi-ditana': (-1683, -1647),
    'Ammi-saduqa': (-1646, -1626), 'Samsu-ditana': (-1625, -1595),
}

# SPI default weights
SPI_WEIGHTS = {
    'material_velocity': 0.35,
    'material_acceleration': 0.25,
    'fragmentation_velocity': 0.25,
    'disengagement_volatility': 0.15,
}

# Thresholds
SPI_THRESHOLD_ELEVATED = 1.5  # z-score
SPI_THRESHOLD_CRITICAL = 2.5  # z-score


def get_genre_weight(record: Dict) -> float:
    """Get genre weight for a record, with fallback to subproject inference."""
    genre = record.get('genre', '')
    if genre and genre in GENRE_WEIGHTS:
        return GENRE_WEIGHTS[genre]
    for g, w in GENRE_WEIGHTS.items():
        if g.lower() in genre.lower():
            return w
    subproject = record.get('subproject', '')
    if subproject in SUBPROJECT_GENRE:
        return GENRE_WEIGHTS.get(SUBPROJECT_GENRE[subproject], 1.0)
    return 1.0


def parse_ur3_year(date_str: str) -> Optional[int]:
    """Parse Ur III year from date string."""
    if not date_str:
        return None
    m = re.match(r'^(SH|AS|SS|IS|UN)(\d{1,2})', date_str.upper())
    if m:
        ruler = m.group(1)
        year_num = int(m.group(2))
        if ruler in UR3_RULERS:
            start, end = UR3_RULERS[ruler]
            year = start + (year_num - 1)
            return max(start, min(year, end))
    return None


def parse_neo_assyrian_year(date_str: str) -> Optional[int]:
    """Parse Neo-Assyrian year from date string."""
    if not date_str:
        return None
    m = re.match(r'^([A-Za-z\-]+(?:\d)?)', date_str)
    if m:
        ruler_key = m.group(1)
        if ruler_key in NEO_ASSYRIAN_RULERS:
            start, end = NEO_ASSYRIAN_RULERS[ruler_key]
            return (start + end) / 2
        ruler_base = re.sub(r'\d$', '', ruler_key)
        if ruler_base in NEO_ASSYRIAN_RULERS:
            start, end = NEO_ASSYRIAN_RULERS[ruler_base]
            return (start + end) / 2
    return None


def parse_ruler_year(date_str: str, ruler_dict: Dict) -> Optional[float]:
    """Parse year from ruler-based date string."""
    if not date_str:
        return None
    m = re.match(r'^([A-Za-z\-_]+)(?:\.\d+)?', date_str)
    if m:
        ruler_key = m.group(1)
        if ruler_key in ruler_dict:
            start, end = ruler_dict[ruler_key]
            return (start + end) / 2
    return None


def parse_date_of_origin(date_str: str) -> Optional[float]:
    """Parse date of origin from various formats. Returns BCE as negative."""
    if not date_str or date_str in ["--.--.00.00", "00.000.00.00", "XXXX - 00 - 00", "", "unknown", None, "00.00.00.00", "0000 - 00 - 00", "--.00.00.00", "N/A", "XXXX - XX - XX"]:
        return None
    date_str = str(date_str).strip()
    
    # Ur III
    y = parse_ur3_year(date_str)
    if y is not None:
        return y
    # Neo-Assyrian
    y = parse_neo_assyrian_year(date_str)
    if y is not None:
        return y
    # OB
    y = parse_ruler_year(date_str, OB_RULERS)
    if y is not None:
        return y
    
    # Range format: YYYY - YYYY
    m = re.match(r'^(\d{1,4})\s*[–\-]\s*(\d{1,4})$', date_str)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        if y1 > y2:
            y1, y2 = y2, y1
        return -(y1 + y2) / 2
    # YYYY - MM - DD
    m = re.match(r'^(\d{3,4})\s*[\.\-]\s*\d{1,2}\s*[\.\-]\s*\d{1,2}$', date_str)
    if m:
        return -int(m.group(1))
    # Pure 4-digit
    m = re.match(r'^(\d{3,4})$', date_str)
    if m:
        return -int(m.group(1))
    # ~YYYY
    m = re.match(r'^[~c\.\s]*(\d{3,4})$', date_str)
    if m:
        return -int(m.group(1))
    # YYYY BCE
    m = re.match(r'^(\d{1,4})\s*(?:BCE|BC)$', date_str, re.IGNORECASE)
    if m:
        return -int(m.group(1))
    # YYYY BCE – YYYY BCE
    m = re.match(r'^(\d{1,4})\s*BCE?\s*[–\-]\s*(\d{1,4})\s*BCE?$', date_str, re.IGNORECASE)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        if y1 > y2:
            y1, y2 = y2, y1
        return -(y1 + y2) / 2
    # YYYY, YYYY
    m = re.match(r'^(\d{3,4}),\s*(\d{3,4})$', date_str)
    if m:
        y1, y2 = int(m.group(1)), int(m.group(2))
        return -(y1 + y2) / 2
    return None


# ============================================================
# SPI Core Functions
# ============================================================

def compute_adaptive_tau(total_records: int, exact_year_records: int, 
                         period_duration: int = 300) -> Tuple[int, str]:
    """
    Compute adaptive short-window size tau based on data density.
    
    Returns:
        tau: window size in years
        confidence: 'EXACT', 'RULER', or 'INTERPOLATED'
    """
    if total_records < 100:
        return None, 'INSUFFICIENT'
    
    exact_ratio = exact_year_records / total_records if total_records > 0 else 0
    
    if exact_ratio >= 0.5:
        # High exact-year ratio: can use 1-year windows
        tau = max(1, period_duration // 1000)
        return max(1, tau), 'EXACT'
    elif exact_ratio >= 0.1:
        # Medium: 3-5 year windows
        tau = max(3, period_duration // 500)
        return max(3, tau), 'RULER'
    else:
        # Low: 5-10 year windows with interpolation
        tau = max(5, period_duration // 200)
        return min(10, max(5, tau)), 'INTERPOLATED'


def aggregate_short_window(records: List[Dict], tau: int, 
                           period_start: int, period_end: int,
                           provenience_filter: Optional[str] = None) -> Dict[int, Dict]:
    """
    Aggregate records into short windows of size tau.
    
    Args:
        records: List of record dicts with 'year', 'genre', 'provenience'
        tau: Window size in years
        period_start, period_end: Time range
        provenience_filter: If set, only count records from this provenience
    
    Returns:
        Dict mapping window_start -> {weighted_count, raw_count, proveniences}
    """
    windows = {}
    # Initialize all windows
    current = (period_start // tau) * tau
    while current <= period_end:
        windows[current] = {
            'weighted_count': 0.0,
            'raw_count': 0,
            'proveniences': Counter(),
        }
        current += tau
    
    for r in records:
        year = r.get('year')
        if year is None or year == 0:
            continue
        if year < period_start or year > period_end:
            continue
        
        prov = r.get('provenience', 'Unknown')
        if provenience_filter and prov != provenience_filter:
            continue
        
        w_start = int(year // tau * tau)
        if w_start in windows:
            weight = get_genre_weight(r)
            windows[w_start]['weighted_count'] += weight
            windows[w_start]['raw_count'] += 1
            if prov and prov != 'Unknown':
                windows[w_start]['proveniences'][prov] += 1
    
    return windows


def compute_material_velocity(windows: Dict[int, Dict], tau: int) -> Dict[int, float]:
    """
    Compute first derivative (velocity) of weighted text count.
    V(t) = [C(t) - C(t-tau)] / tau
    """
    sorted_windows = sorted(windows.keys())
    velocity = {}
    
    for i, w in enumerate(sorted_windows):
        if i == 0:
            velocity[w] = 0.0
            continue
        prev_w = sorted_windows[i - 1]
        curr_c = windows[w]['weighted_count']
        prev_c = windows[prev_w]['weighted_count']
        velocity[w] = (curr_c - prev_c) / tau
    
    return velocity


def compute_material_acceleration(velocity: Dict[int, float], tau: int) -> Dict[int, float]:
    """
    Compute second derivative (acceleration).
    A(t) = [V(t) - V(t-tau)] / tau
    """
    sorted_windows = sorted(velocity.keys())
    acceleration = {}
    
    for i, w in enumerate(sorted_windows):
        if i == 0:
            acceleration[w] = 0.0
            continue
        prev_w = sorted_windows[i - 1]
        acceleration[w] = (velocity[w] - velocity[prev_w]) / tau
    
    return acceleration


def compute_geographic_cv(windows: Dict[int, Dict]) -> Dict[int, float]:
    """
    Compute coefficient of variation (CV) of provenience distribution per window.
    """
    cv = {}
    for w, data in windows.items():
        prov_counts = list(data['proveniences'].values())
        if len(prov_counts) < 2:
            cv[w] = 0.0
            continue
        mean_c = sum(prov_counts) / len(prov_counts)
        if mean_c == 0:
            cv[w] = 0.0
            continue
        std_c = math.sqrt(sum((c - mean_c) ** 2 for c in prov_counts) / len(prov_counts))
        cv[w] = std_c / mean_c
    return cv


def compute_fragmentation_velocity(cv: Dict[int, float], tau: int) -> Dict[int, float]:
    """
    Compute rate of change of geographic CV.
    Delta_GSI(t) = [CV(t) - CV(t-tau)] / tau
    """
    sorted_windows = sorted(cv.keys())
    frag_vel = {}
    
    for i, w in enumerate(sorted_windows):
        if i == 0:
            frag_vel[w] = 0.0
            continue
        prev_w = sorted_windows[i - 1]
        frag_vel[w] = (cv[w] - cv[prev_w]) / tau
    
    return frag_vel


def compute_volatility(velocity: Dict[int, float], k: int = 3) -> Dict[int, float]:
    """
    Compute rolling volatility of velocity over k windows.
    sigma_V(t) = std(V(t), V(t-tau), ..., V(t-(k-1)*tau))
    """
    sorted_windows = sorted(velocity.keys())
    volatility = {}
    
    for i, w in enumerate(sorted_windows):
        if i < k - 1:
            volatility[w] = 0.0
            continue
        recent_vals = [velocity[sorted_windows[j]] for j in range(i - k + 1, i + 1)]
        mean_v = sum(recent_vals) / len(recent_vals)
        std_v = math.sqrt(sum((v - mean_v) ** 2 for v in recent_vals) / len(recent_vals))
        volatility[w] = std_v
    
    return volatility


def z_score_dict(values: Dict[int, float]) -> Dict[int, float]:
    """Compute z-scores for a dict of values."""
    vals = list(values.values())
    if not vals:
        return {k: 0.0 for k in values}
    mean_v = sum(vals) / len(vals)
    std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 1.0
    if std_v == 0:
        std_v = 1.0
    return {k: (v - mean_v) / std_v for k, v in values.items()}


def compute_spi_aggregate(
    velocity: Dict[int, float],
    acceleration: Dict[int, float],
    frag_velocity: Dict[int, float],
    volatility: Dict[int, float],
    weights: Optional[Dict[str, float]] = None
) -> Dict[int, Dict]:
    """
    Compute aggregate SPI score from four components.
    
    Returns dict mapping window_start -> {
        spi_m: material velocity z-score,
        spi_a: material acceleration z-score,
        spi_f: fragmentation velocity z-score (absolute value),
        spi_d: disengagement volatility z-score,
        spi_aggregate: weighted aggregate,
        alert_level: 'NORMAL', 'ELEVATED', 'CRITICAL'
    }
    """
    if weights is None:
        weights = SPI_WEIGHTS
    
    # Z-score each component
    z_vel = z_score_dict(velocity)
    z_acc = z_score_dict(acceleration)
    z_frag = z_score_dict({k: abs(v) for k, v in frag_velocity.items()})
    z_vol = z_score_dict(volatility)
    
    result = {}
    all_windows = sorted(set(velocity.keys()) & set(acceleration.keys()) & 
                        set(frag_velocity.keys()) & set(volatility.keys()))
    
    for w in all_windows:
        spi_m = z_vel.get(w, 0.0)
        spi_a = z_acc.get(w, 0.0)
        spi_f = z_frag.get(w, 0.0)
        spi_d = z_vol.get(w, 0.0)
        
        aggregate = (
            weights['material_velocity'] * abs(spi_m) +
            weights['material_acceleration'] * abs(spi_a) +
            weights['fragmentation_velocity'] * spi_f +
            weights['disengagement_volatility'] * spi_d
        )
        
        # Alert level based on upper tail (spike detection)
        if aggregate > SPI_THRESHOLD_CRITICAL:
            alert = 'CRITICAL'
        elif aggregate > SPI_THRESHOLD_ELEVATED:
            alert = 'ELEVATED'
        else:
            alert = 'NORMAL'
        
        result[w] = {
            'spi_m': round(spi_m, 3),
            'spi_a': round(spi_a, 3),
            'spi_f': round(spi_f, 3),
            'spi_d': round(spi_d, 3),
            'spi_aggregate': round(aggregate, 3),
            'alert_level': alert,
        }
    
    return result


def detect_sudden_drop(windows: Dict[int, Dict], velocity: Dict[int, float],
                        threshold_ratio: float = 0.5) -> List[Dict]:
    """
    Detect sudden drop events: windows where text count drops by > threshold_ratio
    relative to previous window.
    """
    drops = []
    sorted_windows = sorted(windows.keys())
    
    for i, w in enumerate(sorted_windows):
        if i == 0:
            continue
        prev_w = sorted_windows[i - 1]
        curr_c = windows[w]['weighted_count']
        prev_c = windows[prev_w]['weighted_count']
        
        if prev_c > 10 and curr_c < prev_c * threshold_ratio:
            drops.append({
                'window_start': w,
                'previous_count': round(prev_c, 2),
                'current_count': round(curr_c, 2),
                'drop_ratio': round(curr_c / prev_c, 3) if prev_c > 0 else 0,
                'velocity': round(velocity.get(w, 0), 3),
                'type': 'sudden_drop',
            })
    
    return drops


def detect_volatility_spike(volatility: Dict[int, float], 
                            threshold_z: float = 2.0) -> List[Dict]:
    """Detect windows where volatility exceeds threshold."""
    z_vol = z_score_dict(volatility)
    spikes = []
    for w, z in z_vol.items():
        if z > threshold_z:
            spikes.append({
                'window_start': w,
                'volatility': round(volatility[w], 3),
                'z_score': round(z, 3),
                'type': 'volatility_spike',
            })
    return spikes


def detect_correlation_breakdown(windows: Dict[int, Dict], 
                                  min_windows: int = 4) -> Optional[Dict]:
    """
    Detect correlation breakdown between text count and geographic diversity.
    In stable periods, more texts = more sites (positive correlation).
    In crisis periods, text count drops but CV spikes (negative correlation).
    """
    sorted_windows = sorted(windows.keys())
    if len(sorted_windows) < min_windows:
        return None
    
    counts = [windows[w]['weighted_count'] for w in sorted_windows]
    cv = compute_geographic_cv(windows)
    cv_vals = [cv.get(w, 0) for w in sorted_windows]
    
    # Simple correlation over first half vs second half
    mid = len(sorted_windows) // 2
    if mid < 2:
        return None
    
    # Compute correlation in first half
    def corr(x, y):
        n = len(x)
        if n < 2:
            return 0
        mx, my = sum(x)/n, sum(y)/n
        sx = math.sqrt(sum((xi - mx)**2 for xi in x) / n)
        sy = math.sqrt(sum((yi - my)**2 for yi in y) / n)
        if sx == 0 or sy == 0:
            return 0
        return sum((x[i]-mx)*(y[i]-my) for i in range(n)) / (n * sx * sy)
    
    corr_first = corr(counts[:mid], cv_vals[:mid])
    corr_second = corr(counts[mid:], cv_vals[mid:])
    
    # Breakdown: correlation flips from positive to negative
    if corr_first > 0.3 and corr_second < -0.1:
        return {
            'correlation_first_half': round(corr_first, 3),
            'correlation_second_half': round(corr_second, 3),
            'breakdown_detected': True,
            'type': 'correlation_breakdown',
        }
    
    return {
        'correlation_first_half': round(corr_first, 3),
        'correlation_second_half': round(corr_second, 3),
        'breakdown_detected': False,
        'type': 'correlation_breakdown',
    }


# ============================================================
# Main SPI Pipeline
# ============================================================

def compute_spi_for_period(
    records: List[Dict],
    period_name: str,
    period_start: int,
    period_end: int,
    tau: Optional[int] = None,
    provenience_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main SPI computation pipeline for a single period.
    
    Returns comprehensive SPI results including:
    - spi_series: window-by-window SPI scores
    - sudden_drops: detected sudden drop events
    - volatility_spikes: detected volatility spikes
    - correlation_breakdown: count-CV correlation analysis
    - metadata: computation parameters and confidence level
    """
    # Filter valid records
    valid_records = [r for r in records if r.get('year') is not None and r.get('year') != 0]
    exact_records = [r for r in valid_records if r.get('date_of_origin') and parse_date_of_origin(r.get('date_of_origin')) is not None]
    
    # Determine tau and confidence
    if tau is None:
        tau, confidence = compute_adaptive_tau(
            len(valid_records), 
            len(exact_records),
            abs(period_end - period_start)
        )
    else:
        exact_ratio = len(exact_records) / len(valid_records) if len(valid_records) > 0 else 0
        if exact_ratio >= 0.5:
            confidence = 'EXACT'
        elif exact_ratio >= 0.1:
            confidence = 'RULER'
        else:
            confidence = 'INTERPOLATED'
    
    if tau is None:
        return {
            'period': period_name,
            'error': 'INSUFFICIENT_DATA',
            'confidence': 'INSUFFICIENT',
        }
    
    # Aggregate into short windows
    windows = aggregate_short_window(valid_records, tau, period_start, period_end, provenience_filter)
    
    # Remove empty windows at edges for cleaner derivatives
    non_empty_windows = {w: d for w, d in windows.items() if d['raw_count'] > 0 or d['weighted_count'] > 0}
    if len(non_empty_windows) < 3:
        return {
            'period': period_name,
            'error': 'TOO_FEW_WINDOWS',
            'confidence': confidence,
            'n_windows': len(non_empty_windows),
        }
    
    # Compute SPI components
    velocity = compute_material_velocity(non_empty_windows, tau)
    acceleration = compute_material_acceleration(velocity, tau)
    cv = compute_geographic_cv(non_empty_windows)
    frag_velocity = compute_fragmentation_velocity(cv, tau)
    volatility = compute_volatility(velocity, k=3)
    
    # Aggregate SPI
    spi_series = compute_spi_aggregate(velocity, acceleration, frag_velocity, volatility)
    
    # Detection algorithms
    sudden_drops = detect_sudden_drop(non_empty_windows, velocity)
    vol_spikes = detect_volatility_spike(volatility)
    corr_breakdown = detect_correlation_breakdown(non_empty_windows)
    
    # Find max SPI window
    max_spi_window = None
    max_spi_val = -float('inf')
    for w, data in spi_series.items():
        if data['spi_aggregate'] > max_spi_val:
            max_spi_val = data['spi_aggregate']
            max_spi_window = w
    
    return {
        'period': period_name,
        'tau': tau,
        'confidence': confidence,
        'period_start': period_start,
        'period_end': period_end,
        'n_records': len(valid_records),
        'n_exact_records': len(exact_records),
        'n_windows': len(non_empty_windows),
        'windows': {str(w): {
            'weighted_count': round(d['weighted_count'], 2),
            'raw_count': d['raw_count'],
            'proveniences': dict(d['proveniences']),
        } for w, d in non_empty_windows.items()},
        'spi_series': {str(w): v for w, v in spi_series.items()},
        'velocity': {str(w): round(v, 3) for w, v in velocity.items()},
        'acceleration': {str(w): round(v, 3) for w, v in acceleration.items()},
        'cv': {str(w): round(v, 3) for w, v in cv.items()},
        'fragmentation_velocity': {str(w): round(v, 3) for w, v in frag_velocity.items()},
        'volatility': {str(w): round(v, 3) for w, v in volatility.items()},
        'sudden_drops': sudden_drops,
        'volatility_spikes': vol_spikes,
        'correlation_breakdown': corr_breakdown,
        'max_spi_window': max_spi_window,
        'max_spi_value': round(max_spi_val, 3) if max_spi_val > -float('inf') else None,
    }


def load_oracc_records(parsed_data_path: str) -> List[Dict]:
    """Load ORACC parsed records from v8a output."""
    with open(parsed_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    records = []
    # The v8a parsed data has project_stats, not individual records
    # We need to load from the original catalogues
    return records


if __name__ == '__main__':
    print("SPI Computation Engine v13b")
    print("Import this module and call compute_spi_for_period()")
    print("See v13b_spi_meso_test.py for usage example")
