from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_system_context() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="system_context",
        title="Content OS System Context",
        direction="LR",
        groups=[
            GraphGroup(id="inputs", label="Inputs"),
            GraphGroup(id="system", label="System"),
            GraphGroup(id="outputs", label="Outputs"),
        ],
        nodes=[
            GraphNode(id="creator", label="Creator", type="user", group="inputs"),
            GraphNode(id="repo", label="Source Repo", type="repo", group="inputs"),
            GraphNode(id="docs", label="Docs", type="document", group="inputs"),
            GraphNode(id="cloud", label="Cloud Snapshot", type="cloud", group="inputs"),
            GraphNode(id="content_os", label="Content OS", type="ai_service", group="system"),
            GraphNode(id="slides", label="Slides", type="output", group="outputs"),
            GraphNode(id="script", label="Speaker Script", type="output", group="outputs"),
            GraphNode(id="recording", label="Recording Session", type="output", group="outputs"),
        ],
        edges=[
            GraphEdge(**{"from": "creator", "to": "content_os", "label": "brief", "type": "http"}),
            GraphEdge(**{"from": "repo", "to": "content_os", "label": "code", "type": "reads"}),
            GraphEdge(**{"from": "docs", "to": "content_os", "label": "context", "type": "reads"}),
            GraphEdge(**{"from": "cloud", "to": "content_os", "label": "state", "type": "reads"}),
            GraphEdge(**{"from": "content_os", "to": "slides", "label": "deck", "type": "writes"}),
            GraphEdge(**{"from": "content_os", "to": "script", "label": "notes", "type": "writes"}),
            GraphEdge(**{"from": "slides", "to": "recording", "label": "present", "type": "triggers"}),
            GraphEdge(**{"from": "script", "to": "recording", "label": "narrate", "type": "triggers"}),
        ],
        notes=[
            "System boundary is explicit: inputs on the left, generated artifacts on the right.",
        ],
        source_refs=["synthetic:content_os_context"],
    )
