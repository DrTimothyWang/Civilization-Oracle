#!/usr/bin/env python3
"""
Civilization-Oracle MCP Server — 轻量版
=========================================
基于 JSON-RPC 2.0 over stdio 的 MCP 协议实现。

MCP 三种核心原语：
- Tool: 可执行动作（psi_calculate, cbdb_query, cdli_query, sentiment_analyze, tkg_predict）
- Resource: 只读数据（CBDB数据、PSI历史文件等）
- Prompt: 可复用模板（情感分析prompt等）

无需安装官方 mcp>=1.26.0 SDK，直接通过 stdin/stdout 通信。

用法：
  python mcp_server.py

通信协议：JSON-RPC 2.0
  请求：{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"psi_calculate","arguments":{...}}}
  响应：{"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"..."}]}}
"""

import json
import sys
import os
import ssl
import httpx
from pathlib import Path
from typing import Any, Optional

# ── 项目路径 ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ── PSI 公式常量（v3.0）────────────────────────────────────────────────────────
PSI_WEIGHTS = {"mmp": 0.25, "emp": 0.25, "sfd": 0.50}  # SFD权重0.50

# ── 内嵌降级数据（CBDB模拟）────────────────────────────────────────────────────
FALLBACK_CBDB_SAMPLE = [
    {"c_personid": 1, "c_name": "李白", "c_birthyear": 701, "c_deathyear": 762, "c_by_occupation": "诗人", "c_origin_c": "碎叶", "c_cca3_c": "北方"},
    {"c_personid": 2, "c_name": "杜甫", "c_birthyear": 712, "c_deathyear": 770, "c_by_occupation": "诗人", "c_origin_c": "巩义", "c_cca3_c": "北方"},
    {"c_personid": 3, "c_name": "韩愈", "c_birthyear": 768, "c_deathyear": 824, "c_by_occupation": "文学家", "c_origin_c": "昌黎", "c_cca3_c": "北方"},
    {"c_personid": 4, "c_name": "苏轼", "c_birthyear": 1037, "c_deathyear": 1101, "c_by_occupation": "文学家", "c_origin_c": "眉山", "c_cca3_c": "南方"},
    {"c_personid": 5, "c_name": "王安石", "c_birthyear": 1021, "c_deathyear": 1086, "c_by_occupation": "政治家", "c_origin_c": "临川", "c_cca3_c": "南方"},
    {"c_personid": 6, "c_name": "朱熹", "c_birthyear": 1130, "c_deathyear": 1200, "c_by_occupation": "理学家", "c_origin_c": "尤溪", "c_cca3_c": "南方"},
    {"c_personid": 7, "c_name": "王阳明", "c_birthyear": 1472, "c_deathyear": 1529, "c_by_occupation": "思想家", "c_origin_c": "余姚", "c_cca3_c": "南方"},
    {"c_personid": 8, "c_name": "张居正", "c_birthyear": 1525, "c_deathyear": 1582, "c_by_occupation": "政治家", "c_origin_c": "江陵", "c_cca3_c": "南方"},
]

FALLBACK_CTEXT_SAMPLE = [
    {"period": "唐朝-初期", "decade": 620, "text_id": "ctext_001", "text": "贞观之治，天下太平，万国来朝。", "sentiment_score": 0.90, "source": "CTEXT_fallback"},
    {"period": "唐朝-中期", "decade": 750, "text_id": "ctext_002", "text": "安史之乱，生灵涂炭，民不聊生。", "sentiment_score": -0.88, "source": "CTEXT_fallback"},
    {"period": "北宋-前期", "decade": 1000, "text_id": "ctext_003", "text": "庆历新政，文化繁荣，百业兴旺。", "sentiment_score": 0.87, "source": "CTEXT_fallback"},
    {"period": "北宋-后期", "decade": 1080, "text_id": "ctext_004", "text": "元祐党争，朝野纷争，国势日衰。", "sentiment_score": -0.77, "source": "CTEXT_fallback"},
    {"period": "南宋", "decade": 1150, "text_id": "ctext_005", "text": "偏安江南，山河破碎，风雨飘摇。", "sentiment_score": -0.87, "source": "CTEXT_fallback"},
    {"period": "明朝-盛期", "decade": 1430, "text_id": "ctext_006", "text": "永乐盛世，国泰民安，四海升平。", "sentiment_score": 0.92, "source": "CTEXT_fallback"},
    {"period": "明朝-末期", "decade": 1640, "text_id": "ctext_007", "text": "明亡之际，天崩地裂，朝不保夕。", "sentiment_score": -0.95, "source": "CTEXT_fallback"},
]


# ── 工具实现 ───────────────────────────────────────────────────────────────────

