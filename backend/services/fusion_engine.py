from __future__ import annotations

import hashlib
from collections import Counter, defaultdict, deque
from datetime import datetime
from statistics import mean
from typing import Any

from services.data_loader import all_tracks, experiment_rows, fusion_candidates, kg_graph, modal_records


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def score_inverse(value: float, best: float, worst: float) -> float:
    if value <= best:
        return 1.0
    if value >= worst:
        return 0.0
    return clamp(1.0 - (value - best) / (worst - best))


def time_overlap(track_a: dict[str, Any], track_b: dict[str, Any]) -> tuple[float, float]:
    start_a = parse_time(track_a.get("start_time"))
    end_a = parse_time(track_a.get("end_time"))
    start_b = parse_time(track_b.get("start_time"))
    end_b = parse_time(track_b.get("end_time"))
    if not all([start_a, end_a, start_b, end_b]):
        return 0.0, 0.0
    overlap = max(0.0, (min(end_a, end_b) - max(start_a, start_b)).total_seconds())
    denominator = max(1.0, min((end_a - start_a).total_seconds(), (end_b - start_b).total_seconds()))
    return overlap, clamp(overlap / denominator)


def angle_difference(a: Any, b: Any) -> float:
    av = to_float(a, 999.0)
    bv = to_float(b, 999.0)
    if av == 999.0 or bv == 999.0:
        return 180.0
    return abs((av - bv + 180.0) % 360.0 - 180.0)


def semantic_score(radar_type: str, spectrum_type: str, spectrum_model: str = "") -> float:
    radar = (radar_type or "").lower()
    spectrum = (spectrum_type or "").lower()
    model = (spectrum_model or "").lower()
    if "drone" in radar and "drone" in spectrum:
        return 1.0
    if radar in {"unknown", ""} and ("drone" in spectrum or model):
        return 0.78
    if "bird" in radar and "drone" in spectrum:
        return 0.28
    if "drone" in radar and not spectrum:
        return 0.64
    if "drone" in spectrum and not radar:
        return 0.58
    return 0.45


def snr_score(value: Any) -> float:
    return clamp((to_float(value) - 8.0) / 22.0)


def signal_score(signal_db: Any, confidence: Any) -> float:
    signal_part = clamp((to_float(signal_db) - 50.0) / 55.0)
    confidence_part = clamp(to_float(confidence) / 100.0)
    return round(0.55 * signal_part + 0.45 * confidence_part, 4)


def motion_score(speed: Any, altitude: Any, distance: Any) -> float:
    speed_value = to_float(speed)
    altitude_value = to_float(altitude)
    distance_value = to_float(distance)
    speed_part = score_inverse(abs(speed_value - 8.0), 0.0, 28.0)
    altitude_part = 1.0 if 20.0 <= altitude_value <= 220.0 else score_inverse(abs(altitude_value - 120.0), 80.0, 260.0)
    distance_part = 1.0 if 50.0 <= distance_value <= 3500.0 else 0.45
    return round(0.45 * speed_part + 0.35 * altitude_part + 0.20 * distance_part, 4)


def candidate_signature(candidate: dict[str, Any]) -> str:
    fields = [
        "candidate_id",
        "radar_track_id",
        "spectrum_track_id",
        "recognize_track_id",
        "time_overlap",
        "azimuth_diff",
        "kg_score",
        "conflict_flag",
    ]
    text = "|".join(str(candidate.get(field, "")) for field in fields)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def compute_candidate_score(candidate: dict[str, Any]) -> dict[str, float]:
    overlap_score = clamp(to_float(candidate.get("time_overlap") or candidate.get("time_overlap_seconds")) / 120.0)
    azimuth_score = score_inverse(to_float(candidate.get("azimuth_diff") or candidate.get("azimuth_difference_deg"), 180.0), 5.0, 60.0)
    sem_score = semantic_score(
        str(candidate.get("radar_target_type", candidate.get("radar_semantic", ""))),
        str(candidate.get("spectrum_target_type", candidate.get("spectrum_semantic", ""))),
        str(candidate.get("spectrum_model", "")),
    )
    sig_score = signal_score(candidate.get("signal_db_mean"), candidate.get("confidence_mean"))
    radar_part = snr_score(candidate.get("snr_mean") or candidate.get("radar_snr_mean"))
    motion_part = motion_score(candidate.get("speed_mean"), candidate.get("altitude_mean"), candidate.get("distance_mean"))
    conflict_penalty = 0.12 if candidate.get("conflict_flag") else 0.0
    kg_score = (
        0.22 * overlap_score
        + 0.22 * azimuth_score
        + 0.18 * sem_score
        + 0.14 * sig_score
        + 0.12 * radar_part
        + 0.12 * motion_part
        - conflict_penalty
    )
    return {
        "time_score": round(overlap_score, 4),
        "azimuth_score": round(azimuth_score, 4),
        "semantic_score": round(sem_score, 4),
        "signal_score": round(sig_score, 4),
        "radar_score": round(radar_part, 4),
        "motion_score": round(motion_part, 4),
        "conflict_penalty": round(conflict_penalty, 4),
        "kg_score": round(clamp(kg_score), 4),
    }


