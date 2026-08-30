import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"
OUTPUT_DIR = BACKEND_DIR / "outputs" / "reports"
SOURCE_ROOT = BACKEND_DIR.parents[1]


def ensure_runtime_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_modal_jsonl()
    ensure_track_files()
    ensure_kg_files()
    ensure_fusion_candidates()
    ensure_experiment_results()
    ensure_json_defaults()


def read_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings():
    ensure_runtime_data()
    return read_json(DATA_DIR / "settings.json", {})


def jsonl_rows(path, limit=None):
    rows = []
    path = Path(path)
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            if limit and idx > limit:
                break
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def ensure_modal_jsonl():
    source = SOURCE_ROOT / "parsed_0414" / "DJIdata-AIR3"
    for name in ["radar", "spectrum", "recognize", "pho_status", "decrypt"]:
        target = DATA_DIR / f"{name}.jsonl"
        if target.exists():
            continue
        src = source / f"{name}.jsonl"
        if src.exists():
            rows = jsonl_rows(src, limit=120)
        else:
            rows = fallback_modal_rows(name, 80 if name == "radar" else 30)
        with target.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")


def fallback_modal_rows(source, count):
    start = datetime.fromisoformat("2026-04-14T12:46:30+08:00")
    rows = []
    for i in range(count):
        t = start + timedelta(seconds=i * 2)
        target_type = "drone" if source in {"spectrum", "recognize", "decrypt"} else random.choice(["unknown", "bird", "drone"])
        rows.append(
            {
                "record_id": f"{source}_r{i+1:04d}",
                "source": source,
                "line_no": i + 1,
                "line_time_beijing": t.isoformat(),
                "track_id": f"trk_track_{source}_{100+i%12}",
                "target_type": target_type,
                "model": "DJI Air3" if source in {"spectrum", "decrypt"} else "",
                "azimuth": round(105 + random.random() * 15, 2),
                "distance": round(600 + random.random() * 3000, 2),
                "altitude": round(80 + random.random() * 260, 2),
                "speed": round(3 + random.random() * 18, 2),
                "confidence": round(70 + random.random() * 28, 2),
                "snr": round(2 + random.random() * 20, 2),
            }
        )
    return rows


def normalize_record(raw, source, idx):
    payload = raw.get("payload", {}) if isinstance(raw, dict) else {}
    targets = payload.get("targets") or [{}]
    target = targets[0] if targets else {}
    line_time = raw.get("line_time_beijing") or target.get("discovered_at_beijing") or raw.get("time") or ""
    return {
        "record_id": raw.get("record_id") or f"{source}_r{idx:04d}",
        "source": source,
        "track_id": raw.get("track_id") or raw.get("local_track_id") or f"trk_track_{source}_{target.get('target_id', idx)}",
        "time": line_time,
        "target_type": target.get("target_type") or raw.get("target_type") or "",
        "model": target.get("model") or raw.get("model") or "",
        "azimuth": target.get("azimuth_deg") or raw.get("azimuth") or "",
        "distance": target.get("distance_m") or raw.get("distance") or "",
        "altitude": target.get("altitude_m") or raw.get("altitude") or "",
        "speed": target.get("speed_mps") or raw.get("speed") or "",
        "confidence": target.get("confidence") or target.get("similarity") or raw.get("confidence") or "",
        "snr": target.get("snr") or raw.get("snr") or "",
        "raw": raw,
    }


def modal_records(source, page=1, page_size=20, keyword=""):
    rows = [normalize_record(r, source, i) for i, r in enumerate(jsonl_rows(DATA_DIR / f"{source}.jsonl"), start=1)]
    if keyword:
        rows = [r for r in rows if keyword.lower() in json.dumps(r, ensure_ascii=False).lower()]
    total = len(rows)
    start = (page - 1) * page_size
    return {"total": total, "items": rows[start : start + page_size]}


def ensure_track_files():
    cache = SOURCE_ROOT / "KG-Agents" / "data" / "cache" / "track_evidence"
    mapping = {
        "radar_tracks.json": "radar_track_summary.json",
        "spectrum_tracks.json": "spectrum_track_summary.json",
        "recognize_tracks.json": "recognize_track_summary.json",
        "decrypt_tracks.json": "decrypt_label_tracks.json",
    }
    for target_name, source_name in mapping.items():
        target = DATA_DIR / target_name
        if target.exists():
            continue
        src = cache / source_name
        data = read_json(src, None) if src.exists() else None
        if not data:
            data = fallback_tracks(target_name.split("_")[0])
        write_json(target, data)


