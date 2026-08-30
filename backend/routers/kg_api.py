from fastapi import APIRouter

from services.kg_service import (
    get_ego_graph,
    get_graph,
    get_metrics,
    get_neighbors,
    get_neo4j_status,
    get_node_detail,
    get_shortest_path,
)

router = APIRouter()


@router.get("/graph")
def graph(limit: int = 300, node_type: str = "", source: str = ""):
    return get_graph(limit, node_type, source)


@router.get("/neo4j-status")
def status():
    return get_neo4j_status()


@router.get("/node/{node_id}")
def node_detail(node_id: str):
    return get_node_detail(node_id)


@router.get("/neighbors/{node_id}")
def neighbors(node_id: str):
    return get_neighbors(node_id)


@router.get("/metrics")
def metrics(limit: int = 300):
    return get_metrics(limit)


@router.get("/ego/{node_id}")
def ego(node_id: str, depth: int = 1, limit: int = 500):
    return get_ego_graph(node_id, depth, limit)


@router.get("/path")
def path(source_id: str, target_id: str, limit: int = 500):
    return get_shortest_path(source_id, target_id, limit)
