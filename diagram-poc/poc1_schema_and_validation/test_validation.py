"""
POC 1: Schema validation — verify that Pydantic models catch bad data.
Tests node uniqueness, edge refs, group membership, node/edge limits.
"""

import sys
sys.path.insert(0, "..")

import pytest
from pydantic import ValidationError

from models import (
    CanonicalGraph, DiagramSpec, GraphEdge, GraphGroup, GraphNode,
)

# ── Thresholds per diagram type ─────────────────────────────────────

NODE_LIMITS: dict[str, tuple[int, int]] = {
    "system_architecture": (2, 9),
    "request_flow": (2, 8),
    "module_structure": (2, 12),
    "cloud_resource": (2, 10),
}


def validate_diagram_limits(spec: DiagramSpec) -> list[str]:
    """Business-rule validation on top of schema validation."""
    errors: list[str] = []

    # Node count limits
    lo, hi = NODE_LIMITS.get(spec.diagram_type, (2, 12))
    if len(spec.nodes) < lo:
        errors.append(f"Too few nodes: {len(spec.nodes)} < {lo}")
    if len(spec.nodes) > hi:
        errors.append(f"Too many nodes: {len(spec.nodes)} > {hi}")

    # Duplicate node ids
    ids = [n.id for n in spec.nodes]
    dupes = [x for x in ids if ids.count(x) > 1]
    if dupes:
        errors.append(f"Duplicate node ids: {set(dupes)}")

    # Orphan nodes (no edges)
    connected = set()
    for e in spec.edges:
        connected.add(e.from_id)
        connected.add(e.to_id)
    orphans = set(ids) - connected
    if len(orphans) > 1:
        errors.append(f"Too many orphan nodes: {orphans}")

    # Label length
    for n in spec.nodes:
        if len(n.label) > 40:
            errors.append(f"Node label too long: '{n.label[:20]}...'")
    for e in spec.edges:
        if e.label and len(e.label) > 25:
            errors.append(f"Edge label too long: '{e.label[:15]}...'")

    return errors


# ── Test fixtures ───────────────────────────────────────────────────

def _make_node(id: str, label: str = "", **kw) -> GraphNode:
    return GraphNode(id=id, label=label or id, type="service", **kw)


def _make_edge(from_id: str, to_id: str, **kw) -> GraphEdge:
    return GraphEdge(**{"from": from_id, "to": to_id, "type": "http", **kw})


# ── Tests ───────────────────────────────────────────────────────────

def test_valid_diagram():
    spec = DiagramSpec(
        diagram_type="system_architecture",
        title="Test",
        nodes=[_make_node("a"), _make_node("b")],
        edges=[_make_edge("a", "b")],
    )
    assert len(spec.nodes) == 2
    assert validate_diagram_limits(spec) == []


def test_edge_references_invalid_node():
    with pytest.raises(ValidationError, match="not in nodes"):
        DiagramSpec(
            diagram_type="system_architecture",
            title="Bad",
            nodes=[_make_node("a")],
            edges=[_make_edge("a", "nonexistent")],
        )


def test_empty_group_rejected():
    with pytest.raises(ValidationError, match="no members"):
        DiagramSpec(
            diagram_type="system_architecture",
            title="Bad",
            nodes=[_make_node("a"), _make_node("b")],
            edges=[_make_edge("a", "b")],
            groups=[GraphGroup(id="empty_group", label="Empty")],
        )


def test_too_many_nodes():
    nodes = [_make_node(f"n{i}") for i in range(15)]
    edges = [_make_edge(f"n{i}", f"n{i+1}") for i in range(14)]
    spec = DiagramSpec(
        diagram_type="system_architecture",
        title="Overloaded",
        nodes=nodes,
        edges=edges,
    )
    errs = validate_diagram_limits(spec)
    assert any("Too many nodes" in e for e in errs)


def test_orphan_nodes_detected():
    spec = DiagramSpec(
        diagram_type="system_architecture",
        title="Orphans",
        nodes=[_make_node("a"), _make_node("b"), _make_node("c"), _make_node("d")],
        edges=[_make_edge("a", "b")],
    )
    errs = validate_diagram_limits(spec)
    assert any("orphan" in e.lower() for e in errs)


def test_label_length_check():
    spec = DiagramSpec(
        diagram_type="system_architecture",
        title="Long",
        nodes=[
            _make_node("a", label="A" * 50),
            _make_node("b"),
        ],
        edges=[_make_edge("a", "b")],
    )
    errs = validate_diagram_limits(spec)
    assert any("label too long" in e for e in errs)


def test_invalid_node_type():
    with pytest.raises(ValidationError):
        GraphNode(id="x", label="x", type="banana")  # type: ignore


def test_invalid_edge_type():
    with pytest.raises(ValidationError):
        GraphEdge(**{"from": "a", "to": "b", "type": "teleport"})  # type: ignore


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
