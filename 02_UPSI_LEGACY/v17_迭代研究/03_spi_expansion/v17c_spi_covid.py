#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v17c SPI COVID-19 (OWID)
Compute SPI for COVID-19 case rates across major countries.

Methodology:
- Input: OWID daily case/death data from /tmp/owid_covid.csv
- τ = 7 days (weekly)
- Signal: new_cases_smoothed per 100K population (or raw if population not available)
- V(t) = (cases[t] - cases[t-7]) / 7
- A(t) = (V[t] - V[t-7]) / 7
- ΔGSI proxy = death-to-case ratio change (mortality shift indicator)
- σ_V = rolling std of V over 4 weeks
- SPI(t) = 0.35*z(V) + 0.25*z(A) + 0.25*|ΔGSI_z| + 0.15*z(σ_V)

Wave detection alignment:
- Alpha wave: late 2020 - early 2021
- Delta wave: mid 2021
- Omicron wave: late 2021 - early 2022
"""

import csv
import json
import math
import os
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

# ============================================================
# Configuration
# ============================================================

OWID_PATH = '/tmp/owid_covid.csv'
OUTPUT_DIR = '/Users/wangzr/Desktop/历史事件预测建模/v17_迭代研究/03_spi_expansion'

SPI_WEIGHTS = {
    'material_velocity': 0.35,
    'material_acceleration': 0.25,
    'fragmentation_velocity': 0.25,
    'disengagement_volatility': 0.15,
}

SPI_THRESHOLD_ELEVATED = 1.5
SPI_THRESHOLD_CRITICAL = 2.5

# Major countries to analyze
MAJOR_COUNTRIES = [
    "United States", "India", "Brazil", "Germany", "United Kingdom", "France",
    "Italy", "Spain", "Japan", "South Korea", "China", "Russia", "Canada",
    "Australia", "Mexico", "Indonesia", "Netherlands", "Turkey", "Switzerland",
    "Argentina", "Iran", "Sweden", "Belgium"
]

# Known COVID waves (approximate peak dates by country)
WAVE_EVENTS = {
    "United States": [
        {'name': 'Alpha wave peak', 'date': '2021-01-08'},
        {'name': 'Delta wave peak', 'date': '2021-09-01'},
        {'name': 'Omicron wave peak', 'date': '2022-01-10'},
    ],
    "United Kingdom": [
        {'name': 'Alpha wave peak', 'date': '2021-01-20'},
        {'name': 'Delta wave peak', 'date': '2021-07-19'},
        {'name': 'Omicron wave peak', 'date': '2022-01-05'},
    ],
    "Germany": [
        {'name': 'Alpha wave peak', 'date': '2021-01-15'},
        {'name': 'Delta wave peak', 'date': '2021-11-25'},
        {'name': 'Omicron wave peak', 'date': '2022-02-10'},
    ],
    "France": [
        {'name': 'Alpha wave peak', 'date': '2021-04-15'},
        {'name': 'Delta wave peak', 'date': '2021-08-10'},
        {'name': 'Omicron wave peak', 'date': '2022-01-25'},
    ],
    "Italy": [
        {'name': 'Alpha wave peak', 'date': '2021-01-20'},
        {'name': 'Delta wave peak', 'date': '2021-08-15'},
        {'name': 'Omicron wave peak', 'date': '2022-02-05'},
    ],
    "Japan": [
        {'name': 'Alpha wave peak', 'date': '2021-02-10'},
        {'name': 'Delta wave peak', 'date': '2021-09-01'},
        {'name': 'Omicron wave peak', 'date': '2022-02-10'},
    ],
    "China": [
        {'name': 'Wuhan outbreak', 'date': '2020-02-12'},
        {'name': 'Shanghai lockdown', 'date': '2022-04-13'},
        {'name': 'Post-zero-COVID surge', 'date': '2022-12-25'},
    ],
}

# ============================================================
# SPI Core Functions
# ============================================================

def z_score_dict(values: Dict[Any, float]) -> Dict[Any, float]:
    vals = list(values.values())
    if not vals:
        return {k: 0.0 for k in values}
    mean_v = sum(vals) / len(vals)
    std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / len(vals)) if len(vals) > 1 else 1.0
    if std_v == 0:
        std_v = 1.0
    return {k: (v - mean_v) / std_v for k, v in values.items()}


def compute_material_velocity(values: Dict[Any, float], tau: float = 1.0) -> Dict[Any, float]:
    sorted_keys = sorted(values.keys())
    velocity = {}
    for i, k in enumerate(sorted_keys):
        if i == 0:
            velocity[k] = 0.0
            continue
        prev_k = sorted_keys[i - 1]
        velocity[k] = (values[k] - values[prev_k]) / tau
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


def compute_volatility(velocity: Dict[Any, float], k: int = 4) -> Dict[Any, float]:
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
# Data Loading
# ============================================================

def load_owid_data(path: str) -> Dict[str, List[Dict]]:
    """Load OWID COVID data by country."""
    by_country = defaultdict(list)
    print(f"[load] Reading OWID data from {path}...")
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row.get('location', '')
            if country not in MAJOR_COUNTRIES:
                continue
            date = row.get('date', '')
            if not date:
                continue
            try:
                new_cases = float(row.get('new_cases_smoothed') or 0)
                new_deaths = float(row.get('new_deaths_smoothed') or 0)
                population = float(row.get('population') or 1)
            except (ValueError, TypeError):
                continue
            by_country[country].append({
                'date': date,
                'new_cases': new_cases,
                'new_deaths': new_deaths,
                'population': population,
                'case_rate_100k': (new_cases / population) * 100000 if population > 0 else 0,
                'death_rate_100k': (new_deaths / population) * 100000 if population > 0 else 0,
            })
    print(f"  Loaded data for {len(by_country)} countries")
    return dict(by_country)


# ============================================================
# SPI Computation per Country
# ============================================================

def compute_covid_spi_for_country(country: str, data: List[Dict], tau_days: int = 7) -> Dict[str, Any]:
    """Compute SPI for a single country's COVID data."""
    if len(data) < 30:
        return {
            'country': country,
            'error': 'INSUFFICIENT_DATA',
            'confidence': 'INSUFFICIENT',
            'n_records': len(data),
        }

    # Sort by date
    data = sorted(data, key=lambda x: x['date'])

    # Aggregate to weekly windows (tau = 7 days)
    window_cases = {}
    window_deaths = {}
    window_dates = {}

    for i, d in enumerate(data):
        date_obj = datetime.strptime(d['date'], '%Y-%m-%d')
        day_ordinal = date_obj.toordinal()
        w_start = (day_ordinal // tau_days) * tau_days
        if w_start not in window_cases:
            window_cases[w_start] = []
            window_deaths[w_start] = []
            window_dates[w_start] = []
        window_cases[w_start].append(d['case_rate_100k'])
        window_deaths[w_start].append(d['death_rate_100k'])
        window_dates[w_start].append(date_obj)

    # Mean case rate per window
    window_mean_cases = {}
    for w, vals in window_cases.items():
        window_mean_cases[w] = sum(vals) / len(vals)

    # Mortality ratio (deaths/cases) as GSI proxy
    window_mortality = {}
    for w in window_cases:
        c = sum(window_cases[w]) / len(window_cases[w])
        d = sum(window_deaths[w]) / len(window_deaths[w])
        window_mortality[w] = d / max(c, 0.001)  # avoid div by zero

    # Compute SPI components
    velocity = compute_material_velocity(window_mean_cases, tau=tau_days)
    acceleration = compute_material_acceleration(velocity, tau=tau_days)
    frag_velocity = compute_fragmentation_velocity(window_mortality, tau=tau_days)
    volatility = compute_volatility(velocity, k=4)

    spi_series = compute_spi_aggregate(velocity, acceleration, frag_velocity, volatility)

    # Convert to dated format
    spi_series_dated = {}
    for w, sdata in spi_series.items():
        ds = window_dates.get(w, [])
        if ds:
            start_d = min(ds)
            end_d = max(ds)
            spi_series_dated[start_d.strftime('%Y-%m-%d')] = {
                **sdata,
                'window_end': end_d.strftime('%Y-%m-%d'),
                'mean_case_rate_100k': round(window_mean_cases[w], 3),
                'mortality_ratio': round(window_mortality[w], 4),
                'n_days': len(ds),
            }

    # Find max SPI and alerts
    max_spi_window = None
    max_spi_val = -float('inf')
    alert_windows = []
    for w, sdata in spi_series.items():
        if sdata['spi_aggregate'] > max_spi_val:
            max_spi_val = sdata['spi_aggregate']
            max_spi_window = w
        if sdata['alert_level'] in ('ELEVATED', 'CRITICAL'):
            ds = window_dates.get(w, [])
            if ds:
                alert_windows.append({
                    'window_start': min(ds).strftime('%Y-%m-%d'),
                    'window_end': max(ds).strftime('%Y-%m-%d'),
                    'spi_aggregate': sdata['spi_aggregate'],
                    'alert_level': sdata['alert_level'],
                })

    # Align with wave events
    crisis_alignment = []
    for event in WAVE_EVENTS.get(country, []):
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        event_ordinal = event_date.toordinal()
        nearest_w = min(spi_series.keys(), key=lambda w: abs(w + tau_days / 2 - event_ordinal))
        sdata = spi_series.get(nearest_w, {})
        ds = window_dates.get(nearest_w, [])
        crisis_alignment.append({
            'event_name': event['name'],
            'event_date': event['date'],
            'nearest_window_start': min(ds).strftime('%Y-%m-%d') if ds else None,
            'nearest_window_end': max(ds).strftime('%Y-%m-%d') if ds else None,
            'spi_at_event': sdata.get('spi_aggregate', None),
            'alert_at_event': sdata.get('alert_level', 'UNKNOWN'),
            'captured': sdata.get('alert_level') in ('ELEVATED', 'CRITICAL'),
        })

    return {
        'country': country,
        'tau_days': tau_days,
        'confidence': 'EXACT',
        'n_records': len(data),
        'n_windows': len(window_mean_cases),
        'period': [data[0]['date'], data[-1]['date']],
        'spi_series': spi_series_dated,
        'max_spi_window': datetime.fromordinal(max_spi_window).strftime('%Y-%m-%d') if max_spi_window else None,
        'max_spi_value': round(max_spi_val, 3) if max_spi_val > -float('inf') else None,
        'alert_windows': alert_windows,
        'crisis_alignment': crisis_alignment,
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Computing COVID-19 SPI...")

    by_country = load_owid_data(OWID_PATH)

    all_results = {
        'meta': {
            'domain': 'COVID-19 (OWID)',
            'data_source': 'Our World in Data COVID-19 dataset',
            'tau_days': 7,
            'note': 'Weekly aggregation of daily case rates per 100K. '
                    'Velocity = case rate change. Fragmentation = mortality ratio change.',
        },
        'countries': {},
    }

    for country in MAJOR_COUNTRIES:
        if country not in by_country:
            print(f"  Skipping {country} (no data)")
            continue
        print(f"\n  Processing {country}...")
        result = compute_covid_spi_for_country(country, by_country[country], tau_days=7)
        all_results['countries'][country] = result

        if 'error' in result:
            print(f"    ERROR: {result['error']}")
        else:
            print(f"    Records: {result['n_records']} daily -> {result['n_windows']} weekly windows")
            print(f"    Max SPI: {result['max_spi_value']} at {result['max_spi_window']}")
            print(f"    Alert windows: {len(result['alert_windows'])}")
            captured = sum(1 for c in result['crisis_alignment'] if c['captured'])
            print(f"    Waves captured: {captured}/{len(result['crisis_alignment'])}")
            for item in result['crisis_alignment']:
                marker = "✅" if item['captured'] else "❌"
                print(f"      {marker} {item['event_name']} ({item['event_date']}): SPI={item['spi_at_event']} ({item['alert_at_event']})")

    output_path = os.path.join(OUTPUT_DIR, 'v17c_spi_covid.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n  -> Saved {output_path}")
    print("\nDone!")


if __name__ == '__main__':
    main()
