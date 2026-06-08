#!/usr/bin/env python3
"""
Civilization-Oracle 数据接入与部署脚本
========================================
作者：王滇让研究团队
版本：v2.3
日期：2026-05-27

功能：
1. CBDB SQLite 自动下载与验证
2. CTEXT API 集成测试
3. Neo4j 安装检查与降级说明
4. Redis 安装检查与降级说明

使用方式：
    python deploy_data.py --check        # 检查所有依赖
    python deploy_data.py --download-cbdb # 下载CBDB
    python deploy_data.py --test-ctext   # 测试CTEXT API
    python deploy_data.py --full         # 完整检查+下载
"""

import os
import sys
import json
import sqlite3
import subprocess
import urllib.request
import urllib.error
import requests
from pathlib import Path
from datetime import datetime

# ===== 配置 =====
REPO_DIR = Path("/Users/tianjangwang/Documents/历史事件预测建模")
DATA_DIR = REPO_DIR / "data"
CBDB_DIR = DATA_DIR / "cbdb"
REPORTS_DIR = Path.home() / ".civilization_oracle" / "reports"

CBDB_SQLITE_URL = "https://github.com/cbdb-project/cbdb_sqlite/raw/main/cbdb.sqlite"
CBDB_LOCAL = CBDB_DIR / "cbdb.sqlite"

CTEXT_API_BASE = "https://ctext.org/api/search/zh"
CTEXT_TEST_QUERIES = ["范仲淹", "王安石", "北宋", "澶渊之盟"]

NEO4J_INSTALL_URL = "https://neo4j.com/docs/neo4j-dashboard/latest/getting-started.html"
REDIS_INSTALL_URL = "https://redis.io/docs/getting-started/installation/"

LOG_FILE = REPORTS_DIR / "deploy_data_log.json"


def log(msg: str, level: str = "INFO"):
    """打印日志"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] [{level}] {msg}")


def save_log(data: dict):
    """保存日志到JSON文件"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  日志已保存：{LOG_FILE}")


def check_command(cmd: str) -> bool:
    """检查命令是否存在"""
    return subprocess.call(f"which {cmd} >/dev/null 2>&1", shell=True) == 0


def check_neo4j() -> dict:
    """检查Neo4j安装状态"""
    result = {
        "installed": False,
        "command": "neo4j",
        "version": None,
        "status": "未安装",
        "recommendation": "推荐安装（可选，使用内存图谱降级）"
    }

    if check_command("neo4j"):
        result["installed"] = True
        try:
            version = subprocess.check_output("neo4j --version 2>&1 | head -1", shell=True, text=True).strip()
            result["version"] = version
            result["status"] = "已安装"
        except subprocess.CalledProcessError:
            result["status"] = "已安装（无法获取版本）"
    else:
        # 检查是否通过其他方式安装
        for path in ["/Applications/Neo4j Desktop.app", "/usr/local/bin/neo4j"]:
            if os.path.exists(path):
                result["installed"] = True
                result["status"] = "Desktop版已安装"
                break

    return result


def check_redis() -> dict:
    """检查Redis安装状态"""
    result = {
        "installed": False,
        "command": "redis-server",
        "version": None,
        "status": "未安装",
        "recommendation": "可选，使用内存队列降级"
    }

    if check_command("redis-server"):
        result["installed"] = True
        try:
            version = subprocess.check_output("redis-server --version 2>&1 | head -1", shell=True, text=True).strip()
            result["version"] = version
            result["status"] = "已安装"
        except subprocess.CalledProcessError:
            result["status"] = "已安装（无法获取版本）"
    else:
        # 检查brew服务
        try:
            services = subprocess.check_output("brew services list 2>/dev/null | grep redis", shell=True, text=True)
            if "started" in services:
                result["installed"] = True
                result["status"] = "Homebrew服务运行中"
        except subprocess.CalledProcessError:
            pass

    return result


def check_cbdb() -> dict:
    """检查CBDB SQLite本地文件"""
    result = {
        "exists": False,
        "path": str(CBDB_LOCAL),
        "size": None,
        "tables": [],
        "record_count": 0,
        "status": "未下载"
    }

    if CBDB_LOCAL.exists():
        result["exists"] = True
        result["status"] = "已存在"
        result["size"] = CBDB_LOCAL.stat().st_size

        try:
            conn = sqlite3.connect(str(CBDB_LOCAL))
            cursor = conn.cursor()

            # 获取表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            result["tables"] = [row[0] for row in cursor.fetchall()]

            # 尝试获取记录数
            for table in ["PERSONS", "BIOG_MAIN", "biog_main"]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    result["record_count"] = cursor.fetchone()[0]
                    break
                except sqlite3.OperationalError:
                    continue

            conn.close()
            result["status"] = f"已下载（{result['record_count']}条记录）"
        except Exception as e:
            result["status"] = f"文件存在但无法读取：{e}"
    else:
        result["status"] = "未下载"

    return result


