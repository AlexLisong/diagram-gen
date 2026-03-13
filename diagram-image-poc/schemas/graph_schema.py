from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

NodeType = Literal[
    "user",
    "frontend",
    "api",
    "service",
    "ai_service",
    "database",
    "queue",
    "cache",
    "storage",
    "external_api",
    "worker",
    "module",
    "repo",
    "document",
    "cloud",
    "decision",
    "verifier",
    "output",
]

EdgeType = Literal[
    "http",
    "internal_http",
    "stream",
    "reads",
    "writes",
    "publishes",
    "consumes",
    "stores_in",
    "calls",
    "depends_on",
    "triggers",
    "branches",
    "approves",
]

GraphDiagramType = Literal[
    "system_context",
    "high_level_architecture",
    "request_flow",
    "module_structure",
    "decision_flow",
    "verification_flow",
    "deployment",
    "data_flow",
]

Direction = Literal["LR", "TB"]


class GraphNode(BaseModel):
    id: str
    label: str
    type: NodeType
    group: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    label: str = ""
    type: EdgeType

    model_config = {"populate_by_name": True}


class GraphGroup(BaseModel):
    id: str
    label: str


class GraphDiagramSpec(BaseModel):
    diagram_type: GraphDiagramType
    title: str
    direction: Direction = "LR"
    groups: list[GraphGroup] = Field(default_factory=list)
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    notes: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_spec(self) -> "GraphDiagramSpec":
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Node ids must be unique")

        known_ids = set(node_ids)
        for edge in self.edges:
            if edge.from_id not in known_ids:
                raise ValueError(f"Unknown edge source: {edge.from_id}")
            if edge.to_id not in known_ids:
                raise ValueError(f"Unknown edge target: {edge.to_id}")
            if len(edge.label) > 36:
                raise ValueError(f"Edge label too long: {edge.label}")

        known_groups = {group.id for group in self.groups}
        for node in self.nodes:
            if len(node.label) > 40:
                raise ValueError(f"Node label too long: {node.label}")
            if node.group and node.group not in known_groups:
                raise ValueError(f"Node {node.id} references unknown group {node.group}")

        return self
