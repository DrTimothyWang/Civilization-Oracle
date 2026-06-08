#!/usr/bin/env python3
"""
Civilization-Oracle CBDB数据下载脚本
======================================
功能：
1. 从GitHub下载CBDB SQLite数据库
2. 验证数据完整性
3. 提取北宋专家数据（用于PSI验证）

使用方式：
    python cbdb_download.py --check     # 检查本地CBDB
    python cbdb_download.py --download # 下载CBDB（约200MB）
    python cbdb_download.py --extract  # 提取北宋专家数据
    python cbdb_download.py --full     # 完整流程
"""

import os
import sys
import json
import sqlite3
import subprocess
import requests
import zipfile
from pathlib import Path
from datetime import datetime

# ===== 配置 =====
CBDB_SQLITE_URL = "https://huggingface.co/datasets/cbdb/cbdb-sqlite/resolve/main/latest.zip"
CBDB_LOCAL = Path("/Users/tianjangwang/Documents/历史事件预测建模/data/cbdb/cbdb.sqlite")
CBDB_DIR = CBDB_LOCAL.parent

REPORTS_DIR = Path.home() / ".civilization_oracle" / "reports"


def log(msg: str, level: str = "INFO"):
    """打印日志"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [{level}] {msg}")


def check_local() -> dict:
    """检查本地CBDB"""
    result = {
        "exists": False,
        "path": str(CBDB_LOCAL),
        "size_mb": 0,
        "tables": [],
        "record_count": 0,
        "north_song_experts": 0,
        "status": "未下载"
    }

    if not CBDB_LOCAL.exists():
        log("CBDB未下载", "WARNING")
        return result

    result["exists"] = True
    result["size_mb"] = CBDB_LOCAL.stat().st_size / 1024 / 1024
    result["status"] = f"本地存在（{result['size_mb']:.1f} MB）"

    try:
        conn = sqlite3.connect(str(CBDB_LOCAL))
        cursor = conn.cursor()

        # 获取表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        result["tables"] = [row[0] for row in cursor.fetchall()]

        # 获取记录数（尝试多个可能的表名）
        for table in ["PERSONS", "BIOG_MAIN", "biog_main", "Person"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                result["record_count"] = cursor.fetchone()[0]
                break
            except sqlite3.OperationalError:
                continue

        # 提取北宋专家（生卒年在960-1127年之间）
        try:
            # 尝试查询生卒年
            for year_col in ["c_birth", "birth_year", "byear"]:
                for death_col in ["c_death", "death_year", "dyear"]:
                    try:
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM PERSONS
                            WHERE {year_col} >= 960 AND {year_col} <= 1127
                        """)
                        result["north_song_experts"] = cursor.fetchone()[0]
                        break
                    except sqlite3.OperationalError:
                        continue
        except Exception as e:
            log(f"北宋专家提取失败：{e}", "WARNING")

        conn.close()
        result["status"] = f"验证成功（{result['record_count']}条总记录，{result['north_song_experts']}条北宋）"

    except Exception as e:
        result["status"] = f"文件存在但无法读取：{e}"

    return result