def normalize_candidate(candidate: dict[str, Any], rank: int = 0) -> dict[str, Any]:
    score_breakdown = candidate.get("score_breakdown") or compute_candidate_score(candidate)
    computed_score = score_breakdown.get("kg_score")
    if computed_score is None:
        computed_score = compute_candidate_score(candidate)["kg_score"]
    item = {
        **candidate,
        "candidate_id": candidate.get("candidate_id") or f"C{rank:02d}",
        "candidate_source": candidate.get("candidate_source") or "radar-spectrum",
        "radar_track_id": candidate.get("radar_track_id") or candidate.get("radar_track", ""),
        "spectrum_track_id": candidate.get("spectrum_track_id") or candidate.get("spectrum_track", ""),
        "recognize_track_id": candidate.get("recognize_track_id", ""),
        "time_overlap": to_float(candidate.get("time_overlap") or candidate.get("time_overlap_seconds")),
        "azimuth_diff": to_float(candidate.get("azimuth_diff") or candidate.get("azimuth_difference_deg"), 180.0),
        "rank": int(candidate.get("rank") or rank),
        "conflict_flag": bool(candidate.get("conflict_flag", False)),
        "decision_status": candidate.get("decision_status") or "KG positive",
        "score_breakdown": score_breakdown,
        "kg_score": round(to_float(candidate.get("kg_score"), computed_score), 4),
    }
    item["signature"] = candidate_signature(item)
    return item


def generate_candidate_pool(scenario: str = "", top_k: int = 10) -> list[dict[str, Any]]:
    existing = [normalize_candidate(row, idx + 1) for idx, row in enumerate(fusion_candidates(scenario or None))]
    if existing:
        return rank_candidates(existing)[:top_k]

    radar_tracks = all_tracks("radar")
    spectrum_tracks = all_tracks("spectrum")
    candidates: list[dict[str, Any]] = []
    for spectrum in spectrum_tracks or [{}]:
        per_spectrum = []
        for radar in radar_tracks:
            overlap_seconds, overlap_ratio = time_overlap(radar, spectrum)
            diff = angle_difference(radar.get("azimuth_mean"), spectrum.get("azimuth_mean"))
            row = {
                "candidate_source": "radar-spectrum" if spectrum else "radar-only",
                "radar_track_id": radar.get("track_id", ""),
                "spectrum_track_id": spectrum.get("track_id", ""),
                "time_overlap": round(overlap_seconds, 2),
                "time_overlap_ratio": round(overlap_ratio, 4),
                "azimuth_diff": round(diff, 4),
                "radar_target_type": radar.get("target_type", ""),
                "spectrum_target_type": spectrum.get("target_type", ""),
                "spectrum_model": spectrum.get("model", ""),
                "snr_mean": radar.get("snr_mean", 0),
                "distance_mean": radar.get("distance_mean", 0),
                "altitude_mean": radar.get("altitude_mean", 0),
                "speed_mean": radar.get("speed_mean", 0),
                "signal_db_mean": spectrum.get("signal_db_mean", 0),
                "confidence_mean": spectrum.get("confidence_mean", 0),
                "conflict_flag": str(radar.get("target_type", "")).lower() == "bird"
                and str(spectrum.get("target_type", "")).lower() == "drone",
            }
            row["score_breakdown"] = compute_candidate_score(row)
            row["kg_score"] = row["score_breakdown"]["kg_score"]
            per_spectrum.append(row)
        per_spectrum.sort(key=lambda item: (-item["kg_score"], item["azimuth_diff"]))
        candidates.extend(per_spectrum[:top_k])

    for idx, row in enumerate(candidates, start=1):
        row["candidate_id"] = f"C{idx:02d}"
        row["rank"] = idx
    return rank_candidates(candidates)[:top_k]