def fallback_tracks(source):
    count = {"radar": 20, "spectrum": 2, "recognize": 5, "decrypt": 1}.get(source, 5)
    start = datetime.fromisoformat("2026-04-14T12:46:30+08:00")
    tracks = []
    for i in range(count):
        tracks.append(
            {
                "track_id": f"trk_track_{source}_{100+i}",
                "source": source,
                "target_type": "drone" if source != "radar" or i == 0 else random.choice(["bird", "unknown"]),
                "model": "DJI Air3" if source in {"spectrum", "decrypt"} else "",
                "start_time": (start + timedelta(seconds=i * 20)).isoformat(),
                "end_time": (start + timedelta(seconds=160 + i * 20)).isoformat(),
                "point_count": 30 + i,
                "azimuth_mean": round(105 + i * 2.2, 2),
                "altitude_mean": round(80 + i * 9, 2),
                "speed_mean": round(4 + i * 0.7, 2),
                "signal_db_mean": 91.5 if source == "spectrum" else "",
                "confidence_mean": 92 if source in {"spectrum", "recognize"} else "",
                "snr_mean": round(3 + i * 0.9, 2),
            }
        )
    return tracks


def all_tracks(source=None):
    files = {
        "radar": "radar_tracks.json",
        "spectrum": "spectrum_tracks.json",
        "recognize": "recognize_tracks.json",
        "decrypt": "decrypt_tracks.json",
    }
    rows = []
    for src, file in files.items():
        if source and src != source:
            continue
        rows.extend(read_json(DATA_DIR / file, []))
    return rows


def ensure_kg_files():
    nodes = DATA_DIR / "nodes.csv"
    edges = DATA_DIR / "edges.csv"
    if nodes.exists() and edges.exists():
        return
    source_nodes = SOURCE_ROOT / "KG-Agents" / "data" / "global_kg" / "global_nodes.csv"
    source_edges = SOURCE_ROOT / "KG-Agents" / "data" / "global_kg" / "global_edges.csv"
    if source_nodes.exists() and source_edges.exists():
        pd.read_csv(source_nodes, encoding="utf-8-sig", nrows=500).to_csv(nodes, index=False, encoding="utf-8-sig")
        pd.read_csv(source_edges, encoding="utf-8-sig", nrows=800).to_csv(edges, index=False, encoding="utf-8-sig")
        return
    with nodes.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["节点ID", "节点类型", "节点名称", "来源模态", "属性"])
        writer.writeheader()
        for i in range(50):
            writer.writerow({"节点ID": f"node_{i:03d}", "节点类型": random.choice(["轨迹", "轨迹点", "空间位置", "频谱特征"]), "节点名称": f"证据节点{i}", "来源模态": random.choice(["radar", "spectrum", "recognize"]), "属性": "{}"})
    with edges.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["关系ID", "起点ID", "终点ID", "关系类型", "属性"])
        writer.writeheader()
        for i in range(80):
            writer.writerow({"关系ID": f"edge_{i:03d}", "起点ID": f"node_{i%50:03d}", "终点ID": f"node_{(i+7)%50:03d}", "关系类型": random.choice(["包含轨迹点", "具有位置", "具有频谱特征"]), "属性": "{}"})


def kg_graph(limit=300, node_type="", source=""):
    nodes_df = pd.read_csv(DATA_DIR / "nodes.csv", encoding="utf-8-sig")
    edges_df = pd.read_csv(DATA_DIR / "edges.csv", encoding="utf-8-sig")
    if node_type:
        nodes_df = nodes_df[nodes_df.get("节点类型", "").astype(str) == node_type]
    if source:
        nodes_df = nodes_df[nodes_df.get("来源模态", "").astype(str) == source]
    nodes_df = nodes_df.head(int(limit))
    ids = set(nodes_df["节点ID"].astype(str))
    edges_df = edges_df[edges_df["起点ID"].astype(str).isin(ids) & edges_df["终点ID"].astype(str).isin(ids)].head(int(limit) * 2)
    return {
        "nodes": [{"id": r["节点ID"], "name": r.get("节点名称", r["节点ID"]), "type": r.get("节点类型", ""), "source": r.get("来源模态", "")} for _, r in nodes_df.iterrows()],
        "edges": [{"source": r["起点ID"], "target": r["终点ID"], "relation": r.get("关系类型", "")} for _, r in edges_df.iterrows()],
    }


