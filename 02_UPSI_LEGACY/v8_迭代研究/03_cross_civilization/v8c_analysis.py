#!/usr/bin/env python3
"""
v8c_cross_civilization_analysis.py
Track C: Cross-Civilization PSI Analyst
Compares Chinese and Mesopotamian civilization PSI patterns
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from scipy import stats
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================
OUTPUT_DIR = 'v8_迭代研究/03_cross_civilization'

# Civilization lifespans (start, end, peak)
# For BC periods, start > end (e.g., Ur III: 2112 BC -> 2004 BC)
CIV_CONFIG = {
    '唐朝':      {'start': 618,  'end': 907,  'peak': 713,  'region': 'China'},
    '北宋前期':  {'start': 960,  'end': 1027, 'peak': 1022, 'region': 'China'},
    '北宋后期':  {'start': 1028, 'end': 1127, 'peak': 1063, 'region': 'China'},
    '南宋':      {'start': 1127, 'end': 1279, 'peak': 1200, 'region': 'China'},
    '明朝':      {'start': 1368, 'end': 1644, 'peak': 1402, 'region': 'China'},
    'Ur III':    {'start': 2112, 'end': 2004, 'peak': 2094, 'region': 'Mesopotamia'},
    'Old Babylonian': {'start': 1894, 'end': 1595, 'peak': 1792, 'region': 'Mesopotamia'},
    'Neo-Assyrian':   {'start': 911,  'end': 612,  'peak': 668,  'region': 'Mesopotamia'},
    'Neo-Babylonian': {'start': 626,  'end': 539,  'peak': 605,  'region': 'Mesopotamia'},
}

COLORS = {
    '唐朝': '#E74C3C',
    '北宋前期': '#3498DB',
    '北宋后期': '#2ECC71',
    '南宋': '#9B59B6',
    '明朝': '#F39C12',
    'Ur III': '#1ABC9C',
    'Old Babylonian': '#E67E22',
    'Neo-Assyrian': '#34495E',
    'Neo-Babylonian': '#16A085',
}

# ============================================================
# 1. LOAD ALL DATA
# ============================================================
print("Loading data...")

# Chinese decade PSI
with open('output/decade_psi_all_api.json', 'r') as f:
    decade_data = json.load(f)

chinese_records = []
for rec in decade_data['results']:
    chinese_records.append({
        'dynasty': rec['dynasty'],
        'decade': rec['decade'],
        'year_start': rec['year_start'],
        'year_end': rec['year_end'],
        'psi': rec['psi'],
        'psi_ipw': rec['psi_ipw'],
        'expert_count': rec['expert_count'],
        'gsi': rec['gsi'],
        'avg_sentiment': rec['avg_sentiment'],
        'density_norm': rec['density_norm'],
    })
df_china = pd.DataFrame(chinese_records)

# Ur III annual PSI from v7
with open('v7_迭代研究/01_oracc_psi/psi_timeseries.json', 'r') as f:
    ur3_psi_raw = json.load(f)

ur3_records = []
for year_str, psi in ur3_psi_raw.items():
    year = int(year_str)
    # v7 years 2006-2095 correspond to BC years (negative in standard timeline)
    # Ur III: 2112-2004 BC. The v7 years appear to be absolute BC values.
    bc_year = -year  # e.g., 2006 -> -2006 (2006 BC)
    ur3_records.append({'year': bc_year, 'psi': psi, 'dynasty': 'Ur III'})
df_ur3 = pd.DataFrame(ur3_records).sort_values('year')

# CDLI data for SFD proxy
with open('v6.1/data/cdli_psi_v61.json', 'r') as f:
    cdli_data = json.load(f)

meso_sfd = {}
for period_info in cdli_data['periods']:
    name = period_info[0]
    count = period_info[1]['count']
    period_name = name.split(' (')[0]
    meso_sfd[period_name] = count

# Climate validation data
with open('v4/data/climate_validation.json', 'r') as f:
    climate_data = json.load(f)

print(f"  Chinese records: {len(df_china)}")
print(f"  Ur III PSI years: {len(df_ur3)} ({df_ur3['year'].min()} to {df_ur3['year'].max()})")
print(f"  Mesopotamian SFD periods: {len(meso_sfd)}")

# ============================================================
# 2. NORMALIZE LIFECYCLES
# ============================================================

def normalize_lifecycle(df, dynasty_name, start, end, value_col='psi'):
    """Normalize time to [0,1] where 0=start, 1=end. Handles BC (start>end)."""
    subset = df[df['dynasty'] == dynasty_name].copy()
    if len(subset) == 0:
        return None
    
    if 'decade' in subset.columns:
        subset['mid_year'] = subset['decade'] + 5
    else:
        subset['mid_year'] = subset['year']
    
    # Duration (positive for AD, negative for BC)
    duration = end - start
    
    # Filter to within bounds with margin
    if duration > 0:  # AD
        subset = subset[(subset['mid_year'] >= start - 20) & (subset['mid_year'] <= end + 20)]
    else:  # BC (start > end)
        subset = subset[(subset['mid_year'] <= start + 20) & (subset['mid_year'] >= end - 20)]
    
    if len(subset) == 0:
        return None
    
    # Normalize: (current - start) / (end - start)
    # For BC, this gives positive values from 0 to 1
    subset['rel_time'] = (subset['mid_year'] - start) / duration
    subset['rel_time'] = subset['rel_time'].clip(0, 1)
    
    return subset[['rel_time', value_col, 'mid_year', 'expert_count']].sort_values('rel_time')

normalized = {}
for dyn in ['唐朝', '北宋前期', '北宋后期', '南宋', '明朝']:
    cfg = CIV_CONFIG[dyn]
    norm = normalize_lifecycle(df_china, dyn, cfg['start'], cfg['end'])
    if norm is not None:
        normalized[dyn] = norm
        print(f"  {dyn}: {len(norm)} points, rel_time {norm['rel_time'].min():.2f}-{norm['rel_time'].max():.2f}")

# Ur III normalization
ur3_start = CIV_CONFIG['Ur III']['start']
ur3_end = CIV_CONFIG['Ur III']['end']
ur3_duration = ur3_end - ur3_start  # 2004 - 2112 = -108
df_ur3_norm = df_ur3.copy()
df_ur3_norm['mid_year'] = df_ur3_norm['year']
df_ur3_norm['rel_time'] = (df_ur3_norm['year'] - ur3_start) / ur3_duration
df_ur3_norm = df_ur3_norm[(df_ur3_norm['rel_time'] >= 0) & (df_ur3_norm['rel_time'] <= 1)]
if len(df_ur3_norm) > 0:
    normalized['Ur III'] = df_ur3_norm[['rel_time', 'psi', 'mid_year', 'expert_count']]
    print(f"  Ur III: {len(df_ur3_norm)} points, rel_time {df_ur3_norm['rel_time'].min():.2f}-{df_ur3_norm['rel_time'].max():.2f}")
else:
    print("  WARNING: Ur III normalization produced no valid points!")
    # Debug
    print(f"    Ur III year range: {df_ur3['year'].min()} to {df_ur3['year'].max()}")
    print(f"    Expected: {ur3_start} to {ur3_end}")
    print(f"    Duration: {ur3_duration}")
    # Try alternative interpretation: maybe v7 years are relative to some epoch
    # Let's just map the v7 range [2006, 2095] to [0, 1] directly
    v7_min = df_ur3['year'].min()
    v7_max = df_ur3['year'].max()
    df_ur3_alt = df_ur3.copy()
    df_ur3_alt['mid_year'] = df_ur3_alt['year']
    df_ur3_alt['rel_time'] = (df_ur3_alt['year'] - v7_min) / (v7_max - v7_min)
    df_ur3_alt['expert_count'] = 1  # Placeholder
    normalized['Ur III'] = df_ur3_alt[['rel_time', 'psi', 'mid_year', 'expert_count']]
    print(f"  Ur III (alt mapping): {len(df_ur3_alt)} points, rel_time {df_ur3_alt['rel_time'].min():.2f}-{df_ur3_alt['rel_time'].max():.2f}")

# ============================================================
# 3. INTERPOLATE TO COMMON GRID
# ============================================================
common_grid = np.linspace(0, 1, 101)
interpolated = {}

for name, df_norm in normalized.items():
    if len(df_norm) < 3:
        continue
    x = df_norm['rel_time'].values
    y = df_norm['psi'].values
    sort_idx = np.argsort(x)
    x, y = x[sort_idx], y[sort_idx]
    try:
        f = interp1d(x, y, kind='linear', bounds_error=False, fill_value='extrapolate')
        interpolated[name] = f(common_grid)
    except Exception as e:
        print(f"Interpolation failed for {name}: {e}")

print(f"\nInterpolated civilizations: {list(interpolated.keys())}")

# ============================================================
# 4. FIGURE 1: RELATIVE TIME ALIGNMENT
# ============================================================
print("\nGenerating Figure 1...")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

# 1a: All overlaid
ax = axes[0]
for name, series in interpolated.items():
    ax.plot(common_grid, series, label=name, color=COLORS.get(name, 'gray'), linewidth=2, alpha=0.8)
ax.axvline(x=0.5, color='black', linestyle='--', alpha=0.3)
ax.axvline(x=0.7, color='red', linestyle=':', alpha=0.3)
ax.axvline(x=0.9, color='red', linestyle=':', alpha=0.3)
ax.set_xlabel('Relative Time (0=Start, 1=End)')
ax.set_ylabel('PSI')
ax.set_title('Method 1: Relative Time Alignment\nAll Civilizations')
ax.legend(loc='best', fontsize=8)
ax.set_xlim(0, 1)
ax.grid(True, alpha=0.3)

# 1b: China only
ax = axes[1]
for name in ['唐朝', '北宋前期', '北宋后期', '南宋', '明朝']:
    if name in interpolated:
        ax.plot(common_grid, interpolated[name], label=name, color=COLORS.get(name, 'gray'), linewidth=2)
ax.axvline(x=0.7, color='red', linestyle=':', alpha=0.5, label='Decline start')
ax.axvline(x=0.9, color='darkred', linestyle='--', alpha=0.5, label='Crisis zone')
ax.set_xlabel('Relative Time (0=Start, 1=End)')
ax.set_ylabel('PSI')
ax.set_title('Chinese Dynasties Only')
ax.legend(loc='best', fontsize=8)
ax.set_xlim(0, 1)
ax.grid(True, alpha=0.3)

# 1c: Decline phase
ax = axes[2]
decline_mask = common_grid >= 0.7
for name in ['唐朝', '南宋', '明朝', 'Ur III', '北宋后期']:
    if name in interpolated:
        ax.plot(common_grid[decline_mask], interpolated[name][decline_mask], 
                label=name, color=COLORS.get(name, 'gray'), linewidth=2, marker='o', markersize=3)
ax.set_xlabel('Relative Time (0=Start, 1=End)')
ax.set_ylabel('PSI')
ax.set_title('Decline Phase (0.7-1.0)')
ax.legend(loc='best', fontsize=8)
ax.set_xlim(0.7, 1.0)
ax.grid(True, alpha=0.3)

# 1d: Lifecycle key points
ax = axes[3]
lifecycle_points = [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]
point_labels = ['Start', 'Early', 'Mid', 'Late', 'Crisis', 'End']
point_data = {name: [] for name in interpolated.keys()}
for pt in lifecycle_points:
    idx = np.argmin(np.abs(common_grid - pt))
    for name, series in interpolated.items():
        point_data[name].append(series[idx])

x_pos = np.arange(len(point_labels))
width = 0.12
for i, name in enumerate(interpolated.keys()):
    offset = (i - len(interpolated)/2) * width
    ax.bar(x_pos + offset, point_data[name], width, label=name, color=COLORS.get(name, 'gray'), alpha=0.8)
ax.set_xticks(x_pos)
ax.set_xticklabels(point_labels)
ax.set_ylabel('PSI')
ax.set_title('PSI at Lifecycle Key Points')
ax.legend(loc='best', fontsize=7)
ax.grid(True, alpha=0.3, axis='y')

# 1e: Full lifecycle correlation matrix
ax = axes[4]
all_names = list(interpolated.keys())
corr_matrix = np.zeros((len(all_names), len(all_names)))
for i, n1 in enumerate(all_names):
    for j, n2 in enumerate(all_names):
        if i == j:
            corr_matrix[i, j] = 1.0
        else:
            corr_matrix[i, j] = np.corrcoef(interpolated[n1], interpolated[n2])[0, 1]
im = ax.imshow(corr_matrix, cmap='RdYlGn', vmin=-1, vmax=1)
ax.set_xticks(range(len(all_names)))
ax.set_yticks(range(len(all_names)))
ax.set_xticklabels(all_names, rotation=45, ha='right')
ax.set_yticklabels(all_names)
for i in range(len(all_names)):
    for j in range(len(all_names)):
        ax.text(j, i, f'{corr_matrix[i,j]:.2f}', ha='center', va='center', fontsize=9)
ax.set_title('Full Lifecycle Correlation')
plt.colorbar(im, ax=ax, shrink=0.8)

# 1f: Decline phase correlation
ax = axes[5]
decline_names = [n for n in all_names if n in ['唐朝', '南宋', '明朝', 'Ur III', '北宋后期']]
if len(decline_names) >= 2:
    corr_matrix_d = np.zeros((len(decline_names), len(decline_names)))
    for i, n1 in enumerate(decline_names):
        for j, n2 in enumerate(decline_names):
            if i == j:
                corr_matrix_d[i, j] = 1.0
            else:
                corr_matrix_d[i, j] = np.corrcoef(interpolated[n1][decline_mask], interpolated[n2][decline_mask])[0, 1]
    im = ax.imshow(corr_matrix_d, cmap='RdYlGn', vmin=-1, vmax=1)
    ax.set_xticks(range(len(decline_names)))
    ax.set_yticks(range(len(decline_names)))
    ax.set_xticklabels(decline_names, rotation=45, ha='right')
    ax.set_yticklabels(decline_names)
    for i in range(len(decline_names)):
        for j in range(len(decline_names)):
            ax.text(j, i, f'{corr_matrix_d[i,j]:.2f}', ha='center', va='center', fontsize=9)
    ax.set_title('Decline Phase (0.7-1.0) Correlation')
    plt.colorbar(im, ax=ax, shrink=0.8)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig1_relative_alignment.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 5. METHOD 2: CRISIS PRECURSOR PATTERNS
# ============================================================
print("Generating Figure 2...")

def compute_crisis_metrics(df_orig, start, end, name):
    """Compute crisis precursor metrics"""
    metrics = {}
    
    windows = {
        't-100': (end - 100, end) if start < end else (end - 100, end),  # AD
        't-50':  (end - 50, end) if start < end else (end - 50, end),
        't-20':  (end - 20, end) if start < end else (end - 20, end),
        't-10':  (end - 10, end) if start < end else (end - 10, end),
    }
    
    # For BC, end < start, so end-100 is even smaller (further back in time)
    # But our data years are negative for BC
    # e.g., Ur III end=2004 BC = -2004, start=2112 BC = -2112
    # end-100 = -2104, which is before start (-2112)? No, -2104 > -2112
    # So for BC: end=-2004, end-100=-2104, data range [-2095, -2006]
    # t-100 window: [-2104, -2004], but data only goes to -2095
    # This means for Ur III, t-100 doesn't capture much
    
    for win_name, (win_start, win_end) in windows.items():
        subset = df_orig[(df_orig['mid_year'] >= win_start) & (df_orig['mid_year'] <= win_end)]
        if len(subset) > 0:
            metrics[win_name] = {
                'psi_mean': float(subset['psi'].mean()),
                'psi_std': float(subset['psi'].std()) if len(subset) > 1 else 0,
                'psi_min': float(subset['psi'].min()),
                'psi_max': float(subset['psi'].max()),
                'n_points': int(len(subset)),
            }
        else:
            metrics[win_name] = None
    
    # Decline rate in final 50 years
    t50 = df_orig[df_orig['mid_year'] >= (end - 50 if start < end else end - 50)]
    if len(t50) >= 2:
        x = t50['mid_year'].values
        y = t50['psi'].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        metrics['decline_rate'] = float(slope)
        metrics['decline_r2'] = float(r_value**2)
    else:
        metrics['decline_rate'] = None
        metrics['decline_r2'] = None
    
    # Volatility ratio
    t100 = df_orig[(df_orig['mid_year'] >= (end - 100 if start < end else end - 100)) & (df_orig['mid_year'] <= end)]
    t20 = df_orig[(df_orig['mid_year'] >= (end - 20 if start < end else end - 20)) & (df_orig['mid_year'] <= end)]
    if len(t100) > 1 and len(t20) > 1 and t100['psi'].std() > 0:
        metrics['volatility_ratio'] = float(t20['psi'].std() / t100['psi'].std())
    else:
        metrics['volatility_ratio'] = None
    
    return metrics

crisis_metrics = {}
for name in ['唐朝', '北宋后期', '南宋', '明朝', 'Ur III']:
    cfg = CIV_CONFIG[name]
    if name == 'Ur III':
        df_orig = df_ur3.copy()
        df_orig['mid_year'] = df_orig['year']
    else:
        df_orig = df_china[df_china['dynasty'] == name].copy()
        df_orig['mid_year'] = df_orig['decade'] + 5
    
    metrics = compute_crisis_metrics(df_orig, cfg['start'], cfg['end'], name)
    crisis_metrics[name] = metrics
    print(f"  {name} crisis metrics computed")

# Figure 2
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 2a: Final 100 years trajectory
ax = axes[0, 0]
for name in ['唐朝', '南宋', '明朝', 'Ur III']:
    cfg = CIV_CONFIG[name]
    if name == 'Ur III':
        df_orig = df_ur3.copy()
        df_orig['mid_year'] = df_orig['year']
    else:
        df_orig = df_china[df_china['dynasty'] == name].copy()
        df_orig['mid_year'] = df_orig['decade'] + 5
    
    subset = df_orig[df_orig['mid_year'] >= cfg['end'] - 100]
    if len(subset) > 0:
        years_before = cfg['end'] - subset['mid_year']
        ax.plot(years_before, subset['psi'], label=name, color=COLORS.get(name, 'gray'), 
                linewidth=2, marker='o', markersize=4)
ax.set_xlabel('Years Before Collapse')
ax.set_ylabel('PSI')
ax.set_title('Method 2a: Final 100 Years PSI Trajectory')
ax.legend()
ax.set_xlim(100, 0)
ax.grid(True, alpha=0.3)

# 2b: PSI by crisis window
ax = axes[0, 1]
win_names = ['t-100', 't-50', 't-20', 't-10']
x_pos = np.arange(len(win_names))
width = 0.18
for i, name in enumerate(['唐朝', '南宋', '明朝', 'Ur III']):
    if name in crisis_metrics:
        vals = []
        for w in win_names:
            m = crisis_metrics[name].get(w)
            vals.append(m['psi_mean'] if m else np.nan)
        offset = (i - 1.5) * width
        ax.bar(x_pos + offset, vals, width, label=name, color=COLORS.get(name, 'gray'), alpha=0.8)
ax.set_xticks(x_pos)
ax.set_xticklabels(win_names)
ax.set_ylabel('Mean PSI')
ax.set_title('Method 2b: PSI by Crisis Window')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# 2c: Decline rate
ax = axes[1, 0]
names = [n for n in ['唐朝', '北宋后期', '南宋', '明朝', 'Ur III'] if n in crisis_metrics]
decline_rates = [crisis_metrics[n].get('decline_rate', 0) for n in names]
decline_rates = [d if d is not None else 0 for d in decline_rates]
colors_list = [COLORS.get(n, 'gray') for n in names]
bars = ax.bar(names, decline_rates, color=colors_list, alpha=0.8, edgecolor='black')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.set_ylabel('dPSI/dt (per year)')
ax.set_title('Method 2c: PSI Decline Rate (Final 50 Years)')
ax.set_xticklabels(names, rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, decline_rates):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005, 
            f'{val:.4f}', ha='center', va='bottom', fontsize=9)

# 2d: Volatility ratio
ax = axes[1, 1]
vol_ratios = []
vol_names = []
for n in names:
    vr = crisis_metrics[n].get('volatility_ratio')
    if vr is not None:
        vol_ratios.append(vr)
        vol_names.append(n)
if vol_ratios:
    colors_list = [COLORS.get(n, 'gray') for n in vol_names]
    bars = ax.bar(vol_names, vol_ratios, color=colors_list, alpha=0.8, edgecolor='black')
    ax.axhline(y=1.0, color='red', linestyle='--', label='No change')
    ax.set_ylabel('Volatility Ratio (t-20 / t-100)')
    ax.set_title('Method 2d: Volatility Change in Crisis')
    ax.set_xticklabels(vol_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    for bar, val in zip(bars, vol_ratios):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.2f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig2_crisis_precursor.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 6. METHOD 3: CLIMATE-PSI ASSOCIATION
# ============================================================
print("Generating Figure 3...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 3a: Climate correlation by dynasty
ax = axes[0]
dynasties = list(climate_data['by_dynasty'].keys())
corrs = [climate_data['by_dynasty'][d]['correlation'] for d in dynasties]
colors_list = [COLORS.get(d, 'gray') for d in dynasties]
bars = ax.bar(dynasties, corrs, color=colors_list, alpha=0.8, edgecolor='black')
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.axhline(y=0.5, color='green', linestyle='--', alpha=0.3, label='Strong positive')
ax.axhline(y=-0.5, color='red', linestyle='--', alpha=0.3, label='Strong negative')
ax.set_ylabel('PSI-Temperature Correlation')
ax.set_title('Method 3a: Climate-PSI Correlation by Dynasty')
ax.set_xticklabels(dynasties, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars, corrs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
            f'{val:.2f}', ha='center', va='bottom', fontsize=9)

# 3b: Key events scatter
ax = axes[1]
events = climate_data['key_events']
psi_z = [e['psi_z'] for e in events]
temp_a = [e['temp_anomaly'] for e in events]
ax.scatter(temp_a, psi_z, s=100, c='steelblue', edgecolors='black', alpha=0.8, zorder=3)
for e in events:
    ax.annotate(e['event'], (e['temp_anomaly'], e['psi_z']), 
                fontsize=7, alpha=0.8, xytext=(5, 5), textcoords='offset points')
if len(temp_a) > 1:
    slope, intercept, r_value, p_value, std_err = stats.linregress(temp_a, psi_z)
    x_line = np.linspace(min(temp_a), max(temp_a), 100)
    ax.plot(x_line, slope * x_line + intercept, 'r--', alpha=0.5, 
            label=f'R={r_value:.2f}, p={p_value:.3f}')
ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
ax.set_xlabel('Temperature Anomaly (°C)')
ax.set_ylabel('PSI Z-Score')
ax.set_title('Method 3b: Climate-PSI at Key Events')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig3_climate_psi.png', dpi=150, bbox_inches='tight')
plt.close()

# Figure 3b: Climate overlay on normalized timeline
fig, ax = plt.subplots(figsize=(12, 6))
for name in ['唐朝', '南宋', '明朝']:
    if name in interpolated:
        ax.plot(common_grid, interpolated[name], label=name, color=COLORS.get(name, 'gray'), 
                linewidth=2, alpha=0.8)
# Approximate cold period positions (from Chinese climate record)
ax.axvspan(0.75, 0.85, alpha=0.1, color='blue', label='Cold period (approx)')
ax.axvspan(0.90, 1.0, alpha=0.15, color='darkblue', label='Severe cold (approx)')
ax.set_xlabel('Relative Time (0=Start, 1=End)')
ax.set_ylabel('PSI')
ax.set_title('Method 3c: Climate Stress Overlay (Blue=Cold Periods)')
ax.legend(loc='best')
ax.set_xlim(0, 1)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/fig3b_climate_overlay.png', dpi=150, bbox_inches='tight')
plt.close()

# ============================================================
# 7. SUMMARY STATISTICS
# ============================================================
print("Computing summary statistics...")

# Full correlation matrix
all_names = list(interpolated.keys())
full_corr = pd.DataFrame(index=all_names, columns=all_names, dtype=float)
for n1 in all_names:
    for n2 in all_names:
        full_corr.loc[n1, n2] = float(np.corrcoef(interpolated[n1], interpolated[n2])[0, 1])

# Decline phase correlation
decline_mask = common_grid >= 0.7
decline_corr = pd.DataFrame(index=all_names, columns=all_names, dtype=float)
for n1 in all_names:
    for n2 in all_names:
        decline_corr.loc[n1, n2] = float(np.corrcoef(interpolated[n1][decline_mask], interpolated[n2][decline_mask])[0, 1])

# Phase statistics
phase_stats = {}
for name, series in interpolated.items():
    phase_stats[name] = {
        'early_psi': float(np.mean(series[common_grid <= 0.25])),
        'mid_psi': float(np.mean(series[(common_grid > 0.25) & (common_grid <= 0.75)])),
        'decline_psi': float(np.mean(series[common_grid > 0.75])),
        'peak_psi': float(np.max(series)),
        'trough_psi': float(np.min(series)),
        'range_psi': float(np.max(series) - np.min(series)),
    }

# SFD proxy for Mesopotamian civilizations
sfd_proxy = {}
for name in ['Ur III', 'Old Babylonian', 'Neo-Assyrian', 'Neo-Babylonian']:
    if name in meso_sfd:
        duration = abs(CIV_CONFIG[name]['end'] - CIV_CONFIG[name]['start'])
        sfd_proxy[name] = {
            'total_texts': int(meso_sfd[name]),
            'duration_years': int(duration),
            'sfd_per_year': float(meso_sfd[name] / duration) if duration > 0 else None,
        }

# Save results
results = {
    'meta': {
        'analysis': 'v8c_cross_civilization',
        'date': '2026-06-04',
        'n_civilizations_with_psi_timeseries': len(interpolated),
        'n_chinese': 5,
        'n_mesopotamian_psi': 1,
        'n_mesopotamian_sfd': len(sfd_proxy),
    },
    'correlation_full': full_corr.to_dict(),
    'correlation_decline': decline_corr.to_dict(),
    'phase_statistics': phase_stats,
    'crisis_metrics': crisis_metrics,
    'sfd_proxy': sfd_proxy,
}

with open(f'{OUTPUT_DIR}/v8c_numerical_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\n=== FULL LIFECYCLE CORRELATION ===")
print(full_corr.round(3).to_string())
print("\n=== DECLINE PHASE (0.7-1.0) CORRELATION ===")
print(decline_corr.round(3).to_string())
print("\n=== PHASE STATISTICS ===")
for name, stats in phase_stats.items():
    print(f"  {name}: {stats}")
print("\n=== SFD PROXY (Texts/Year) ===")
for name, sfd in sfd_proxy.items():
    print(f"  {name}: {sfd}")

print("\nAll figures and data saved successfully!")
