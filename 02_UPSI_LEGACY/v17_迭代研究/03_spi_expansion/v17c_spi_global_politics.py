#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v17c SPI Global Politics (Wikidata)
Compute SPI for political events from Wikidata war/revolution/coup data.

Methodology:
- Input: yearly event counts from wikidata_events.json
- V(t) = (events[t] - events[t-1]) / 1 year
- A(t) = (V[t] - V[t-1]) / 1 year
- σ_V = rolling std of V over 5 years
- ΔGSI proxy = event type diversity (war vs revolution vs civil_conflict) CV change
- SPI(t) = 0.35*z(V) + 0.25*z(A) + 0.25*|ΔGSI_z| + 0.15*z(σ_V)

Crisis alignment with well-documented political crises.
"""

import json
import math
import os
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ============================================================
# Configuration
# ============================================================

INPUT_PATH = '/Users/wangzr/Desktop/历史事件预测建模/v5/data/wikidata_events.json'
OUTPUT_DIR = '/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/03_spi_expansion'

SPI_WEIGHTS = {
    'material_velocity': 0.35,
    'material_acceleration': 0.25,
    'fragmentation_velocity': 0.25,
    'disengagement_volatility': 0.15,
}

SPI_THRESHOLD_ELEVATED = 1.5
SPI_THRESHOLD_CRITICAL = 2.5

# Well-documented political crises for validation
KNOWN_CRISES = [
    {'name': 'French Revolution', 'year': 1789},
    {'name': 'Napoleonic Wars peak', 'year': 1812},
    {'name': 'Revolutions of 1848', 'year': 1848},
    {'name': 'American Civil War', 'year': 1861},
    {'name': 'World War I', 'year': 1914},
    {'name': 'Russian Revolution', 'year': 1917},
    {'name': 'World War II', 'year': 1939},
    {'name': 'Cold War begins', 'year': 1947},
    {'name': 'Korean War', 'year': 1950},
    {'name': 'Cuban Missile Crisis', 'year': 1962},
    {'name': 'Vietnam War escalation', 'year': 1965},
    {'name': 'Fall of Berlin Wall', 'year': 1989},
    {'name': 'Soviet Union collapse', 'year': 1991},
    {'name': '9/11 Attacks', 'year': 2001},
    {'name': 'Iraq War', 'year': 2003},
    {'name': 'Arab Spring', 'year': 2011},
    {'name': 'Russia annexes Crimea', 'year': 2014},
    {'name': 'Russo-Ukrainian War escalation', 'year': 2022},
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


def compute_material_velocity(counts: Dict[int, float], tau: float = 1.0) -> Dict[int, float]:
    """V(t) = [C(t) - C(t-tau)] / tau"""
    sorted_keys = sorted(counts.keys())
    velocity = {}
    for i, k in enumerate(sorted_keys):
        if i == 0:
            velocity[k] = 0.0
            continue
        prev_k = sorted_keys[i - 1]
        velocity[k] = (counts[k] - counts[prev_k]) / tau
    return velocity


def compute_material_acceleration(velocity: Dict[int, float], tau: float = 1.0) -> Dict[int, float]:
    """A(t) = [V(t) - V(t-tau)] / tau"""
    sorted_keys = sorted(velocity.keys())
    acceleration = {}
    for i, k in enumerate(sorted_keys):
        if i == 0:
            acceleration[k] = 0.0
            continue
        prev_k = sorted_keys[i - 1]
        acceleration[k] = (velocity[k] - velocity[prev_k]) / tau
    return acceleration


def compute_volatility(velocity: Dict[int, float], k: int = 5) -> Dict[int, float]:
    """Rolling volatility of velocity over k windows."""
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


def compute_event_type_diversity(year_types: Dict[int, Counter]) -> Dict[int, float]:
    """Compute coefficient of variation of event type counts per year as GSI proxy."""
    cv = {}
    for year, counter in year_types.items():
        counts = list(counter.values())
        if len(counts) < 2:
            cv[year] = 0.0
            continue
        mean_c = sum(counts) / len(counts)
        if mean_c == 0:
            cv[year] = 0.0
            continue
        std_c = math.sqrt(sum((c - mean_c) ** 2 for c in counts) / len(counts))
        cv[year] = std_c / mean_c
    return cv


def compute_fragmentation_velocity(cv: Dict[int, float], tau: float = 1.0) -> Dict[int, float]:
    """Delta_GSI(t) = [CV(t) - CV(t-tau)] / tau"""
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
    velocity: Dict[int, float],
    acceleration: Dict[int, float],
    frag_velocity: Dict[int, float],
    volatility: Dict[int, float],
    weights: Optional[Dict[str, float]] = None
) -> Dict[int, Dict]:
    """Compute aggregate SPI score from four components."""
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
# Data Loading
# ============================================================

def load_wikidata_events(path: str) -> List[Dict]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def aggregate_yearly(events: List[Dict]) -> Tuple[Dict[int, int], Dict[int, float], Dict[int, Counter]]:
    """Aggregate events by year. Returns (event_counts, death_counts, event_types)."""
    by_year = defaultdict(lambda: {'count': 0, 'deaths': 0.0, 'types': Counter()})

    for e in events:
        start = e.get('start', '')
        if not start:
            continue
        try:
            if start.startswith('-'):
                year = -int(start[1:5])
            else:
                year = int(start[:4])
        except ValueError:
            continue

        by_year[year]['count'] += 1
        by_year[year]['deaths'] += e.get('deaths', 0)
        by_year[year]['types'][e.get('type', 'unknown')] += 1

    years = sorted(by_year.keys())
    counts = {y: by_year[y]['count'] for y in years}
    deaths = {y: by_year[y]['deaths'] for y in years}
    types = {y: by_year[y]['types'] for y in years}
    return counts, deaths, types


# ============================================================
# Main Pipeline
# ============================================================

def compute_global_politics_spi(events: List[Dict], tau: int = 1) -> Dict[str, Any]:
    counts, deaths, year_types = aggregate_yearly(events)

    if len(counts) < 10:
        return {
            'domain': 'Global Politics (Wikidata)',
            'error': 'INSUFFICIENT_DATA',
            'confidence': 'INSUFFICIENT',
            'n_years': len(counts),
        }

    # Determine confidence based on data density
    total_events = sum(counts.values())
    year_span = max(counts.keys()) - min(counts.keys()) + 1
    events_per_year = total_events / year_span if year_span > 0 else 0

    if events_per_year >= 5:
        confidence = 'EXACT'
    elif events_per_year >= 1:
        confidence = 'RULER'
    else:
        confidence = 'INTERPOLATED'

    # Compute SPI components
    velocity = compute_material_velocity(counts, tau=tau)
    acceleration = compute_material_acceleration(velocity, tau=tau)
    cv = compute_event_type_diversity(year_types)
    frag_velocity = compute_fragmentation_velocity(cv, tau=tau)
    volatility = compute_volatility(velocity, k=5)

    spi_series = compute_spi_aggregate(velocity, acceleration, frag_velocity, volatility)

    # Find max SPI and alert windows
    max_spi_year = None
    max_spi_val = -float('inf')
    alert_windows = []
    for year, data in spi_series.items():
        if data['spi_aggregate'] > max_spi_val:
            max_spi_val = data['spi_aggregate']
            max_spi_year = year
        if data['alert_level'] in ('ELEVATED', 'CRITICAL'):
            alert_windows.append({
                'year': year,
                'spi_aggregate': data['spi_aggregate'],
                'alert_level': data['alert_level'],
            })

    # Align with known crises
    crisis_alignment = []
    for event in KNOWN_CRISES:
        event_year = event['year']
        # Find nearest year with SPI data
        available_years = sorted(spi_series.keys())
        if not available_years:
            continue
        nearest_y = min(available_years, key=lambda y: abs(y - event_year))
        spi_data = spi_series.get(nearest_y, {})
        crisis_alignment.append({
            'event_name': event['name'],
            'event_year': event_year,
            'nearest_spi_year': nearest_y,
            'spi_at_event': spi_data.get('spi_aggregate', None),
            'alert_at_event': spi_data.get('alert_level', 'UNKNOWN'),
            'captured': spi_data.get('alert_level') in ('ELEVATED', 'CRITICAL'),
            'events_that_year': counts.get(nearest_y, 0),
        })

    # Summary statistics
    all_spi = [d['spi_aggregate'] for d in spi_series.values()]
    mean_spi = sum(all_spi) / len(all_spi) if all_spi else 0
    std_spi = math.sqrt(sum((s - mean_spi) ** 2 for s in all_spi) / len(all_spi)) if len(all_spi) > 1 else 0

    # Top 10 SPI years
    top_spi_years = sorted(spi_series.items(), key=lambda x: x[1]['spi_aggregate'], reverse=True)[:10]

    return {
        'domain': 'Global Politics (Wikidata)',
        'tau_years': tau,
        'confidence': confidence,
        'period': [min(counts.keys()), max(counts.keys())],
        'n_events': total_events,
        'n_years': len(counts),
        'events_per_year': round(events_per_year, 2),
        'year_span': year_span,
        'mean_spi': round(mean_spi, 3),
        'std_spi': round(std_spi, 3),
        'max_spi_year': max_spi_year,
        'max_spi_value': round(max_spi_val, 3) if max_spi_val > -float('inf') else None,
        'top_spi_years': [
            {'year': y, 'spi': d['spi_aggregate'], 'alert': d['alert_level']}
            for y, d in top_spi_years
        ],
        'alert_windows': alert_windows,
        'crisis_alignment': crisis_alignment,
        'yearly_counts': {str(y): c for y, c in counts.items()},
        'yearly_deaths': {str(y): round(d, 1) for y, d in deaths.items()},
        'spi_series': {str(y): v for y, v in spi_series.items()},
        'velocity': {str(y): round(v, 3) for y, v in velocity.items()},
        'acceleration': {str(y): round(v, 3) for y, v in acceleration.items()},
        'volatility': {str(y): round(v, 3) for y, v in volatility.items()},
        'event_type_diversity_cv': {str(y): round(v, 3) for y, v in cv.items()},
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Loading Wikidata events...")
    events = load_wikidata_events(INPUT_PATH)
    print(f"  Loaded {len(events)} events")

    print("Computing Global Politics SPI...")
    result = compute_global_politics_spi(events, tau=1)

    output_path = os.path.join(OUTPUT_DIR, 'v17c_spi_global_politics.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {output_path}")

    # Print summary
    if 'error' in result:
        print(f"  ERROR: {result['error']}")
    else:
        print(f"  Period: {result['period'][0]} to {result['period'][1]}")
        print(f"  Events: {result['n_events']} over {result['n_years']} years")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Max SPI: {result['max_spi_value']} at year {result['max_spi_year']}")
        print(f"  Alert windows: {len(result['alert_windows'])}")
        captured = sum(1 for c in result['crisis_alignment'] if c['captured'])
        print(f"  Crises captured: {captured}/{len(result['crisis_alignment'])}")
        print("\n  Top 5 SPI years:")
        for item in result['top_spi_years'][:5]:
            print(f"    {item['year']}: SPI={item['spi']} ({item['alert']})")
        print("\n  Crisis alignment (sample):")
        for item in result['crisis_alignment'][:8]:
            marker = "✅" if item['captured'] else "❌"
            print(f"    {marker} {item['event_name']} ({item['event_year']}): SPI={item['spi_at_event']} @ {item['nearest_spi_year']}")

    print("\nDone!")


if __name__ == '__main__':
    main()