def ensure_fusion_candidates():
    path = DATA_DIR / "fusion_candidates.json"
    if path.exists():
        return
    rows = []
    for i in range(1, 11):
        rows.append(
            {
                "candidate_id": f"C{i:02d}",
                "candidate_source": "radar-spectrum",
                "scenario": random.choice(["完整模态", "自然冲突", "重复频谱"]),
                "radar_track_id": f"trk_track_radar_{200+i}",
                "spectrum_track_id": "trk_track_spectrum_79490",
                "recognize_track_id": f"trk_track_recognize_{i%5+1}" if i < 5 else "",
                "time_overlap": 20 + i * 12,
                "azimuth_diff": round(2 + i * 1.6, 2),
                "kg_score": round(0.93 - i * 0.025, 4),
                "rank": i,
                "conflict_flag": i in {2, 4, 7},
                "decision_status": random.choice(["confirm", "reject", "uncertain"]),
                "score_breakdown": {
                    "time_score": round(0.9 - i * 0.01, 2),
                    "azimuth_score": round(0.95 - i * 0.03, 2),
                    "semantic_score": 1.0,
                    "signal_score": 0.93,
                    "radar_score": round(0.7 - i * 0.03, 2),
                    "motion_score": 0.82,
                },
            }
        )
    write_json(path, rows)


def ensure_experiment_results():
    path = DATA_DIR / "experiment_results.csv"
    if path.exists():
        return
    scenes = ["完整模态", "缺失频谱", "缺失视觉", "仅雷达", "自然冲突", "重复频谱"]
    methods = ["Radar-only", "KG Fusion", "KG-Heuristic", "KG+LLM Agent"]
    values = {
        "Radar-only": (0.0034, 1.0, 0.0068, 0.9966),
        "KG Fusion": (0.1, 1.0, 0.1818, 0.9),
        "KG-Heuristic": (1.0, 1.0, 1.0, 0.0),
        "KG+LLM Agent": (1.0, 1.0, 1.0, 0.0),
    }
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["场景", "方法", "Precision", "Recall", "F1", "FAR", "Token成本", "端到端延迟秒", "F1保持率"])
        writer.writeheader()
        for scene in scenes:
            for method in methods:
                p, r, f1, far = values[method]
                if scene == "自然冲突" and method == "KG+LLM Agent":
                    p, r, f1, far = 0, 0, 0, 1
                if scene in {"缺失频谱", "仅雷达"} and method == "KG Fusion":
                    p, r, f1, far = 0, 0, 0, 0
                writer.writerow({"场景": scene, "方法": method, "Precision": p, "Recall": r, "F1": f1, "FAR": far, "Token成本": 2500 if "LLM" in method else 0, "端到端延迟秒": 18.6 if "LLM" in method else 0.4, "F1保持率": f1})
    write_json(DATA_DIR / "baseline_comparison_results.json", {"source": "local_fallback", "rows": scenes})


def ensure_json_defaults():
    defaults = {
        "chat_sessions.json": [{"session_id": "chat_001", "title": "系统数据概况", "messages": []}],
        "report_draft.json": {"items": [], "title": "无人机多源融合研判报告"},
        "settings.json": {
            "data_dir": "backend/data",
            "local_rule_llm": True,
            "ollama_url": "http://localhost:11434/api/generate",
            "top_k": 5,
            "kg_limit": 300,
            "enable_neo4j": False,
            "neo4j_uri": "bolt://localhost:7687",
            "neo4j_user": "neo4j",
            "neo4j_password": "12345678",
            "neo4j_database": "neo4j",
            "system_title": "基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0",
            "report_format": "markdown",
        },
    }
    for name, data in defaults.items():
        path = DATA_DIR / name
        if not path.exists():
            write_json(path, data)


def fusion_candidates(scenario=None):
    rows = read_json(DATA_DIR / "fusion_candidates.json", [])
    if scenario:
        filtered = [r for r in rows if r.get("scenario") == scenario]
        rows = filtered or rows
    return rows


def experiment_rows():
    return pd.read_csv(DATA_DIR / "experiment_results.csv", encoding="utf-8-sig").to_dict("records")