def rank_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [normalize_candidate(item, idx + 1) for idx, item in enumerate(candidates)]
    rows.sort(key=lambda item: (item["conflict_flag"], -item["kg_score"], item["azimuth_diff"], -item["time_overlap"]))
    for idx, item in enumerate(rows, start=1):
        item["rank"] = idx
    return rows


def candidate_statistics(scenario: str = "") -> dict[str, Any]:
    rows = generate_candidate_pool(scenario, 50)
    if not rows:
        return {"candidate_count": 0, "avg_score": 0, "conflict_count": 0, "source_distribution": {}}
    return {
        "candidate_count": len(rows),
        "avg_score": round(mean(item["kg_score"] for item in rows), 4),
        "max_score": max(item["kg_score"] for item in rows),
        "min_score": min(item["kg_score"] for item in rows),
        "conflict_count": sum(1 for item in rows if item["conflict_flag"]),
        "source_distribution": dict(Counter(item["candidate_source"] for item in rows)),
        "top_candidate": rows[0],
    }


def candidate_explanation(candidate: dict[str, Any]) -> dict[str, Any]:
    item = normalize_candidate(candidate)
    score = item.get("score_breakdown") or compute_candidate_score(item)
    evidence = []
    evidence.append("时间重叠充分" if score["time_score"] >= 0.7 else "时间重叠不足或中等")
    evidence.append("方位角一致性强" if score["azimuth_score"] >= 0.75 else "方位角存在偏差")
    if item["conflict_flag"]:
        evidence.append("存在 radar 与 spectrum 语义冲突")
    elif score["semantic_score"] >= 0.75:
        evidence.append("语义证据支持无人机目标")
    if score["signal_score"] >= 0.65:
        evidence.append("频谱信号强度和置信度较高")
    if score["radar_score"] >= 0.55:
        evidence.append("雷达 SNR 支持稳定目标")
    if score["motion_score"] >= 0.6:
        evidence.append("运动特征处于合理范围")
    recommendation = "confirm" if item["kg_score"] >= 0.78 and not item["conflict_flag"] else "uncertain"
    if item["kg_score"] < 0.45:
        recommendation = "reject"
    return {
        "candidate_id": item["candidate_id"],
        "recommendation": recommendation,
        "evidence": evidence,
        "score_breakdown": score,
        "summary": "；".join(evidence),
    }


def build_llm_candidate_input(candidate: dict[str, Any]) -> dict[str, Any]:
    item = normalize_candidate(candidate)
    return {
        "候选编号": item["candidate_id"],
        "候选来源": item["candidate_source"],
        "雷达轨迹": item["radar_track_id"],
        "频谱轨迹": item["spectrum_track_id"],
        "视觉轨迹": item["recognize_track_id"],
        "时间重叠秒数": item["time_overlap"],
        "方位角差": item["azimuth_diff"],
        "KG融合分数": item["kg_score"],
        "冲突标记": item["conflict_flag"],
        "得分明细": item["score_breakdown"],
    }


def build_llm_prompt_payload(candidate_id: str, scenario: str = "") -> dict[str, Any]:
    rows = generate_candidate_pool(scenario, 10)
    selected = next((row for row in rows if row["candidate_id"] == candidate_id), rows[0] if rows else {})
    return {
        "task": "基于知识图谱候选证据进行无人机目标研判",
        "scenario": scenario or "完整模态",
        "available_modalities": ["radar", "spectrum", "recognize", "pho_status"],
        "selected_candidate": build_llm_candidate_input(selected) if selected else {},
        "candidate_pool": [build_llm_candidate_input(row) for row in rows],
        "decision_schema": {
            "decision": "confirm / reject / uncertain",
            "risk_level": "高 / 中 / 低",
            "reason": "中文理由",
            "suggestion": "处置建议",
        },
    }


