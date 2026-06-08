#!/usr/bin/env python3
"""运行四诊合参2.0验证（本地化，无网络依赖）"""
import sys, os
sys.path.insert(0, '/Users/tianjangwang/Documents/历史事件预测建模')
os.chdir('/Users/tianjangwang/Documents/历史事件预测建模')

# 1. 验证CNHGIS内置映射
try:
    from four_diagnosis_v2.cnhgis import CNHGISClient
    geo = CNHGISClient()
    test_places = [
        ('长安', (108.94, 34.34)),
        ('汴京', (114.35, 34.79)),
        ('临安', (120.19, 30.26)),
        ('洛阳', (112.45, 34.62)),
        ('燕京', (116.41, 39.93)),
        ('成都', (104.06, 30.67)),
        ('广州', (113.26, 23.13)),
        ('泉州', (118.68, 24.89)),
    ]
    success = 0
    for name, expected in test_places:
        r = geo.geocode(name)
        if r:
            lon, lat = r['lon'], r['lat']
            diff = ((lon-expected[0])**2 + (lat-expected[1])**2)**0.5
            conf = r.get('confidence', 0)
            ok = diff < 1.0 and conf >= 0.7
            print('GEO: {} ({:.2f},{:.2f}) conf={:.2f} diff={:.3f} OK={}'.format(name, lon, lat, conf, diff, ok))
            if ok: success += 1
        else:
            print('GEO: {} FAILED'.format(name))
    print('CNHGIS_SUCCESS: {}/{}'.format(success, len(test_places)))
except Exception as e:
    print('CNHGIS_ERROR:', str(e)[:100])

# 2. 测试four_diagnosis模块
try:
    from four_diagnosis_v2 import FourDiagnosisValidator, compute_four_diagnoses
    validator = FourDiagnosisValidator(consistency_threshold=0.7)
    diagnoses = compute_four_diagnoses(
        dynasty='明朝',
        expert_data=[{'y_coord': 35 + i * 0.1} for i in range(50)],
        climate_data={'temp_anomaly': 0.15, 'disaster_freq': 0.25, 'years': list(range(1560,1570))},
        text_sentiments=[0.5, 0.6, 0.7, -0.3, 0.4, 0.6, 0.5, -0.2, 0.3, 0.8],
    )
    result = validator.validate('明朝', diagnoses)
    print('DIAG_RESULT: final_psi={:.4f} consistency={:.4f} verdict={}'.format(
        result.final_psi, result.consistency_score, result.verdict))
    print('  modalities: ' + ', '.join('{}={:.4f}'.format(m, d.value) for m, d in result.modalities.items()))
    print('DIAG_OK: True' if result.verdict in ('accept', 'escalate') else 'DIAG_OK: False')
except Exception as e:
    print('DIAG_ERROR:', str(e)[:100])
    import traceback; traceback.print_exc()