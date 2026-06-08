"""
Civilization-Oracle v2.5
CBDB SQLite → 四朝专家JSON导入脚本

用法:
    python cbdb_import.py                    # 导出全部朝代
    python cbdb_import.py --dynasty 北宋      # 仅北宋
    python cbdb_import.py --output data/experts_song.json
    python cbdb_import.py --check             # 仅检查CBDB连接
"""
import argparse
import json
import sqlite3
import sys
from datetime import datetime

# 朝代年份映射
# CBDB dynasty code → 中文朝代名
DYNASTY_CODES = {
    6: '唐朝',
    15: '宋',        # 需用生年细分北宋/南宋
    19: '明朝',
    20: '清朝',
}

# 宋朝内部分期（用生年）
SONG_PERIODS = {
    '北宋前期': (960, 1027),
    '北宋后期': (1028, 1127),
    '南宋': (1128, 1279),
}

DYNASTY_YEARS = {
    '北宋': (960, 1127),
    '南宋': (1128, 1279),
    '明朝': (1368, 1644),
    '唐朝': (618, 907),
    '唐朝前期': (618, 755),
    '唐朝后期': (755, 907),
}


def connect_cbdb(db_path='data/cbdb/cbdb.sqlite'):
    """连接CBDB数据库"""
    try:
        conn = sqlite3.connect(db_path)
        print(f"[✓] CBDB连接成功: {db_path}")
        return conn
    except Exception as e:
        print(f"[✗] CBDB连接失败: {e}")
        sys.exit(1)


def inspect_cbdb(conn):
    """检查CBDB结构和数据分布"""
    cur = conn.cursor()

    # 朝代分布
    cur.execute("""
        SELECT c_dy, COUNT(*) as cnt
        FROM biog_main
        WHERE c_dy IS NOT NULL AND c_dy != ''
        GROUP BY c_dy
        ORDER BY cnt DESC
    """)
    print("\n朝代分布：")
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]} 条")

    # 年份范围
    cur.execute("""
        SELECT
            MIN(c_birthyear) as min_by,
            MAX(c_birthyear) as max_by,
            COUNT(*) as total
        FROM biog_main
        WHERE c_birthyear > 0
    """)
    row = cur.fetchone()
    print(f"\n生年范围: {row[0]} - {row[1]} (共 {row[2]} 条有生年)")
    return cur


def load_experts_by_dynasty(conn, dynasty_name, min_year=None, max_year=None,
                             limit=None, include_coords=True):
    """
    从CBDB加载指定朝代的专家记录

    Args:
        conn: SQLite连接
        dynasty_name: 朝代名称（如'北宋'）
        min_year: 生年下限
        max_year: 生年上限
        limit: 最大记录数
        include_coords: 是否关联地理坐标

    Returns:
        list[dict]: 专家记录列表
    """
    cur = conn.cursor()

    # 获取朝代年份范围
    if dynasty_name in DYNASTY_YEARS:
        dyn_start, dyn_end = DYNASTY_YEARS[dynasty_name]
    else:
        dyn_start, dyn_end = None, None

    # 构建查询
    query = """
        SELECT DISTINCT
            b.c_personid,
            b.c_name_chn,
            b.c_name,
            b.c_surname_chn,
            b.c_mingzi_chn,
            b.c_birthyear,
            b.c_deathyear,
            b.c_dy,
            b.c_index_year,
            b.c_choronym_code
        FROM biog_main b
        WHERE 1=1
    """
    params = []

    # 朝代过滤（使用c_dy字段）
    if dynasty_name == '北宋':
        # 北宋: 生年960-1127
        query += " AND b.c_birthyear >= 960 AND b.c_birthyear <= 1127"
    elif dynasty_name == '南宋':
        query += " AND b.c_birthyear >= 1127 AND b.c_birthyear <= 1279"
    elif dynasty_name == '明朝':
        query += " AND b.c_birthyear >= 1368 AND b.c_birthyear <= 1644"
    elif dynasty_name == '唐朝':
        query += " AND b.c_birthyear >= 618 AND b.c_birthyear <= 907"

    # 额外年份过滤
    if min_year:
        query += " AND b.c_birthyear >= ?"
        params.append(min_year)
    if max_year:
        query += " AND b.c_birthyear <= ?"
        params.append(max_year)

    # 只取有生年的记录
    query += " AND b.c_birthyear > 0"

    # 排序和限制
    query += " ORDER BY b.c_birthyear"
    if limit:
        query += f" LIMIT {limit}"

    cur.execute(query, params)
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]

    experts = []
    for row in rows:
        record = dict(zip(col_names, row))
        # 字段标准化
        expert = {
            'person_id': record.get('c_personid'),
            'name_chn': record.get('c_name_chn') or '',
            'name_pinyin': record.get('c_name') or '',
            'surname_chn': record.get('c_surname_chn') or '',
            'mingzi_chn': record.get('c_mingzi_chn') or '',
            'birth_year': record.get('c_birthyear') or 0,
            'death_year': record.get('c_deathyear') or 0,
            'dynasty': record.get('c_dy') or dynasty_name,
            'index_year': record.get('c_index_year') or 0,
            'choronym_code': record.get('choronym_code') or '',
            'quality_tag': _estimate_quality_tag(record),
            '_source': 'cbdb',
        }
        experts.append(expert)

    return experts