def deterministic_llm_decision(candidate: dict[str, Any]) -> dict[str, Any]:
    item = normalize_candidate(candidate)
    explanation = candidate_explanation(item)
    if item["conflict_flag"] and item["kg_score"] < 0.86:
        decision = "uncertain"
        risk_level = "中"
        suggestion = "建议进入人工复核队列，继续观察雷达轨迹和视觉证据。"
    elif item["kg_score"] >= 0.78:
        decision = "confirm"
        risk_level = "高"
        suggestion = "建议持续跟踪并触发告警。"
    elif item["kg_score"] >= 0.48:
        decision = "uncertain"
        risk_level = "中"
        suggestion = "建议保留候选，等待更多模态证据。"
    else:
        decision = "reject"
        risk_level = "低"
        suggestion = "建议暂不告警，仅保留为低优先级记录。"
    return {
        "candidate_id": item["candidate_id"],
        "decision": decision,
        "risk_level": risk_level,
        "reason": explanation["summary"],
        "suggestion": suggestion,
        "evidence": [{"type": "kg", "field": key, "value": value} for key, value in explanation["score_breakdown"].items()],
        "prompt_payload": build_llm_prompt_payload(item["candidate_id"]),
    }


def evaluate_positive_set(positive_ids: list[str], scenario: str = "") -> dict[str, Any]:
    rows = generate_candidate_pool(scenario, 50)
    positives = [row for row in rows if row["candidate_id"] in set(positive_ids)]
    tp = 1 if any(not row["conflict_flag"] and row["rank"] <= 3 for row in positives) else 0
    fp = max(0, len(positives) - tp)
    fn = 0 if tp else 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    far = fp / (tp + fp) if tp + fp else 0.0
    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1": round(f1, 4),
        "FAR": round(far, 4),
        "positive_count": len(positives),
        "positive_ids": positive_ids,
    }


def graph_adjacency(limit: int = 300) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    graph = kg_graph(limit)
    nodes = {node["id"]: node for node in graph["nodes"]}
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in graph["edges"]:
        adjacency[edge["source"]].append({"neighbor": edge["target"], "relation": edge.get("relation", ""), "direction": "out"})
        adjacency[edge["target"]].append({"neighbor": edge["source"], "relation": edge.get("relation", ""), "direction": "in"})
    return adjacency, nodes


def graph_local_metrics(limit: int = 300) -> dict[str, Any]:
    adjacency, nodes = graph_adjacency(limit)
    degrees = {node_id: len(edges) for node_id, edges in adjacency.items()}
    type_counter = Counter(node.get("type", "unknown") for node in nodes.values())
    source_counter = Counter(node.get("source", "unknown") for node in nodes.values())
    top_degree = sorted(degrees.items(), key=lambda item: item[1], reverse=True)[:10]
    return {
        "node_count": len(nodes),
        "edge_touch_count": sum(degrees.values()),
        "type_distribution": dict(type_counter),
        "source_distribution": dict(source_counter),
        "top_degree_nodes": [
            {"node_id": node_id, "degree": degree, "name": nodes.get(node_id, {}).get("name", node_id)}
            for node_id, degree in top_degree
        ],
    }


def graph_shortest_path(source_id: str, target_id: str, limit: int = 500) -> dict[str, Any]:
    adjacency, nodes = graph_adjacency(limit)
    if source_id not in nodes or target_id not in nodes:
        return {"found": False, "path": [], "message": "source or target not in current graph sample"}
    queue = deque([(source_id, [source_id])])
    visited = {source_id}
    while queue:
        current, path = queue.popleft()
        if current == target_id:
            return {"found": True, "path": path, "nodes": [nodes[node_id] for node_id in path], "length": len(path) - 1}
        for edge in adjacency.get(current, []):
            neighbor = edge["neighbor"]
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append((neighbor, path + [neighbor]))
    return {"found": False, "path": [], "message": "no path in current graph sample"}