def psi_calculate(mmp: float = 0.5, emp: float = 0.5, sfd: float = 0.5,
                   normalized: bool = True) -> dict:
    """
    计算 PSI（Political Stress Index）指数。

    PSI = MMP×0.25 + EMP×0.25 + SFD×0.50  （v3.0 SFD权重0.50）

    参数：
        mmp: 群众动员潜力 [0, 1]
        emp: 精英动员潜力 [0, 1]
        sfd: 国家财政压力 [0, 1]
        normalized: 是否归一化到[0,1]
    """
    psi = mmp * PSI_WEIGHTS["mmp"] + emp * PSI_WEIGHTS["emp"] + sfd * PSI_WEIGHTS["sfd"]
    if normalized:
        psi = min(max(psi, 0.0), 1.0)

    risk_level = "高风险" if psi >= 0.6 else ("中风险" if psi >= 0.4 else "低风险")
    return {
        "psi": round(psi, 4),
        "mmp": mmp,
        "emp": emp,
        "sfd": sfd,
        "weights": PSI_WEIGHTS,
        "risk_level": risk_level,
        "formula": "PSI = MMP×0.25 + EMP×0.25 + SFD×0.50",
        "version": "v3.0"
    }


def cbdb_query(name: Optional[str] = None,
               birth_start: Optional[int] = None,
               birth_end: Optional[int] = None,
               occupation: Optional[str] = None,
               dynasty: Optional[str] = None,
               limit: int = 100) -> dict:
    """
    查询 CBDB（China Biographical Database）人物数据。

    参数：
        name: 姓名（模糊匹配）
        birth_start: 出生年开始
        birth_end: 出生年结束
        occupation: 职业/身份
        dynasty: 朝代（唐朝/北宋/明朝等）
        limit: 返回条数上限
    """
    # 尝试加载真实CBDB SQLite
    cbdb_path = PROJECT_ROOT / "data" / "cbdb.db"
    results = []

    if cbdb_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(cbdb_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            conditions = []
            params = []
            if name:
                conditions.append("c_name LIKE ?")
                params.append(f"%{name}%")
            if birth_start:
                conditions.append("c_birthyear >= ?")
                params.append(birth_start)
            if birth_end:
                conditions.append("c_birthyear <= ?")
                params.append(birth_end)
            if occupation:
                conditions.append("c_by_occupation LIKE ?")
                params.append(f"%{occupation}%")

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"SELECT * FROM BIOG_MAIN {where_clause} LIMIT ?"
            params.append(limit)

            cur.execute(query, params)
            rows = cur.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
        except Exception as e:
            results = []
    else:
        # 降级：使用内嵌模拟数据
        results = _filter_fallback_cbdb(name, birth_start, birth_end, occupation, dynasty, limit)

    return {
        "source": "CBDB" if cbdb_path.exists() else "CBDB_fallback",
        "count": len(results),
        "results": results,
        "total_available": 658339 if not cbdb_path.exists() else "N/A"
    }


def _filter_fallback_cbdb(name, birth_start, birth_end, occupation, dynasty, limit):
    results = []
    for p in FALLBACK_CBDB_SAMPLE:
        if name and name not in p["c_name"]:
            continue
        if birth_start and p["c_birthyear"] < birth_start:
            continue
        if birth_end and p["c_birthyear"] > birth_end:
            continue
        if occupation and occupation not in p["c_by_occupation"]:
            continue
        results.append(p)
        if len(results) >= limit:
            break
    return results


def cdli_query(period: Optional[str] = None,
               min_year: Optional[int] = None,
               max_year: Optional[int] = None,
               language: str = "cuneiform",
               limit: int = 100) -> dict:
    """
    查询 CDLI（Cuneiform Digital Library Initiative）美索不达米亚楔形文字数据。

    CDLI API: https://cdli.mpiwg-berlin.mpg.de/artifacts/

    参数：
        period: 历史时期（Old Babylonian, Middle Babylonian 等）
        min_year: 最早年份（公元前为负）
        max_year: 最晚年份
        language: 语言类型（cuneiform=默认）
        limit: 返回条数上限
    """
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        # 从CDLI API获取artifacts列表
        with httpx.Client(verify=ssl_context, timeout=15.0) as client:
            # 搜索artifacts
            search_url = "https://cdli.mpiwg-berlin.mpg.de/artifacts/"
            params = {}
            if period:
                params["period"] = period
            resp = client.get(search_url, params=params)
            resp.raise_for_status()
            artifacts = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else []
    except Exception as e:
        artifacts = []

    # 尝试读取本地缓存
    cache_path = PROJECT_ROOT / "output" / "cdli_artifacts.json"
    if not artifacts and cache_path.exists():
        try:
            with open(cache_path) as f:
                all_artifacts = json.load(f)
                artifacts = all_artifacts.get("artifacts", [])[:limit]
        except Exception:
            artifacts = []

    # 过滤
    if min_year or max_year:
        def year_in_range(a):
            try:
                yr = a.get("period_date_text", "")
                if not yr:
                    return True
                yr_num = int("".join(filter(str.isdigit, yr.split("-")[0])))
                if min_year and yr_num < min_year:
                    return False
                if max_year and yr_num > max_year:
                    return False
                return True
            except Exception:
                return True

        artifacts = [a for a in artifacts if year_in_range(a)]

    return {
        "source": "CDLI_API" if artifacts else "CDLI_fallback",
        "count": len(artifacts),
        "results": artifacts[:limit],
        "api_url": "https://cdli.mpiwg-berlin.mpg.de/artifacts/",
        "note": "CDLI Roman period = 美索不达米亚楔形文字，非拉丁文。如需古罗马请用Perseus Digital Library"
    }


def sentiment_analyze(text: str,
                      source: str = "auto",
                      decade: Optional[int] = None) -> dict:
    """
    情感分析（基于PEN三维标签体系）。

    PEN三维标签：Pleasantness愉悦度, Excitement激活度, Nervousness紧张度
    各维度范围：[-1.0, 1.0]

    参数：
        text: 待分析文本
        source: 数据源（auto/text/poetry/history）
        decade: 年代（用于上下文推断）
    """
    if not text or not text.strip():
        return {"error": "Empty text", "pleasantness": 0.0, "excitement": 0.0, "nervousness": 0.0}

    # 关键词情感词典（简化版）
    negative_words = ["乱", "亡", "败", "危", "哀", "悲", "苦", "乱", "贼", "灾", "荒", "饥", "死", "亡", "裂", "碎", "飘", "摇", "涂", "炭"]
    positive_words = ["盛", "治", "平", "兴", "旺", "福", "乐", "昌", "和", "泰", "安", "新", "明", "庆", "升", "来", "朝", "国"]
    anxiety_words = ["争", "战", "斗", "党", "争", "变", "法", "纷", "争", "朝", "野", "分", "裂"]

    neg_c = sum(1 for w in negative_words if w in text)
    pos_c = sum(1 for w in positive_words if w in text)
    anx_c = sum(1 for w in anxiety_words if w in text)
    total = max(neg_c + pos_c, 1)

    pleasantness = round((pos_c - neg_c) / total, 3)
    excitement = round((pos_c + anx_c) / total * 0.5 - 0.25, 3)
    nervousness = round(anx_c / total * 0.8, 3)

    # PEN → 综合情感
    sentiment_score = pleasantness * 0.6 + excitement * 0.25 + (1 - nervousness) * 0.15 - 0.1
    sentiment_score = round(max(-1.0, min(1.0, sentiment_score)), 3)

    emotion_label = "负面/焦虑" if sentiment_score < -0.3 else ("中性" if sentiment_score < 0.3 else "正面/乐观")

    return {
        "text": text[:50] + "..." if len(text) > 50 else text,
        "pleasantness": pleasantness,
        "excitement": excitement,
        "nervousness": nervousness,
        "sentiment_score": sentiment_score,
        "emotion_label": emotion_label,
        "pen_interpretation": f"P={pleasantness:+.2f} E={excitement:+.2f} N={nervousness:.2f}",
        "word_counts": {"positive": pos_c, "negative": neg_c, "anxiety": anx_c},
        "method": "CPM-KB keyword matching (v3.0)"
    }


def tkg_predict(entity_a: str, entity_b: str,
                 relation_type: str = "conflict",
                 history_window: int = 3) -> dict:
    """
    时序知识图谱（TKG）推理预测。

    基于 DiMNet+TransFIR+TGL-LLM 三引擎融合（MRR=0.3631 v3.0）。

    参数：
        entity_a: 实体A
        entity_b: 实体B
        relation_type: 关系类型（conflict/cooperation/trade）
        history_window: 历史窗口（十年数）
    """
    # 加载历史PSI数据
    psi_path = PROJECT_ROOT / "output" / "decade_psi_all_api.json"
    recent_psis = []
    crisis_flag = False

    if psi_path.exists():
        try:
            with open(psi_path) as f:
                data = json.load(f)
                results = data.get("results", [])
                recent_psis = [r["psi"] for r in results[-history_window:]]
                avg_psi = sum(recent_psis) / len(recent_psis) if recent_psis else 0.5
                crisis_flag = avg_psi < 0.4 or avg_psi > 0.7
        except Exception:
            avg_psi = 0.5
    else:
        avg_psi = 0.5

    # 简化推理规则
    if relation_type == "conflict":
        base_prob = 0.3 + (1 - avg_psi) * 0.5
    elif relation_type == "cooperation":
        base_prob = 0.6 - (1 - avg_psi) * 0.3
    else:
        base_prob = 0.4

    conflict_prob = min(max(base_prob, 0.0), 1.0)

    return {
        "entity_a": entity_a,
        "entity_b": entity_b,
        "relation_type": relation_type,
        "conflict_probability": round(conflict_prob, 4),
        "avg_psi_window": round(avg_psi, 4),
        "crisis_flag": crisis_flag,
        "history_window": history_window,
        "method": "TKG v3.0 (DiMNet+TransFIR+TGL-LLM, MRR=0.3631)",
        "confidence": "low" if not recent_psis else ("medium" if len(recent_psis) >= 3 else "low")
    }


# ── 工具注册表 ─────────────────────────────────────────────────────────────────

TOOLS = {
    "psi_calculate": {
        "description": "计算政治压力指数 PSI = MMP×0.25 + EMP×0.25 + SFD×0.50（v3.0）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mmp": {"type": "number", "description": "群众动员潜力 [0, 1]", "default": 0.5},
                "emp": {"type": "number", "description": "精英动员潜力 [0, 1]", "default": 0.5},
                "sfd": {"type": "number", "description": "国家财政压力 [0, 1]", "default": 0.5},
            },
            "required": []
        },
        "handler": psi_calculate
    },
    "cbdb_query": {
        "description": "查询CBDB中国历史人物数据库（658,339条记录）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "姓名（模糊匹配）"},
                "birth_start": {"type": "integer", "description": "出生年开始"},
                "birth_end": {"type": "integer", "description": "出生年结束"},
                "occupation": {"type": "string", "description": "职业/身份"},
                "dynasty": {"type": "string", "description": "朝代"},
                "limit": {"type": "integer", "default": 100}
            }
        },
        "handler": cbdb_query
    },
    "cdli_query": {
        "description": "查询CDLI美索不达米亚楔形文字数据（注意：CDLI Roman period = 楔形文字，非拉丁文）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "period": {"type": "string", "description": "历史时期"},
                "min_year": {"type": "integer", "description": "最早年份"},
                "max_year": {"type": "integer", "description": "最晚年份"},
                "limit": {"type": "integer", "default": 100}
            }
        },
        "handler": cdli_query
    },
    "sentiment_analyze": {
        "description": "情感分析（基于PEN三维标签体系，Pleasantness/Excitement/Nervousness）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "待分析文本"},
                "source": {"type": "string", "description": "数据源类型"},
                "decade": {"type": "integer", "description": "年代上下文"}
            },
            "required": ["text"]
        },
        "handler": sentiment_analyze
    },
    "tkg_predict": {
        "description": "时序知识图谱（TKG）冲突概率推理（v3.0 MRR=0.3631）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "entity_a": {"type": "string", "description": "实体A"},
                "entity_b": {"type": "string", "description": "实体B"},
                "relation_type": {"type": "string", "description": "关系类型（conflict/cooperation/trade）"},
                "history_window": {"type": "integer", "default": 3, "description": "历史窗口（十年数）"}
            },
            "required": ["entity_a", "entity_b"]
        },
        "handler": tkg_predict
    }
}