def download_cbdb() -> dict:
    """下载CBDB SQLite（从Hugging Face）"""
    result = {
        "success": False,
        "url": CBDB_SQLITE_URL,
        "size_mb": 0,
        "record_count": 0,
        "tables": [],
        "status": "失败"
    }

    CBDB_DIR.mkdir(parents=True, exist_ok=True)
    zip_file = CBDB_DIR / "latest.zip"

    log("开始下载CBDB SQLite（约200MB，可能需要几分钟）...", "INFO")
    log(f"下载地址：{CBDB_SQLITE_URL}", "INFO")

    try:
        # 下载zip文件
        response = requests.get(CBDB_SQLITE_URL, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        log(f"ZIP文件大小：{total_size / 1024 / 1024:.1f} MB", "INFO")

        downloaded = 0
        with open(zip_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        if downloaded % (5 * 1024 * 1024) < 8192:
                            print(f"\r  下载进度：{percent:.1f}%", end="", flush=True)

        print()

        # 解压zip
        log("解压CBDB数据库...", "INFO")
        with zipfile.ZipFile(zip_file, 'r') as zf:
            # 获取sqlite文件（可能是.sqlite3或.sqlite）
            db_files = [f for f in zf.namelist() if '.sqlite' in f]
            if db_files:
                # 解压到目标位置
                zf.extractall(str(CBDB_DIR))
                extracted = CBDB_DIR / db_files[0]
                log(f"解压文件：{db_files[0]}（{extracted.stat().st_size / 1024 / 1024:.1f} MB）", "INFO")

                # 重命名为标准名称
                if extracted.exists() and str(extracted) != str(CBDB_LOCAL):
                    extracted.rename(CBDB_LOCAL)
                    log(f"重命名为：{CBDB_LOCAL}", "INFO")

                # 删除zip
                zip_file.unlink()
            else:
                log(f"未找到sqlite文件，zip内容：{zf.namelist()}", "WARNING")

        # 验证数据库
        if CBDB_LOCAL.exists():
            result["success"] = True
            result["size_mb"] = CBDB_LOCAL.stat().st_size / 1024 / 1024
            result["status"] = f"下载并解压成功（{result['size_mb']:.1f} MB）"

            log("验证数据库...", "INFO")
            conn = sqlite3.connect(str(CBDB_LOCAL))
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            result["tables"] = [row[0] for row in cursor.fetchall()]
            log(f"  表：{result['tables']}", "INFO")

            for table in ["PERSONS", "BIOG_MAIN", "biog_main"]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    result["record_count"] = cursor.fetchone()[0]
                    log(f"  记录数：{result['record_count']}", "INFO")
                    break
                except sqlite3.OperationalError:
                    continue

            conn.close()
        else:
            result["status"] = "解压失败：未找到数据库文件"

    except requests.exceptions.RequestException as e:
        result["status"] = f"下载失败：{e}"
    except Exception as e:
        result["status"] = f"错误：{e}"

    return result


def extract_north_song() -> dict:
    """提取北宋专家数据"""
    result = {
        "success": False,
        "expert_count": 0,
        "output_file": None,
        "status": "失败"
    }

    if not CBDB_LOCAL.exists():
        result["status"] = "CBDB未下载"
        return result

    try:
        conn = sqlite3.connect(str(CBDB_LOCAL))
        cursor = conn.cursor()

        # 获取表结构
        cursor.execute("PRAGMA table_info(PERSONS)")
        columns = [row[1] for row in cursor.fetchall()]

        log(f"CBDB表结构字段：{columns}", "INFO")

        # 提取北宋专家（根据实际表结构调整）
        query = """
            SELECT c_personid, c_name, c_birth, c_death, c_byear, c_dyear, c_addr, c_occ
            FROM PERSONS
            WHERE (c_birth >= 960 AND c_birth <= 1127)
               OR (c_byear >= 960 AND c_byear <= 1127)
               OR (c_death >= 960 AND c_death <= 1127)
               OR (c_dyear >= 960 AND c_dyear <= 1127)
        """

        cursor.execute(query)
        experts = cursor.fetchall()

        result["expert_count"] = len(experts)
        result["status"] = f"提取{result['expert_count']}条北宋专家记录"

        # 导出为JSON
        output_dir = REPORTS_DIR / "north_song"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "north_song_experts.json"
        experts_data = []

        for row in experts:
            experts_data.append({
                "person_id": row[0],
                "name": row[1],
                "birth": row[2],
                "death": row[3],
                "birth_year": row[4],
                "death_year": row[5],
                "address": row[6],
                "occupation": row[7]
            })

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(experts_data, f, ensure_ascii=False, indent=2)

        result["output_file"] = str(output_file)
        result["success"] = True

        conn.close()

    except Exception as e:
        result["status"] = f"错误：{e}"

    return result


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Civilization-Oracle CBDB数据下载脚本                          ║
║  版本：v2.3  |  日期：2026-05-27                               ║
╚══════════════════════════════════════════════════════════════╝
""")

    if len(sys.argv) < 2:
        print("用法：")
        print("  python cbdb_download.py --check     # 检查本地CBDB")
        print("  python cbdb_download.py --download  # 下载CBDB SQLite")
        print("  python cbdb_download.py --extract   # 提取北宋专家数据")
        print("  python cbdb_download.py --full      # 完整流程")
        print()
        sys.exit(1)

    command = sys.argv[1]

    if command == "--check":
        result = check_local()
        status_icon = "✅" if result["record_count"] > 0 else "⚪"
        log(f"CBDB状态：{result['status']}", "INFO")

    elif command == "--download":
        result = download_cbdb()
        status = "✅" if result["success"] else "❌"
        log(f"下载{result['status']}", "INFO" if result["success"] else "ERROR")

    elif command == "--extract":
        result = extract_north_song()
        status = "✅" if result["success"] else "❌"
        log(f"提取{result['status']}", "INFO" if result["success"] else "ERROR")
        if result["output_file"]:
            log(f"输出文件：{result['output_file']}", "INFO")

    elif command == "--full":
        log("执行完整流程：检查 → 下载 → 验证 → 提取", "INFO")
        print()

        # 检查
        check = check_local()
        if check["record_count"] > 0:
            log(f"CBDB已存在：{check['record_count']}条记录", "INFO")
        else:
            # 下载
            dl = download_cbdb()
            log(f"下载{ dl['status']}", "INFO" if dl["success"] else "ERROR")

        # 提取
        ext = extract_north_song()
        log(f"提取{ext['status']}", "INFO" if ext["success"] else "ERROR")

    else:
        log(f"未知命令：{command}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()