def check_ctext_api() -> dict:
    """测试CTEXT API连接"""
    result = {
        "accessible": False,
        "base_url": CTEXT_API_BASE,
        "test_queries": {},
        "status": "无法访问",
        "note": "CTEXT API需要人机验证，建议浏览器访问https://ctext.org/zh手动查询"
    }

    try:
        # 测试基础连通性（不使用API）
        response = requests.head("https://ctext.org/zh", timeout=10, allow_redirects=True)
        if response.status_code == 200:
            result["accessible"] = True
            result["status"] = "网站可访问（API需要人机验证）"
    except requests.exceptions.RequestException as e:
        result["status"] = f"网络错误：{type(e).__name__}"

    # 尝试API查询（可能触发验证码）
    for query in CTEXT_TEST_QUERIES:
        try:
            url = f"https://ctext.org/api/search/zh"
            encoded_query = requests.utils.quote(query)
            req = urllib.request.Request(f"{url}?search={encoded_query}&scope=all")
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                result["test_queries"][query] = {
                    "success": True,
                    "result_count": data.get("count", 0)
                }
        except json.JSONDecodeError:
            result["test_queries"][query] = {
                "success": False,
                "error": "验证码拦截（人机验证）"
            }
        except Exception as e:
            result["test_queries"][query] = {
                "success": False,
                "error": str(e)
            }

    return result


def download_cbdb() -> dict:
    """下载CBDB SQLite数据库"""
    result = {
        "success": False,
        "url": CBDB_SQLITE_URL,
        "path": str(CBDB_LOCAL),
        "size": None,
        "record_count": 0,
        "status": "失败"
    }

    CBDB_DIR.mkdir(parents=True, exist_ok=True)

    log("开始下载CBDB SQLite（可能需要几分钟）...", "INFO")

    try:
        # 使用curl下载（更稳定）
        cmd = f'curl -L -o "{CBDB_LOCAL}" "{CBDB_SQLITE_URL}" 2>&1'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=300)  # 5分钟超时

        if process.returncode == 0 and CBDB_LOCAL.exists():
            result["success"] = True
            result["size"] = CBDB_LOCAL.stat().st_size
            result["status"] = f"下载完成（{result['size'] / 1024 / 1024:.1f} MB）"

            # 验证数据库
            try:
                conn = sqlite3.connect(str(CBDB_LOCAL))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                result["tables"] = tables

                # 获取记录数
                for table in ["PERSONS", "BIOG_MAIN", "biog_main"]:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        result["record_count"] = cursor.fetchone()[0]
                        break
                    except sqlite3.OperationalError:
                        continue

                conn.close()
                result["status"] = f"下载并验证成功（{result['record_count']}条记录）"
            except Exception as e:
                result["status"] = f"下载成功但验证失败：{e}"
        else:
            result["status"] = f"下载失败：{stderr.decode('utf-8', errors='replace')[:200]}"

    except subprocess.TimeoutExpired:
        result["status"] = "下载超时（>5分钟）"
    except Exception as e:
        result["status"] = f"错误：{e}"

    return result


def install_neo4j_guide():
    """打印Neo4j安装指南"""
    guide = """
╔══════════════════════════════════════════════════════════════╗
║  Neo4j 安装指南                                                ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  方式一：Neo4j Desktop（推荐个人/笔记本）                       ║
║  ─────────────────────────────────────────────────────        ║
║  1. 访问：https://neo4j.com/download/                         ║
║  2. 下载 Neo4j Desktop（约300MB）                             ║
║  3. 安装后启动，首次会要求创建项目                             ║
║  4. 建议：分配至少4GB内存给Neo4j                              ║
║                                                               ║
║  方式二：Homebrew（macOS Terminal）                            ║
║  ─────────────────────────────────────────────────────        ║
║  $ brew install neo4j                                          ║
║  $ neo4j start                                                ║
║  默认端口：7474（HTTP），7687（Bolt）                          ║
║  默认账号：neo4j / neo4j（首次登录需修改）                      ║
║                                                               ║
║  ⚠️  注意：Civilization-Oracle无需Neo4j即可运行               ║
║     phase5_kgraph.py使用内存图谱降级（内嵌示例数据）            ║
║     安装Neo4j仅用于生产环境大规模图谱存储                       ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(guide)


def install_redis_guide():
    """打印Redis安装指南"""
    guide = """
╔══════════════════════════════════════════════════════════════╗
║  Redis 安装指南                                                ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  方式一：Homebrew（macOS Terminal）                            ║
║  ─────────────────────────────────────────────────────        ║
║  $ brew install redis                                         ║
║  $ brew services start redis                                  ║
║  $ redis-cli ping                                             ║
║  应返回：PONG                                                  ║
║                                                               ║
║  方式二：Docker（跨平台）                                      ║
║  ─────────────────────────────────────────────────────        ║
║  $ docker run -d -p 6379:6379 redis:latest                   ║
║                                                               ║
║  ⚠️  注意：Civilization-Oracle无需Redis即可运行               ║
║     phase4_master.py使用内存队列降级                           ║
║     安装Redis仅用于多进程/分布式部署                           ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(guide)