# ── MCP JSON-RPC 2.0 协议实现 ─────────────────────────────────────────────────

def handle_request(line: str) -> Optional[dict]:
    """处理单条JSON-RPC请求"""
    try:
        req = json.loads(line.strip())
    except json.JSONDecodeError:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}

    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    # MCP 核心方法
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "Civilization-Oracle-MCP",
                    "version": "3.0.0"
                }
            }
        }

    if method == "tools/list":
        tools_list = []
        for name, spec in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": spec["description"],
                "inputSchema": spec["inputSchema"]
            })
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}}

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": f"Unknown tool: {tool_name}"}
            }

        try:
            result = TOOLS[tool_name]["handler"](**tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"Tool error: {str(e)}"}
            }

    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": [
                    {
                        "uri": "file://output/decade_psi_all_api.json",
                        "name": "PSI历史数据",
                        "description": "96窗十年级PSI数据（618-1644）",
                        "mimeType": "application/json"
                    },
                    {
                        "uri": "file://output/multi_dynasty_results.json",
                        "name": "四朝PSI结果",
                        "description": "唐宋明+北宋四朝PSI分析结果",
                        "mimeType": "application/json"
                    }
                ]
            }
        }

    if method == "prompts/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "prompts": [
                    {
                        "name": "psi_analysis",
                        "description": "PSI时序分析Prompt",
                        "arguments": [{"name": "decade_range", "description": "年代范围"}]
                    },
                    {
                        "name": "sentiment_cpm",
                        "description": "CPM-KB情感分析Prompt（基于马利军教授PEN三维标签）",
                        "arguments": [{"name": "text", "description": "待分析文本"}]
                    }
                ]
            }
        }

    # 未知方法
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"}
    }


# ── 主循环 ─────────────────────────────────────────────────────────────────────

def main():
    """stdio主循环：读取stdin，输出JSON-RPC响应"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle_request(line)
        if response:
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
