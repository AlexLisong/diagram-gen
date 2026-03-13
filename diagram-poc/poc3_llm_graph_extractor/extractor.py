"""
POC 3: LLM-based graph extraction from repo structure.
Demonstrates: repo scan → raw candidates → LLM normalization → CanonicalGraph.

For this POC we simulate LLM calls with deterministic logic.
Replace _llm_normalize() with actual OpenAI/Claude call in production.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "..")

from models import (
    CanonicalGraph, GraphEdge, GraphGroup, GraphNode,
    RawEdge, RawGraph, RawNode,
)

# ── Step 1: Scan repo structure ─────────────────────────────────────

# Known patterns that hint at service types
TYPE_HINTS: dict[str, str] = {
    "next.config": "frontend",
    "vite.config": "frontend",
    "package.json": "frontend",
    "Program.cs": "api",
    "Startup.cs": "api",
    "appsettings.json": "api",
    "main.py": "service",
    "fastapi": "ai_service",
    "requirements.txt": "service",
    "Dockerfile": "worker",
    "docker-compose": "worker",
}

EDGE_HINTS: dict[str, tuple[str, str]] = {
    "fetch(": ("http", "calls"),
    "axios": ("http", "calls"),
    "HttpClient": ("internal_http", "calls"),
    "SqlConnection": ("reads", "database"),
    "Redis": ("reads", "cache"),
    "SSE": ("stream", "streams to"),
}


def scan_repo(repo_path: str) -> RawGraph:
    """Scan a directory for candidate nodes and edges."""
    root = Path(repo_path)
    if not root.exists():
        raise FileNotFoundError(f"Repo path not found: {repo_path}")

    nodes: list[RawNode] = []
    edges: list[RawEdge] = []
    evidence: list[str] = []

    # Find top-level directories as candidate services
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            raw_type = ""
            for file_hint, stype in TYPE_HINTS.items():
                matches = list(child.rglob(file_hint))
                if matches:
                    raw_type = stype
                    evidence.append(f"Found {file_hint} in {child.name}")
                    break

            nodes.append(RawNode(
                id=child.name,
                label=child.name,
                raw_type=raw_type or "unknown",
                source=str(child),
            ))

    # Simple edge detection from README if exists
    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text()
        if "→" in content or "->" in content:
            evidence.append("Found flow arrows in README")

    return RawGraph(
        candidate_nodes=nodes,
        candidate_edges=edges,
        evidence=evidence,
    )


# ── Step 2: Normalize (simulated LLM) ──────────────────────────────

# In production, this would be an LLM call with constrained output
NORMALIZATION_MAP: dict[str, tuple[str, str]] = {
    "tapp-front": ("React Frontend", "frontend"),
    "tapp-9": ("C# Backend API", "api"),
    "tapp-core-openai-agents": ("Python AI Service", "ai_service"),
    "tapp-print": ("PDF Generator", "service"),
    "evm-dashboard": ("EVM Dashboard", "frontend"),
    "ethoswarm": ("Ethoswarm Web", "frontend"),
    "web-api": ("C# Web API", "api"),
    "evm-copilot-api": ("EVM Copilot API", "ai_service"),
    "light-frontend": ("Lighthouse Frontend", "frontend"),
    "light-backend": ("Lighthouse Backend", "api"),
    "light-trendline-engine": ("Trendline Engine", "ai_service"),
    "light-data-fetcher": ("Data Fetcher", "service"),
}

GROUP_RULES: dict[str, str] = {
    "frontend": "client",
    "user": "client",
    "api": "backend",
    "service": "backend",
    "ai_service": "backend",
    "database": "data",
    "cache": "data",
    "storage": "data",
}


def normalize_graph(raw: RawGraph) -> CanonicalGraph:
    """
    Normalize raw extraction into a CanonicalGraph.
    In production: send raw to LLM with constrained schema output.
    """
    nodes: list[GraphNode] = []
    groups_seen: set[str] = set()

    for rn in raw.candidate_nodes:
        label, node_type = NORMALIZATION_MAP.get(
            rn.id, (rn.label.replace("-", " ").title(), rn.raw_type or "service")
        )
        group = GROUP_RULES.get(node_type, "other")
        groups_seen.add(group)

        nodes.append(GraphNode(
            id=rn.id,
            label=label,
            type=node_type,  # type: ignore
            group=group,
            metadata=rn.metadata,
        ))

    # Auto-generate edges based on common patterns
    edges: list[GraphEdge] = []
    frontend_ids = [n.id for n in nodes if n.type == "frontend"]
    api_ids = [n.id for n in nodes if n.type == "api"]
    ai_ids = [n.id for n in nodes if n.type == "ai_service"]

    for fid in frontend_ids:
        for aid in api_ids:
            edges.append(GraphEdge(**{
                "from": fid, "to": aid, "label": "REST", "type": "http",
            }))
    for aid in api_ids:
        for aiid in ai_ids:
            edges.append(GraphEdge(**{
                "from": aid, "to": aiid, "label": "AI Request", "type": "internal_http",
            }))
    for aiid in ai_ids:
        for fid in frontend_ids:
            edges.append(GraphEdge(**{
                "from": aiid, "to": fid, "label": "SSE", "type": "stream",
            }))

    groups = [
        GraphGroup(id="client", label="Client Layer"),
        GraphGroup(id="backend", label="Backend Layer"),
        GraphGroup(id="data", label="Data Layer"),
    ]
    groups = [g for g in groups if g.id in groups_seen]

    return CanonicalGraph(
        title="Auto-extracted Architecture",
        nodes=nodes,
        edges=edges,
        groups=groups,
        source_refs=[rn.source for rn in raw.candidate_nodes],
    )


# ── Step 3: LLM prompt template for production ─────────────────────

LLM_EXTRACTION_PROMPT = """
You are a software architecture analyst.

