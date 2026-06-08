#!/usr/bin/env python3
"""验证十年级PSI API输出"""
import json, os
path = '/Users/tianjangwang/Documents/历史事件预测建模/output/decade_psi_all_api.json'
if os.path.exists(path):
    with open(path) as f:
        d = json.load(f)
    results = d['results']
    print('Records: ' + str(len(results)))
    print('First 3: ' + str([(r['dynasty'], r['decade'], r['psi']) for r in results[:3]]))
    print('Last 3: ' + str([(r['dynasty'], r['decade'], r['psi']) for r in results[-3:]]))
else:
    print('FILE_NOT_FOUND')