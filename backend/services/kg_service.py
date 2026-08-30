from __future__ import annotations

from typing import Any

from services.data_loader import kg_graph
from services.fusion_engine import graph_ego, graph_local_metrics, graph_shortest_path
from services.neo4j_service import neo4j_graph_sample, neo4j_status


def get_graph(limit: int = 300, node_type: str = "", source: str = "") -> dict[str, Any]:
    neo4j_graph = neo4j_graph_sample(limit)
    if neo4j_graph:
        return _annotate_graph(neo4j_graph, source_name="neo4j")
    return _annotate_graph(kg_graph(limit, node_type, source), source_name="local_csv")


def get_neo4j_status() -> dict[str, Any]:
    return neo4j_status()


def get_node_detail(node_id: str) -> dict[str, Any]:
    graph = kg_graph(500)
    node = next((item for item in graph["nodes"] if item["id"] == node_id), None)
    return node or {"id": node_id, "name": node_id, "type": "unknown"}


def get_neighbors(node_id: str) -> dict[str, Any]:
    graph = kg_graph(500)
    edges = [
        edge for edge in graph["edges"] if edge["source"] == node_id or edge["target"] == node_id
    ]
    ids = {edge["source"] for edge in edges} | {edge["target"] for edge in edges}
    nodes = [node for node in graph["nodes"] if node["id"] in ids]
    return {"nodes": nodes, "edges": edges}


def get_metrics(limit: int = 300) -> dict[str, Any]:
    return graph_local_metrics(limit)


def get_ego_graph(node_id: str, depth: int = 1, limit: int = 500) -> dict[str, Any]:
    return graph_ego(node_id, depth, limit)


def get_shortest_path(source_id: str, target_id: str, limit: int = 500) -> dict[str, Any]:
    return graph_shortest_path(source_id, target_id, limit)


def _annotate_graph(graph: dict[str, Any], source_name: str) -> dict[str, Any]:
    graph = dict(graph)
    graph["graph_backend"] = source_name
    graph["summary"] = {
        "node_count": len(graph.get("nodes", [])),
        "edge_count": len(graph.get("edges", [])),
        "backend": source_name,
    }
    return graph