Given the following repository structure and file listings, extract the system graph.

## Rules
- Output ONLY valid JSON matching the CanonicalGraph schema
- node.type must be one of: {node_types}
- edge.type must be one of: {edge_types}
- Do NOT invent services that don't exist in the input
- Normalize names to human-readable labels
- Group nodes into: client, backend, data, external
- Maximum {max_nodes} nodes

## Input
{repo_structure}

## Output Schema
{schema}
"""


def build_llm_prompt(repo_structure: str, max_nodes: int = 8) -> str:
    """Build the prompt for production LLM extraction."""
    from models import CanonicalGraph
    return LLM_EXTRACTION_PROMPT.format(
        node_types=", ".join(GraphNode.model_fields["type"].annotation.__args__),
        edge_types=", ".join(GraphEdge.model_fields["type"].annotation.__args__),
        max_nodes=max_nodes,
        repo_structure=repo_structure,
        schema=CanonicalGraph.model_json_schema(),
    )


# ── Demo ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulate scanning a repo-like directory
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create fake repo structure
        for name in ["tapp-front", "tapp-9", "tapp-core-openai-agents"]:
            d = Path(tmpdir) / name
            d.mkdir()
            if "front" in name:
                (d / "package.json").write_text("{}")
                (d / "vite.config.ts").write_text("")
            elif "9" in name:
                (d / "Program.cs").write_text("")
                (d / "appsettings.json").write_text("{}")
            else:
                (d / "main.py").write_text("")
                (d / "requirements.txt").write_text("fastapi\nopenai\n")

        # Run pipeline
        print("=== Step 1: Scan ===")
        raw = scan_repo(tmpdir)
        print(f"Found {len(raw.candidate_nodes)} candidates")
        for n in raw.candidate_nodes:
            print(f"  {n.id}: {n.raw_type}")
        print(f"Evidence: {raw.evidence}")

        print("\n=== Step 2: Normalize ===")
        graph = normalize_graph(raw)
        print(f"Title: {graph.title}")
        print(f"Nodes: {len(graph.nodes)}")
        for n in graph.nodes:
            print(f"  [{n.type}] {n.id} → {n.label} (group: {n.group})")
        print(f"Edges: {len(graph.edges)}")
        for e in graph.edges:
            print(f"  {e.from_id} --{e.label}--> {e.to_id}")

        print("\n=== LLM Prompt Template ===")
        prompt = build_llm_prompt("tapp-front/\ntapp-9/\ntapp-core-openai-agents/")
        print(prompt[:500] + "...")

        # Export
        output = graph.model_dump(by_alias=True)
        print("\n=== Canonical Graph JSON ===")
        print(json.dumps(output, indent=2)[:800] + "...")
