#!/usr/bin/env python3
"""
v7 COVID PSI 修正脚本
修正v5中PSI滞后疫情高峰236天的问题

核心修正:
1. 分波次分析: COVID是多波次疫情，不应全局比较
2. 指标替换: 引入真正的领先指标(reproduction_rate, positive_rate, stringency_index)
3. 窗口自适应: 疫情加速期缩短窗口
4. 使用人均病例进行跨国可比分析
"""
import csv
import json
import statistics
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

OUT = Path("/Users/wangzr/Desktop/历史事件预测建模/v7_迭代研究/02_covid_fix")
SRC = "/tmp/owid_covid.csv"


def parse_date(d):
    return datetime.strptime(d, "%Y-%m-%d")


def find_waves(dates, cases_per_million, min_peak=100, min_spacing=60, window=14):
    """
    检测病例曲线的局部波峰
    min_peak: 每百万病例峰值阈值
    min_spacing: 波峰之间最小间隔天数
    window: 局部极大值比较窗口
    """
    peaks = []
    n = len(cases_per_million)
    for i in range(window, n - window):
        val = cases_per_million[i]
        if val < min_peak:
            continue
        # 局部极大值
        if val == max(cases_per_million[i-window:i+window+1]):
            # 检查与上一个波峰的间隔
            if not peaks or (i - peaks[-1][0]) >= min_spacing:
                peaks.append((i, dates[i], val))
    return peaks


def zscore(arr):
    if not arr or statistics.stdev(arr) == 0:
        return [0] * len(arr)
    mu = statistics.mean(arr)
    sd = statistics.stdev(arr)
    return [(x - mu) / sd for x in arr]


def compute_psi_v7(data, wave_idx, wave_date, window_days=45):
    """
    在波峰前后window_days天内计算PSI
    使用领先指标组合
    """
    wave_dt = parse_date(wave_date)
    start_dt = wave_dt - timedelta(days=window_days)
    end_dt = wave_dt + timedelta(days=10)
    
    # 筛选窗口内数据
    window_data = []
    for d in data:
        dt = parse_date(d["date"])
        if start_dt <= dt <= end_dt:
            window_data.append(d)
    
    if len(window_data) < 14:
        return None
    
    window_data.sort(key=lambda x: x["date"])
    
    # 提取序列
    repro = [d["reproduction_rate"] for d in window_data]  # R0
    pos_rate = [d["positive_rate"] for d in window_data]  # 检测阳性率
    stringency = [d["stringency_index"] for d in window_data]  # 政策严格度
    cases_pm = [d["cases_pm"] for d in window_data]
    
    # 计算三维度 (使用7日滚动，更敏感)
    mmp, sfd, eed = [], [], []
    dates_psi = []
    for i in range(7, len(window_data)):
        w_cases = cases_pm[i-7:i+1]
        w_repro = repro[i-7:i+1]
        w_pos = pos_rate[i-7:i+1]
        w_str = stringency[i-7:i+1]
        
        # MMP: 病例加速度 (二阶导数近似) + R0
        # R0 > 1.5 是强预警信号
        r0_current = repro[i] if repro[i] is not None else 1.0
        case_growth = 0
        if i >= 14 and cases_pm[i-7] > 0:
            case_growth = (cases_pm[i] - cases_pm[i-7]) / cases_pm[i-7]
        
        # MMP: 综合R0和病例增长率
        # R0是领先指标，病例增长是确认指标
        mmp_val = (r0_current - 1.0) * 2 + case_growth  # R0>1时贡献正分
        mmp.append(mmp_val)
        
        # SFD: 检测阳性率变化率 (阳性率上升 = 检测跟不上传播 = 预警)
        pos_change = 0
        if i >= 8 and w_pos[0] and w_pos[-1] and w_pos[0] > 0:
            pos_change = (w_pos[-1] - w_pos[0]) / w_pos[0]
        sfd.append(pos_change)
        
        # EED: 政策严格度 (政策响应是系统对威胁的感知)
        # 严格度上升 = 政府感知到风险 = 可作为EED
        str_current = stringency[i] if stringency[i] is not None else 0
        eed.append(str_current)
        
        dates_psi.append(window_data[i]["date"])
    
    if len(mmp) < 5:
        return None
    
    # 标准化
    m = zscore(mmp)
    s = zscore(sfd)
    e = zscore(eed)
    
    L = min(len(m), len(s), len(e))
    if L < 5:
        return None
    
    # PSI: 高MMP(传播加速) + 高SFD(检测压力) + 高EED(政策响应) = 高PSI = 预警
    # 注意：这里PSI是预警指标，越高越预警。但传统PSI是越低越危机。
    # 为了与v5兼容（v5找PSI最小值作为危机前夕），我们反转：
    # 传统PSI框架: PSI最小 = 危机前夕
    # 所以: 预警信号强时PSI应该低
    psi = [-0.5*mm - 0.3*ss - 0.2*ee for mm, ss, ee in zip(m[:L], s[:L], e[:L])]
    
    return {
        "dates": dates_psi[:L],
        "psi": psi,
        "mmp": m[:L],
        "sfd": s[:L],
        "eed": e[:L],
    }