def check_all():
    """完整依赖检查"""
    log("检查所有依赖项...", "INFO")
    print()

    # Neo4j
    neo4j = check_neo4j()
    status_icon = "✅" if neo4j["installed"] else "⚪"
    print(f"{status_icon} Neo4j: {neo4j['status']}")
    if not neo4j["installed"]:
        print(f"   → {neo4j['recommendation']}")

    # Redis
    redis = check_redis()
    status_icon = "✅" if redis["installed"] else "⚪"
    print(f"{status_icon} Redis: {redis['status']}")
    if not redis["installed"]:
        print(f"   → {redis['recommendation']}")

    # CBDB
    cbdb = check_cbdb()
    status_icon = "✅" if cbdb["record_count"] > 0 else "⚪"
    print(f"{status_icon} CBDB: {cbdb['status']}")
    if cbdb["record_count"] > 0:
        print(f"   → 包含{cbdb['record_count']}条记录，{len(cbdb['tables'])}个表")

    # CTEXT
    print()
    log("测试CTEXT API连接（可能需要几秒）...", "INFO")
    ctext = check_ctext_api()
    status_icon = "✅" if ctext["accessible"] else "❌"
    print(f"{status_icon} CTEXT: {ctext['status']}")
    if ctext["test_queries"]:
        for query, result in ctext["test_queries"].items():
            if result.get("success"):
                print(f"   → '{query}': 找到{result['result_count']}条结果")
            else:
                print(f"   → '{query}': {result.get('error', '未知错误')}")

    print()
    print("=" * 60)
    print("依赖检查汇总")
    print("=" * 60)

    can_run_pipeline = cbdb["record_count"] > 0 or ctext["accessible"]
    print(f"当前系统可运行端到端Pipeline: {'✅ 是' if can_run_pipeline else '⚪ 部分可运行（使用模拟数据）'}")
    print(f"  - CBDB数据: {'✅' if cbdb['record_count'] > 0 else '⚪ 使用模拟数据'}")
    print(f"  - CTEXT数据: {'✅' if ctext['accessible'] else '⚪ 使用模拟语料'}")
    print(f"  - Neo4j图谱: {'✅' if neo4j['installed'] else '⚪ 使用内存图谱'}")
    print(f"  - Redis队列: {'✅' if redis['installed'] else '⚪ 使用内存队列'}")
    print("=" * 60)

    return {
        "neo4j": neo4j,
        "redis": redis,
        "cbdb": cbdb,
        "ctext": ctext,
        "can_run_pipeline": can_run_pipeline
    }


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Civilization-Oracle 数据接入与部署脚本                         ║
║  版本：v2.3  |  日期：2026-05-27                               ║
╚══════════════════════════════════════════════════════════════╝
""")

    if len(sys.argv) < 2:
        print("用法：")
        print("  python deploy_data.py --check        # 检查所有依赖")
        print("  python deploy_data.py --download-cbdb # 下载CBDB SQLite")
        print("  python deploy_data.py --test-ctext   # 测试CTEXT API")
        print("  python deploy_data.py --install-neo4j # Neo4j安装指南")
        print("  python deploy_data.py --install-redis # Redis安装指南")
        print("  python deploy_data.py --full         # 完整检查+下载")
        print()
        sys.exit(1)

    command = sys.argv[1]

    if command == "--check":
        result = check_all()
        save_log({"command": "check", "timestamp": datetime.now().isoformat(), "result": result})

    elif command == "--download-cbdb":
        result = download_cbdb()
        status = "✅" if result["success"] else "❌"
        log(f"CBDB下载{result['status']}", "INFO" if result["success"] else "ERROR")
        if result["record_count"] > 0:
            log(f"共{result['record_count']}条记录", "INFO")
        save_log({"command": "download-cbdb", "timestamp": datetime.now().isoformat(), "result": result})

    elif command == "--test-ctext":
        result = check_ctext_api()
        status = "✅" if result["accessible"] else "❌"
        log(f"CTEXT API: {result['status']}", "INFO" if result["accessible"] else "ERROR")
        save_log({"command": "test-ctext", "timestamp": datetime.now().isoformat(), "result": result})

    elif command == "--install-neo4j":
        install_neo4j_guide()

    elif command == "--install-redis":
        install_redis_guide()

    elif command == "--full":
        log("执行完整检查+下载...", "INFO")
        print()

        # 检查
        check_result = check_all()

        print()
        if not check_result["cbdb"]["exists"]:
            log("开始下载CBDB...", "INFO")
            dl_result = download_cbdb()
            log(f"CBDB下载: {dl_result['status']}", "INFO" if dl_result["success"] else "ERROR")

        save_log({
            "command": "full",
            "timestamp": datetime.now().isoformat(),
            "check_result": check_result
        })

    else:
        log(f"未知命令: {command}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()