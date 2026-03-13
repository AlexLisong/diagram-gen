from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_deployment() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="deployment",
        title="Content OS Deployment View",
        direction="LR",
        groups=[
            GraphGroup(id="edge", label="Edge"),
            GraphGroup(id="app", label="Application"),
            GraphGroup(id="data", label="Data"),
            GraphGroup(id="external", label="External"),
        ],
        nodes=[
            GraphNode(id="browser", label="Creator Browser", type="user", group="edge"),
            GraphNode(id="web", label="Frontend App", type="frontend", group="app"),
            GraphNode(id="api", label="API Service", type="api", group="app"),
            GraphNode(id="worker", label="Planner Worker", type="worker", group="app"),
            GraphNode(id="db", label="Postgres", type="database", group="data"),
            GraphNode(id="storage", label="Asset Storage", type="storage", group="data"),
            GraphNode(id="openai", label="OpenAI API", type="external_api", group="external"),
        ],
        edges=[
            GraphEdge(**{"from": "browser", "to": "web", "label": "HTTPS", "type": "http"}),
            GraphEdge(**{"from": "web", "to": "api", "label": "REST", "type": "http"}),
            GraphEdge(**{"from": "api", "to": "worker", "label": "jobs", "type": "triggers"}),
            GraphEdge(**{"from": "api", "to": "db", "label": "metadata", "type": "writes"}),
            GraphEdge(**{"from": "worker", "to": "storage", "label": "exports", "type": "stores_in"}),
            GraphEdge(**{"from": "worker", "to": "openai", "label": "LLM calls", "type": "http"}),
        ],
        notes=[
            "POC deployment view is intentionally simplified and cloud-neutral.",
        ],
        source_refs=["synthetic:content_os_deployment"],
    )
