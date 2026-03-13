from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_high_level_architecture() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="high_level_architecture",
        title="Content OS High-Level Architecture",
        direction="LR",
        groups=[
            GraphGroup(id="ingestion", label="Ingestion"),
            GraphGroup(id="planning", label="Planning"),
            GraphGroup(id="generation", label="Generation"),
            GraphGroup(id="delivery", label="Delivery"),
        ],
        nodes=[
            GraphNode(id="ingestor", label="Ingestion", type="service", group="ingestion"),
            GraphNode(id="graph", label="Graph Builder", type="service", group="planning"),
            GraphNode(id="planner", label="Planner", type="ai_service", group="planning"),
            GraphNode(id="slides", label="Slide Generator", type="service", group="generation"),
            GraphNode(id="script", label="Script Writer", type="service", group="generation"),
            GraphNode(id="verifier", label="Verifier", type="verifier", group="generation"),
            GraphNode(id="exporter", label="Exporter", type="output", group="delivery"),
        ],
        edges=[
            GraphEdge(**{"from": "ingestor", "to": "graph", "label": "normalized data", "type": "writes"}),
            GraphEdge(**{"from": "graph", "to": "planner", "label": "diagram spec", "type": "calls"}),
            GraphEdge(**{"from": "planner", "to": "slides", "label": "slide plan", "type": "calls"}),
            GraphEdge(**{"from": "planner", "to": "script", "label": "narrative plan", "type": "calls"}),
            GraphEdge(**{"from": "slides", "to": "verifier", "label": "claims", "type": "publishes"}),
            GraphEdge(**{"from": "script", "to": "verifier", "label": "facts", "type": "publishes"}),
            GraphEdge(**{"from": "verifier", "to": "exporter", "label": "approved assets", "type": "approves"}),
        ],
        notes=[
            "Phase 1 focus: small node count, clear handoffs, deterministic output.",
        ],
        source_refs=["synthetic:content_os_architecture"],
    )