def graph_ego(node_id: str, depth: int = 1, limit: int = 500) -> dict[str, Any]:
    adjacency, nodes = graph_adjacency(limit)
    if node_id not in nodes:
        return {"center": node_id, "nodes": [], "edges": []}
    visited = {node_id}
    frontier = {node_id}
    for _ in range(max(1, depth)):
        next_frontier = set()
        for current in frontier:
            for edge in adjacency.get(current, []):
                if edge["neighbor"] not in visited:
                    visited.add(edge["neighbor"])
                    next_frontier.add(edge["neighbor"])
        frontier = next_frontier
    graph = kg_graph(limit)
    edges = [edge for edge in graph["edges"] if edge["source"] in visited and edge["target"] in visited]
    return {"center": node_id, "nodes": [nodes[nid] for nid in visited if nid in nodes], "edges": edges}


def modality_quality_report() -> dict[str, Any]:
    report = {}
    for source in ["radar", "spectrum", "recognize", "pho_status", "decrypt"]:
        records = modal_records(source, page=1, page_size=100000)["items"]
        total = len(records)
        track_ids = {row.get("track_id") for row in records if row.get("track_id")}
        target_types = Counter(row.get("target_type") or "unknown" for row in records)
        missing_time = sum(1 for row in records if not row.get("time"))
        completeness = {}
        for field in ["azimuth", "distance", "altitude", "speed", "confidence", "snr"]:
            present = sum(1 for row in records if row.get(field) not in {"", None})
            completeness[field] = round(present / total, 4) if total else 0.0
        report[source] = {
            "record_count": total,
            "track_count": len(track_ids),
            "target_type_distribution": dict(target_types),
            "missing_time_count": missing_time,
            "field_completeness": completeness,
        }
    return report


def experiment_summary() -> dict[str, Any]:
    rows = experiment_rows()
    scene_key = "场景"
    method_key = "方法"
    scene_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    method_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        scene_groups[str(row.get(scene_key))].append(row)
        method_groups[str(row.get(method_key))].append(row)
    scene_summary = []
    for scene, items in scene_groups.items():
        best = max(items, key=lambda item: to_float(item.get("F1")))
        worst = max(items, key=lambda item: to_float(item.get("FAR")))
        scene_summary.append(
            {
                "scene": scene,
                "method_count": len(items),
                "best_f1_method": best.get(method_key),
                "best_f1": to_float(best.get("F1")),
                "highest_far_method": worst.get(method_key),
                "highest_far": to_float(worst.get("FAR")),
            }
        )
    method_summary = []
    for method, items in method_groups.items():
        method_summary.append(
            {
                "method": method,
                "avg_f1": round(mean(to_float(item.get("F1")) for item in items), 4),
                "avg_far": round(mean(to_float(item.get("FAR")) for item in items), 4),
                "scene_count": len(items),
            }
        )
    return {"scene_summary": scene_summary, "method_summary": method_summary}


def build_analysis_report(candidate_id: str = "C01", scenario: str = "") -> dict[str, Any]:
    candidates = generate_candidate_pool(scenario, 10)
    selected = next((item for item in candidates if item["candidate_id"] == candidate_id), candidates[0] if candidates else {})
    decision = deterministic_llm_decision(selected) if selected else {}
    quality = modality_quality_report()
    experiments = experiment_summary()
    lines = ["# 无人机多源感知融合分析报告", "", "## 1. 数据质量概况"]
    for source, item in quality.items():
        lines.append(f"- {source}: records={item['record_count']}, tracks={item['track_count']}")
    lines += [
        "",
        "## 2. 候选目标研判",
        f"- 候选编号：{candidate_id}",
        f"- 研判结果：{decision.get('decision')}",
        f"- 风险等级：{decision.get('risk_level')}",
        f"- 研判理由：{decision.get('reason')}",
        "",
        "## 3. 实验结果摘要",
    ]
    for row in experiments["method_summary"]:
        lines.append(f"- {row['method']}: avg_f1={row['avg_f1']}, avg_far={row['avg_far']}")
    return {"candidate": selected, "decision": decision, "quality": quality, "experiments": experiments, "markdown": "\n".join(lines)}