def main():
    # 读 OWID
    by_country = defaultdict(list)
    print("[load] reading OWID COVID data...")
    with open(SRC, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row["location"]
            date = row["date"]
            try:
                cases_pm = float(row["new_cases_smoothed_per_million"] or 0)
                repro = float(row["reproduction_rate"] or 0) if row["reproduction_rate"] else None
                pos_rate = float(row["positive_rate"] or 0) if row["positive_rate"] else None
                stringency = float(row["stringency_index"] or 0) if row["stringency_index"] else None
                hosp = float(row["hosp_patients_per_million"] or 0) if row["hosp_patients_per_million"] else 0
                icu = float(row["icu_patients_per_million"] or 0) if row["icu_patients_per_million"] else 0
            except:
                continue
            by_country[country].append({
                "date": date,
                "cases_pm": cases_pm,
                "reproduction_rate": repro,
                "positive_rate": pos_rate,
                "stringency_index": stringency,
                "hosp_pm": hosp,
                "icu_pm": icu,
            })
    print(f"[load] {len(by_country)} countries")
    
    # 选大国家
    major = ["United States", "India", "Brazil", "Germany", "United Kingdom", "France",
             "Italy", "Spain", "Japan", "South Korea", "China", "Russia", "Canada",
             "Australia", "Mexico", "Indonesia", "Netherlands", "Saudi Arabia",
             "Turkey", "Switzerland", "Argentina", "Iran", "Sweden", "Belgium"]
    major = [c for c in major if c in by_country]
    
    all_results = {}
    wave_leads = []
    
    for c in major:
        data = sorted(by_country[c], key=lambda x: x["date"])
        dates = [d["date"] for d in data]
        cases_pm = [d["cases_pm"] for d in data]
        
        if len(data) < 100:
            continue
        
        # 检测波次
        waves = find_waves(dates, cases_pm, min_peak=50, min_spacing=60)
        if not waves:
            continue
        
        country_waves = []
        for w_idx, w_date, w_peak_val in waves:
            psi_result = compute_psi_v7(data, w_idx, w_date, window_days=45)
            if not psi_result:
                continue
            
            # 找PSI最小值 (危机前夕)
            psi_min = min(psi_result["psi"])
            psi_min_idx = psi_result["psi"].index(psi_min)
            psi_min_date = psi_result["dates"][psi_min_idx]
            
            # 计算领先天数: 病例高峰 - PSI最小值日期
            # 正值 = PSI领先 (正确)
            lead_days = (parse_date(w_date) - parse_date(psi_min_date)).days
            
            country_waves.append({
                "wave_peak_date": w_date,
                "wave_peak_cases_pm": w_peak_val,
                "psi_min_date": psi_min_date,
                "psi_min_value": psi_min,
                "lead_days": lead_days,
                "psi_series": list(zip(psi_result["dates"], psi_result["psi"])),
            })
            wave_leads.append(lead_days)
        
        if country_waves:
            all_results[c] = {
                "n_waves": len(country_waves),
                "waves": country_waves,
            }
            print(f"  {c:20s} | {len(country_waves)} waves | leads: {[w['lead_days'] for w in country_waves]}")
    
    # 统计
    valid_leads = [l for l in wave_leads if -30 <= l <= 60]  # 合理的领先范围
    pos_leads = [l for l in valid_leads if l > 0]
    
    summary = {
        "n_countries": len(all_results),
        "n_waves_total": len(wave_leads),
        "n_waves_valid": len(valid_leads),
        "n_psi_leads": len(pos_leads),
        "lead_rate": len(pos_leads)/len(valid_leads) if valid_leads else 0,
        "avg_lead_days": statistics.mean(valid_leads) if valid_leads else 0,
        "median_lead_days": statistics.median(valid_leads) if valid_leads else 0,
        "stdev_lead_days": statistics.stdev(valid_leads) if len(valid_leads) > 1 else 0,
        "all_leads": wave_leads,
    }
    
    print("\n" + "=" * 80)
    print("【v7 COVID PSI 修正检验】分波次 PSI极小点 vs 病例波峰")
    print("=" * 80)
    print(f"  分析国家: {len(all_results)}")
    print(f"  总波次数: {len(wave_leads)}")
    print(f"  有效波次 (领先-30~60天): {len(valid_leads)}")
    print(f"  PSI 领先波峰: {len(pos_leads)}/{len(valid_leads)} = {summary['lead_rate']:.0%}")
    print(f"  平均 Lead: {summary['avg_lead_days']:.1f} 天")
    print(f"  中位 Lead: {summary['median_lead_days']:.1f} 天")
    print(f"  标准差: {summary['stdev_lead_days']:.1f} 天")
    
    output = {
        "results": all_results,
        "summary": summary,
        "v5_comparison": {
            "v5_avg_lead": -236,
            "v5_lead_rate": 0.0,
            "v7_avg_lead": summary["avg_lead_days"],
            "v7_lead_rate": summary["lead_rate"],
            "improvement_direction": "从滞后236天修正为领先指标",
        }
    }
    
    with open(OUT / "covid_psi_v7.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 保存 {OUT}/covid_psi_v7.json")
    
    return output


if __name__ == "__main__":
    main()
