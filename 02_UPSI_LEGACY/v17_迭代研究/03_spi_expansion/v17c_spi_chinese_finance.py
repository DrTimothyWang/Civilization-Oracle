#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v17c SPI Chinese Finance (A-share)
Compute SPI for Chinese A-share indices using same methodology as v14b finance SPI.

Methodology:
- Input: daily price data from yfinance (000300.SS = CSI 300, 000001.SS = SSE Composite, 399001.SZ = SZSE Component)
- τ = 5 trading days
- V(t) = rate of price change per window
- A(t) = acceleration of price change
- ΔGSI proxy = intra-window volatility change (CV of daily returns)
- σ_V = rolling std of V over 3 windows
- SPI(t) = 0.35*z(V) + 0.25*z(A) + 0.25*|ΔGSI_z| + 0.15*z(σ_V)

Crisis alignment:
- 2024 Snowball crash (Jan 2024): Chinese A-share structured product knock-ins
- 2024 Feb market rout (Feb 2024)
- 2025 arbitrage collapse (if data available)
"""

import json
import math
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import yfinance as yf

# ============================================================
# Configuration
# ============================================================

OUTPUT_DIR = '/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/03_spi_expansion'

SPI_WEIGHTS = {
    'material_velocity': 0.35,
    'material_acceleration': 0.25,
    'fragmentation_velocity': 0.25,
    'disengagement_volatility': 0.15,
}

SPI_THRESHOLD_ELEVATED = 1.5
SPI_THRESHOLD_CRITICAL = 2.5

# Chinese indices to analyze
CHINESE_INDICES = {
    'CSI300': {'ticker': '000300.SS', 'name': 'CSI 300 Index'},
    'SSE': {'ticker': '000001.SS', 'name': 'Shanghai Composite'},
    'SZSE': {'ticker': '399001.SZ', 'name': 'Shenzhen Component'},
}

# Known crisis events for Chinese A-share
KNOWN_CRISES = [
    {'name': '2024 Snowball Crash (knock-in)', 'date': '2024-01-17', 'ticker': '000300.SS'},
    {'name': '2024 Feb Market Rout', 'date': '2024-02-05', 'ticker': '000300.SS'},
    {'name': '2024 Spring Rebound peak', 'date': '2024-05-20', 'ticker': '000300.SS'},
    {'name': '2024 Sep Policy Rally', 'date': '2024-09-24', 'ticker': '000300.SS'},
]

# ============================================================
# SPI Core Functions
# ============================================================

def z_score_dict(values: Dict[Any, float]) -> Dict[Any, float]:
    """Compute z-scores for a dict of values."""
    vals = list(values.values())
    if not vals:
        return {k: 0.0 for k in values}
    mean_v = sum(vals) / len(vals)
    std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 1.0
    if std_v == 0:
        std_v = 1.0
    return {k: (v - mean_v) / std_v for k, v in values.items()}


def compute_material_velocity(counts: Dict[Any, float], tau: float = 1.0) -> Dict[Any, float]:
    sorted_keys = sorted(counts.keys())
    velocity = {}
    for i, k in enumerate(sorted_keys):
        if i == 0:
            velocity[k] = 0.0
            continue
        prev_k = sorted_keys[i - 1]
        velocity[k] = (counts[k] - counts[prev_k]) / tau
    return velocity


def compute_material_acceleration(velocity: Dict[Any, float], tau: float = 1.0) -> Dict[Any, float]:
    sorted_keys = sorted(velocity.keys())
    acceleration = {}
    for i, k in enumerate(sorted_keys):
        if i == 0:
            acceleration[k] = 0.0
            continue
        prev_k = sorted_keys[i - 1]
        acceleration[k] = (velocity[k] - velocity[prev_k]) / tau
    return acceleration


def compute_volatility(velocity: Dict[Any, float], k: int = 3) -> Dict[Any, float]:
    sorted_keys = sorted(velocity.keys())
    volatility = {}
    for i, k_val in enumerate(sorted_keys):
        if i < k - 1:
            volatility[k_val] = 0.0
            continue
        recent_vals = [velocity[sorted_keys[j]] for j in range(i - k + 1, i + 1)]
        mean_v = sum(recent_vals) / len(recent_vals)
        std_v = math.sqrt(sum((v - mean_v) ** 2 for v in recent_vals) / len(recent_vals))
        volatility[k_val] = std_v
    return volatility


def compute_fragmentation_velocity(cv: Dict[Any, float], tau: float = 1.0) -> Dict[Any, float]:
    sorted_keys = sorted(cv.keys())
    frag_vel = {}
    for i, k in enumerate(sorted_keys):
        if i == 0:
            frag_vel[k] = 0.0
            continue
        prev_k = sorted_keys[i - 1]
        frag_vel[k] = (cv[k] - cv[prev_k]) / tau
    return frag_vel


def compute_spi_aggregate(
    velocity: Dict[Any, float],
    acceleration: Dict[Any, float],
    frag_velocity: Dict[Any, float],
    volatility: Dict[Any, float],
    weights: Optional[Dict[str, float]] = None
) -> Dict[Any, Dict]:
    if weights is None:
        weights = SPI_WEIGHTS

    z_vel = z_score_dict(velocity)
    z_acc = z_score_dict(acceleration)
    z_frag = z_score_dict({k: abs(v) for k, v in frag_velocity.items()})
    z_vol = z_score_dict(volatility)

    result = {}
    all_keys = sorted(set(velocity.keys()) & set(acceleration.keys()) &
                      set(frag_velocity.keys()) & set(volatility.keys()))

    for k in all_keys:
        spi_m = z_vel.get(k, 0.0)
        spi_a = z_acc.get(k, 0.0)
        spi_f = z_frag.get(k, 0.0)
        spi_d = z_vol.get(k, 0.0)

        aggregate = (
            weights['material_velocity'] * abs(spi_m) +
            weights['material_acceleration'] * abs(spi_a) +
            weights['fragmentation_velocity'] * spi_f +
            weights['disengagement_volatility'] * spi_d
        )

        if aggregate > SPI_THRESHOLD_CRITICAL:
            alert = 'CRITICAL'
        elif aggregate > SPI_THRESHOLD_ELEVATED:
            alert = 'ELEVATED'
        else:
            alert = 'NORMAL'

        result[k] = {
            'spi_m': round(spi_m, 3),
            'spi_a': round(spi_a, 3),
            'spi_f': round(spi_f, 3),
            'spi_d': round(spi_d, 3),
            'spi_aggregate': round(aggregate, 3),
            'alert_level': alert,
        }

    return result


# ============================================================
# Data Fetching
# ============================================================

def fetch_chinese_finance_data(ticker: str, start: str, end: str) -> Tuple[List[datetime], List[float], List[float]]:
    """Fetch financial data from yfinance. Returns (dates, closes, volumes)."""
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
    except Exception as e:
        print(f"    Error fetching {ticker}: {e}")
        return [], [], []
    if data.empty:
        print(f"    No data for {ticker}")
        return [], [], []
    dates = data.index.tolist()
    closes = data['Close'].values.flatten().tolist() if hasattr(data['Close'], 'values') else data['Close'].tolist()
    volumes = data['Volume'].values.flatten().tolist() if hasattr(data['Volume'], 'values') else data['Volume'].tolist()
    return dates, closes, volumes


# ============================================================
# SPI Computation for Chinese Finance
# ============================================================

def compute_chinese_finance_spi(ticker: str, name: str, start: str, end: str,
                                 window_days: int = 5,
                                 crisis_events: List[Dict] = None) -> Dict[str, Any]:
    """Compute SPI on Chinese A-share price data."""
    dates, closes, volumes = fetch_chinese_finance_data(ticker, start, end)
    if not dates:
        return {
            'ticker': ticker,
            'name': name,
            'error': 'NO_DATA',
            'confidence': 'INSUFFICIENT',
        }

    # Aggregate to windows of `window_days`
    window_closes = {}
    window_volumes = {}
    window_dates = {}

    for i, d in enumerate(dates):
        day_ordinal = d.toordinal()
        w_start = (day_ordinal // window_days) * window_days
        if w_start not in window_closes:
            window_closes[w_start] = []
            window_volumes[w_start] = []
            window_dates[w_start] = []
        window_closes[w_start].append(closes[i])
        window_volumes[w_start].append(volumes[i])
        window_dates[w_start].append(d)

    # Use mean close per window as the level
    window_mean_close = {}
    for w, vals in window_closes.items():
        window_mean_close[w] = sum(vals) / len(vals)

    # Compute VIX-like internal volatility per window (CV of daily closes)
    window_internal_vol = {}
    for w, vals in window_closes.items():
        if len(vals) >= 2:
            mean_v = sum(vals) / len(vals)
            std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / len(vals))
            window_internal_vol[w] = std_v / mean_v if mean_v > 0 else 0
        else:
            window_internal_vol[w] = 0.0

    # Compute SPI components
    velocity = compute_material_velocity(window_mean_close, tau=window_days)
    acceleration = compute_material_acceleration(velocity, tau=window_days)
    frag_velocity = compute_fragmentation_velocity(window_internal_vol, tau=window_days)
    volatility = compute_volatility(velocity, k=3)

    spi_series = compute_spi_aggregate(velocity, acceleration, frag_velocity, volatility)

    # Convert window ordinals back to dates
    spi_series_dated = {}
    for w, data in spi_series.items():
        ds = window_dates.get(w, [])
        if ds:
            start_d = min(ds)
            end_d = max(ds)
            spi_series_dated[start_d.strftime('%Y-%m-%d')] = {
                **data,
                'window_end': end_d.strftime('%Y-%m-%d'),
                'mean_close': round(window_mean_close[w], 2),
                'n_days': len(ds),
            }

    # Find max SPI
    max_spi_window = None
    max_spi_val = -float('inf')
    alert_windows = []
    for w, data in spi_series.items():
        if data['spi_aggregate'] > max_spi_val:
            max_spi_val = data['spi_aggregate']
            max_spi_window = w
        if data['alert_level'] in ('ELEVATED', 'CRITICAL'):
            ds = window_dates.get(w, [])
            if ds:
                alert_windows.append({
                    'window_start': min(ds).strftime('%Y-%m-%d'),
                    'window_end': max(ds).strftime('%Y-%m-%d'),
                    'spi_aggregate': data['spi_aggregate'],
                    'alert_level': data['alert_level'],
                })

    # Align with crisis events
    crisis_alignment = []
    if crisis_events:
        for event in crisis_events:
            if event.get('ticker') and event['ticker'] != ticker:
                continue
            try:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
            except ValueError:
                continue
            event_ordinal = event_date.toordinal()
            # Find nearest window
            nearest_w = min(spi_series.keys(), key=lambda w: abs(w + window_days / 2 - event_ordinal))
            spi_data = spi_series.get(nearest_w, {})
            ds = window_dates.get(nearest_w, [])
            crisis_alignment.append({
                'event_name': event['name'],
                'event_date': event['date'],
                'nearest_window_start': min(ds).strftime('%Y-%m-%d') if ds else None,
                'nearest_window_end': max(ds).strftime('%Y-%m-%d') if ds else None,
                'spi_at_event': spi_data.get('spi_aggregate', None),
                'alert_at_event': spi_data.get('alert_level', 'UNKNOWN'),
                'captured': spi_data.get('alert_level') in ('ELEVATED', 'CRITICAL'),
            })

    return {
        'ticker': ticker,
        'name': name,
        'window_days': window_days,
        'confidence': 'EXACT',
        'period': [start, end],
        'n_records': len(dates),
        'n_windows': len(window_mean_close),
        'spi_series': spi_series_dated,
        'max_spi_window': datetime.fromordinal(max_spi_window).strftime('%Y-%m-%d') if max_spi_window else None,
        'max_spi_value': round(max_spi_val, 3) if max_spi_val > -float('inf') else None,
        'alert_windows': alert_windows,
        'crisis_alignment': crisis_alignment,
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Computing Chinese Finance SPI...")

    # Analysis period: 2023-01-01 to 2025-06-01 (covers Snowball crash and recent events)
    start = '2023-01-01'
    end = '2025-06-01'

    all_results = {
        'meta': {
            'domain': 'Chinese Finance (A-share)',
            'data_source': 'yfinance (CSI 300, SSE Composite, SZSE Component)',
            'window_days': 5,
            'period': [start, end],
            'note': 'Daily price data aggregated to 5-day windows. '
                    'Velocity = rate of price change. Fragmentation = intra-window volatility change.',
        },
        'indices': {},
    }

    for key, info in CHINESE_INDICES.items():
        print(f"\n  Processing {info['name']} ({info['ticker']})...")
        result = compute_chinese_finance_spi(
            info['ticker'], info['name'], start, end,
            window_days=5, crisis_events=KNOWN_CRISES
        )
        all_results['indices'][key] = result

        if 'error' in result:
            print(f"    ERROR: {result['error']}")
        else:
            print(f"    Records: {result['n_records']} daily bars -> {result['n_windows']} windows")
            print(f"    Max SPI: {result['max_spi_value']} at {result['max_spi_window']}")
            print(f"    Alert windows: {len(result['alert_windows'])}")
            captured = sum(1 for c in result['crisis_alignment'] if c['captured'])
            print(f"    Crises captured: {captured}/{len(result['crisis_alignment'])}")
            for item in result['crisis_alignment']:
                marker = "✅" if item['captured'] else "❌"
                print(f"      {marker} {item['event_name']} ({item['event_date']}): SPI={item['spi_at_event']} ({item['alert_at_event']})")

    output_path = os.path.join(OUTPUT_DIR, 'v17c_spi_chinese_finance.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n  -> Saved {output_path}")
    print("\nDone!")


if __name__ == '__main__':
    main()