def _estimate_quality_tag(record):
    """
    根据记录完整性估计数据质量标签

    A: 完整（有生卒年+姓名+籍贯）
    B: 良好（有生年+姓名）
    C: 一般（有生年或姓名之一）
    D: 缺失较多
    """
    score = 0
    by = record.get('c_birthyear')
    dy = record.get('c_deathyear')
    if by and by > 0:
        score += 2
    if dy and dy > 0:
        score += 2
    if record.get('c_name_chn'):
        score += 3
    if record.get('c_index_year', 0) and record.get('c_index_year', 0) > 0:
        score += 1
    if record.get('c_choronym_code'):
        score += 1

    if score >= 7:
        return 'A'
    elif score >= 4:
        return 'B'
    elif score >= 2:
        return 'C'
    else:
        return 'D'


def load_experts_with_coords(conn, dynasty_name, limit=None):
        """
        加载专家并关联地理坐标（通过BIOG_ADDR_DATA）

        CBDB dynasty codes:
          6 = 唐, 15 = 宋(需生年细分), 19 = 明, 20 = 清
        
        Returns:
            list[dict]: 含lat/lng的专家记录
        """
        cur = conn.cursor()

        # 映射朝代 → CBDB dynasty code
        dynasty_codes = {
            '北宋前期': {'dy': 15, 'by_min': 960, 'by_max': 1027},
            '北宋后期': {'dy': 15, 'by_min': 1028, 'by_max': 1127},
            '南宋': {'dy': 15, 'by_min': 1128, 'by_max': 1279},
            '明朝': {'dy': 19, 'by_min': 1368, 'by_max': 1644},
            '唐朝': {'dy': 6, 'by_min': 618, 'by_max': 907},
            '唐朝前期': {'dy': 6, 'by_min': 618, 'by_max': 755},
            '唐朝后期': {'dy': 6, 'by_min': 755, 'by_max': 907},
        }

        if dynasty_name not in dynasty_codes:
            print(f"[!] 未知朝代: {dynasty_name}，返回空列表")
            return []

        params = dynasty_codes[dynasty_name]
        dy_code = params['dy']
        by_min = params['by_min']
        by_max = params['by_max']

        # 联合查询：人物表 + 地址表
        # addr_codes 用 x_coord/y_coord（经纬度），CHGIS_PT_ID 关联CHGIS
        query = """
            SELECT DISTINCT
                b.c_personid,
                b.c_name_chn,
                b.c_birthyear,
                b.c_deathyear,
                addr.x_coord,
                addr.y_coord,
                addr.c_name_chn as placename,
                addr.c_addr_id
            FROM biog_main b
            LEFT JOIN biog_addr_data bad ON b.c_personid = bad.c_personid
            LEFT JOIN addr_codes addr ON bad.c_addr_id = addr.c_addr_id
            WHERE b.c_dy = ?
              AND b.c_birthyear >= ?
              AND b.c_birthyear <= ?
              AND b.c_birthyear > 0
        """
        # 排序优先有坐标的，再限制数量
        query += " ORDER BY CASE WHEN addr.x_coord IS NOT NULL THEN 0 ELSE 1 END, b.c_birthyear"
        if limit:
            query += f" LIMIT {limit}"

        cur.execute(query, (dy_code, by_min, by_max))
        rows = cur.fetchall()

        experts = []
        for row in rows:
            person_id, name_chn, birth, death, x, y, placename, addr_id = row
            if not name_chn:
                continue
            # 北宋/南宋标签
            if dynasty_name in ('北宋', '北宋后期') and birth and birth >= 1028:
                period_label = '北宋后期'
            else:
                period_label = dynasty_name
            
            expert = {
                'person_id': person_id,
                'name_chn': name_chn,
                'birth_year': birth or 0,
                'death_year': death or 0,
                'dynasty': period_label,
                'lat': float(y) if y else None,
                'lng': float(x) if x else None,  # CBDB x=经度, y=纬度
                'placename': placename or '',
                'addr_id': addr_id,
                'quality_tag': _estimate_quality_tag({
                    'c_birthyear': birth, 'c_deathyear': death,
                    'c_name_chn': name_chn, 'c_index_year': 0,
                    'c_choronym_code': ''
                }),
                '_source': 'cbdb',
            }
            experts.append(expert)

        return experts


