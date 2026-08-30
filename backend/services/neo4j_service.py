from __future__ import annotations

from typing import Any

from services.data_loader import load_settings


def neo4j_status() -> dict[str, Any]:
    settings = load_settings()
    uri = settings.get("neo4j_uri", "bolt://localhost:7687")
    user = settings.get("neo4j_user", "neo4j")
    password = settings.get("neo4j_password", "12345678")
    database = settings.get("neo4j_database", "neo4j")
    try:
        from neo4j import GraphDatabase
    except Exception as exc:
        return {
            "connected": False,
            "mode": "local_csv_fallback",
            "uri": uri,
            "database": database,
            "message": f"neo4j driver unavailable: {exc}",
        }

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database) as session:
            count = session.run("MATCH (n) RETURN count(n) AS node_count").single()["node_count"]
        driver.close()
        return {
            "connected": True,
            "mode": "neo4j",
            "uri": uri,
            "database": database,
            "node_count": count,
            "message": "Neo4j connection ok",
        }
    except Exception as exc:
        return {
            "connected": False,
            "mode": "local_csv_fallback",
            "uri": uri,
            "database": database,
            "message": str(exc),
        }


def neo4j_graph_sample(limit: int = 300) -> dict[str, Any] | None:
    settings = load_settings()
    if not settings.get("enable_neo4j", False):
        return None
    try:
        from neo4j import GraphDatabase
    except Exception:
        return None

    uri = settings.get("neo4j_uri", "bolt://localhost:7687")
    user = settings.get("neo4j_user", "neo4j")
    password = settings.get("neo4j_password", "12345678")
    database = settings.get("neo4j_database", "neo4j")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database=database) as session:
            rows = session.run(
                """
                MATCH (n)
                WITH n LIMIT $limit
                OPTIONAL MATCH (n)-[r]-(m)
                RETURN n, r, m
                LIMIT $edge_limit
                """,
                limit=limit,
                edge_limit=limit * 2,
            )
            nodes = {}
            edges = []
            for row in rows:
                for key in ("n", "m"):
                    node = row.get(key)
                    if node is None:
                        continue
                    labels = list(node.labels)
                    node_id = str(node.element_id)
                    nodes[node_id] = {
                        "id": node_id,
                        "name": str(node.get("name", node.get("id", node_id))),
                        "type": labels[0] if labels else "Neo4j节点",
                        "source": node.get("source", node.get("来源模态", "neo4j")),
                    }
                rel = row.get("r")
                if rel is not None:
                    edges.append(
                        {
                            "source": str(rel.start_node.element_id),
                            "target": str(rel.end_node.element_id),
                            "relation": rel.type,
                        }
                    )
        driver.close()
        if nodes:
            return {"nodes": list(nodes.values()), "edges": edges}
    except Exception:
        return None
    return None
