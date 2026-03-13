"""
Shared Pydantic models for the diagram pipeline.
Three layers: RawGraph → CanonicalGraph → DiagramSpec
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

# ── Enums ────────────────────────────────────────────────────────────

NodeType = Literal[
    "frontend", "api", "service", "ai_service", "database",
    "queue", "cache", "storage", "auth", "external_api",
    "worker", "module", "lambda", "app_service", "vm",
    "function", "repo", "pipeline", "user", "s3", "rds", "redis",
]

EdgeType = Literal[
    "http", "internal_http", "grpc", "stream",
    "reads", "writes", "publishes", "consumes",
    "deploys_to", "authenticates_via", "triggers",
    "stores_in", "calls", "depends_on",
]

DiagramType = Literal[
    "system_architecture",
    "request_flow",
    "module_structure",
    "cloud_resource",
]

Direction = Literal["LR", "TB", "RL", "BT"]

# ── Layer 1: Raw Graph (dirty extraction result) ────────────────────

class RawNode(BaseModel):
    id: str
    label: str
    raw_type: str = ""  # not yet normalized
    source: str = ""    # where it was found
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RawEdge(BaseModel):
    from_id: str
    to_id: str
    label: str = ""
    evidence: str = ""  # why we think this edge exists


class RawGraph(BaseModel):
    candidate_nodes: List[RawNode]
    candidate_edges: List[RawEdge]
    evidence: List[str] = Field(default_factory=list)


# ── Layer 2: Canonical Graph (normalized, semantic) ─────────────────

class GraphNode(BaseModel):
    id: str
    label: str
    type: NodeType
    group: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    label: Optional[str] = None
    type: EdgeType

    model_config = {"populate_by_name": True}


class GraphGroup(BaseModel):
    id: str
    label: str


class Annotation(BaseModel):
    target: str
    text: str


class CanonicalGraph(BaseModel):
    title: str
    diagram_type: DiagramType = "system_architecture"
    direction: Direction = "LR"
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    groups: List[GraphGroup] = Field(default_factory=list)
    annotations: List[Annotation] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list)


# ── Layer 3: Diagram Spec (view for one slide) ─────────────────────

class DiagramSpec(BaseModel):
    diagram_type: DiagramType
    title: str
    direction: Direction = "LR"
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    groups: List[GraphGroup] = Field(default_factory=list)
    legend: bool = False
    notes: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_refs(self) -> "DiagramSpec":
        node_ids = {n.id for n in self.nodes}
        for edge in self.edges:
            if edge.from_id not in node_ids:
                raise ValueError(f"Edge from_id '{edge.from_id}' not in nodes")
            if edge.to_id not in node_ids:
                raise ValueError(f"Edge to_id '{edge.to_id}' not in nodes")
        for group in self.groups:
            members = [n for n in self.nodes if n.group == group.id]
            if not members:
                raise ValueError(f"Group '{group.id}' has no members")
        return self