def export_to_json(experts, output_path, metadata=None):
    """
    导出专家数据为JSON文件

    Args:
        experts: 专家记录列表
        output_path: 输出文件路径
        metadata: 附加元数据
    """
    output = {
        'meta': {
            'version': 'v2.5',
            'export_time': datetime.now().isoformat(),
            'n_records': len(experts),
            'data_source': 'CBDB',
            'quality_distribution': _count_quality_tags(experts),
        },
        'experts': experts,
    }
    if metadata:
        output['meta'].update(metadata)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"[✓] 导出 {len(experts)} 条记录 → {output_path}")
    return output


def _count_quality_tags(experts):
    """统计质量标签分布"""
    counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for e in experts:
        tag = e.get('quality_tag', 'D')
        if tag in counts:
            counts[tag] += 1
    return counts


def run_all_dynasties(conn, output_dir='data/experts'):
    """导出全部四个朝代的专家数据"""
    results = {}
    for dynasty in ['北宋前期', '北宋后期', '南宋', '明朝', '唐朝']:
        print(f"\n>>> 导出 {dynasty} ...")
        experts = load_experts_with_coords(conn, dynasty)
        output_path = f"{output_dir}/{dynasty}.json"
        result = export_to_json(experts, output_path, metadata={
            'dynasty': dynasty,
            'years': DYNASTY_YEARS.get(dynasty),
        })
        results[dynasty] = {
            'path': output_path,
            'n_records': len(experts),
            'quality_dist': result['meta']['quality_distribution'],
        }

    # 汇总报告
    print("\n" + "=" * 60)
    print("四朝专家导出汇总")
    print("=" * 60)
    print(f"{'朝代':<8} {'记录数':>6} {'A':>4} {'B':>4} {'C':>4} {'D':>4}")
    print("-" * 60)
    for dy, info in results.items():
        d = info['quality_dist']
        print(f"{dy:<8} {info['n_records']:>6} {d['A']:>4} {d['B']:>4} {d['C']:>4} {d['D']:>4}")

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CBDB导入工具 v2.5')
    parser.add_argument('--dynasty', type=str,
                        choices=['北宋前期', '北宋后期', '南宋', '明朝', '唐朝', 'all'],
                        default='all', help='指定朝代（默认all）')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--limit', type=int, help='最大记录数')
    parser.add_argument('--check', action='store_true', help='仅检查连接')
    parser.add_argument('--db-path', type=str, default='data/cbdb/cbdb.sqlite',
                        help='CBDB路径')
    args = parser.parse_args()

    conn = connect_cbdb(args.db_path)

    if args.check:
        inspect_cbdb(conn)
        conn.close()
        sys.exit(0)

    if args.dynasty == 'all':
        run_all_dynasties(conn)
    else:
        experts = load_experts_with_coords(conn, args.dynasty, limit=args.limit)
        output_path = args.output or f"data/experts/{args.dynasty}.json"
        export_to_json(experts, output_path, metadata={
            'dynasty': args.dynasty,
            'years': DYNASTY_YEARS.get(args.dynasty),
        })

    conn.close()