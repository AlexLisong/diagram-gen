"""
POC 5: End-to-end pipeline.
Demonstrates the full flow:
  Input JSON → Validate → Render Mermaid → Export HTML/SVG

This is the integration test for the entire diagram generation system.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "..")

from models import CanonicalGraph, DiagramSpec, GraphEdge, GraphGroup, GraphNode

# Add parent POC dirs to path
sys.path.insert(0, str(Path(__file__).parent.parent / "poc2_mermaid_renderer"))
sys.path.insert(0, str(Path(__file__).parent.parent / "poc4_svg_export"))

from renderer import render_mermaid
from exporter import export_to_html_preview, export_via_mmdc

# ── Node limits per diagram type ────────────────────────────────────

NODE_LIMITS: dict[str, tuple[int, int]] = {
    "system_architecture": (2, 9),
    "request_flow": (2, 8),
    "module_structure": (2, 12),
    "cloud_resource": (2, 10),
}


def validate_spec(spec: DiagramSpec) -> list[str]:
    """Business-rule validation beyond Pydantic schema."""
    errors: list[str] = []
    lo, hi = NODE_LIMITS.get(spec.diagram_type, (2, 12))
    if not (lo <= len(spec.nodes) <= hi):
        errors.append(f"Node count {len(spec.nodes)} outside [{lo}, {hi}]")

    ids = [n.id for n in spec.nodes]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate node IDs")

    connected = set()
    for e in spec.edges:
        connected.add(e.from_id)
        connected.add(e.to_id)
    orphans = set(ids) - connected
    if len(orphans) > 1:
        errors.append(f"Orphan nodes: {orphans}")

    return errors


def select_view(
    graph: CanonicalGraph,
    diagram_type: str,
    max_nodes: int = 8,
) -> DiagramSpec:
    """
    Select a subset of the canonical graph for one slide.
    In production, this would be an LLM call.
    """
    # Simple strategy: take first max_nodes nodes
    nodes = graph.nodes[:max_nodes]
    node_ids = {n.id for n in nodes}

    edges = [e for e in graph.edges if e.from_id in node_ids and e.to_id in node_ids]
    groups = [g for g in graph.groups if any(n.group == g.id for n in nodes)]

    return DiagramSpec(
        diagram_type=diagram_type,  # type: ignore
        title=graph.title,
        direction=graph.direction,
        nodes=nodes,
        edges=edges,
        groups=groups,
    )


def run_pipeline(input_json: dict, output_dir: str) -> dict:
    """Run the full pipeline and return results."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results: dict = {"steps": []}

    # Step 1: Parse CanonicalGraph
    try:
        graph = CanonicalGraph(**input_json)
        results["steps"].append({"step": "parse", "status": "ok", "nodes": len(graph.nodes)})
    except Exception as e:
        results["steps"].append({"step": "parse", "status": "error", "error": str(e)})
        return results

    # Step 2: Select view
    spec = select_view(graph, graph.diagram_type)
    results["steps"].append({"step": "select_view", "status": "ok", "nodes": len(spec.nodes)})

    # Step 3: Validate
    errors = validate_spec(spec)
    if errors:
        results["steps"].append({"step": "validate", "status": "warning", "errors": errors})
    else:
        results["steps"].append({"step": "validate", "status": "ok"})

    # Step 4: Render Mermaid
    mermaid = render_mermaid(spec)
    mmd_path = out / "diagram.mmd"
    mmd_path.write_text(mermaid)
    results["steps"].append({"step": "render_mermaid", "status": "ok", "path": str(mmd_path)})

    # Step 5: Export HTML
    html_path = out / "diagram.html"
    export_to_html_preview(mermaid, str(html_path))
    results["steps"].append({"step": "export_html", "status": "ok", "path": str(html_path)})

    # Step 6: Export SVG (optional)
    svg_path = out / "diagram.svg"
    svg_ok = export_via_mmdc(mermaid, str(svg_path))
    results["steps"].append({
        "step": "export_svg",
        "status": "ok" if svg_ok else "skipped (mmdc not installed)",
    })

    # Save spec JSON for reference
    spec_path = out / "spec.json"
    spec_path.write_text(json.dumps(spec.model_dump(by_alias=True), indent=2))

    results["mermaid"] = mermaid
    return results


# ── Test scenarios ──────────────────────────────────────────────────

SCENARIO_1_TAPP = {
    "title": "Tapp AI Copilot Architecture",
    "diagram_type": "system_architecture",
    "direction": "LR",
    "nodes": [
        {"id": "user", "label": "User", "type": "user", "group": "client"},
        {"id": "frontend", "label": "React Frontend", "type": "frontend", "group": "client",
         "metadata": {"tech": ["React", "TypeScript", "CopilotKit"]}},
        {"id": "api", "label": "C# Backend", "type": "api", "group": "backend",
         "metadata": {"tech": [".NET", "ABP"]}},
        {"id": "ai", "label": "Python AI Service", "type": "ai_service", "group": "backend",
         "metadata": {"tech": ["FastAPI", "LangChain", "OpenAI"]}},
        {"id": "db", "label": "SQL Server", "type": "database", "group": "data"},
        {"id": "pdf", "label": "PDF Generator", "type": "service", "group": "backend"},
    ],
    "edges": [
        {"from": "user", "to": "frontend", "label": "Browser", "type": "http"},
        {"from": "frontend", "to": "api", "label": "REST", "type": "http"},
        {"from": "api", "to": "ai", "label": "AI Request", "type": "internal_http"},
        {"from": "ai", "to": "frontend", "label": "SSE", "type": "stream"},
        {"from": "api", "to": "db", "label": "SQL", "type": "reads"},
        {"from": "api", "to": "pdf", "label": "Generate", "type": "calls"},
    ],
    "groups": [
        {"id": "client", "label": "Client Layer"},
        {"id": "backend", "label": "Backend Layer"},
        {"id": "data", "label": "Data Layer"},
    ],
}

SCENARIO_2_REQUEST_FLOW = {
    "title": "AI Chat Request Flow",
    "diagram_type": "request_flow",
    "direction": "LR",
    "nodes": [
        {"id": "react", "label": "React UI", "type": "frontend"},
        {"id": "copilot", "label": "CopilotKit", "type": "frontend"},
        {"id": "csharp", "label": "C# API", "type": "api"},
        {"id": "python", "label": "Python Agent", "type": "ai_service"},
        {"id": "openai", "label": "OpenAI GPT-4", "type": "external_api"},
    ],
    "edges": [
        {"from": "react", "to": "copilot", "label": "Action", "type": "calls"},
        {"from": "copilot", "to": "csharp", "label": "HTTP", "type": "http"},
        {"from": "csharp", "to": "python", "label": "Forward", "type": "internal_http"},
        {"from": "python", "to": "openai", "label": "LLM Call", "type": "http"},
        {"from": "python", "to": "csharp", "label": "Events", "type": "stream"},
        {"from": "csharp", "to": "react", "label": "SSE", "type": "stream"},
    ],
}

SCENARIO_3_LIGHTHOUSE = {
    "title": "Lighthouse Market Insight Engine",
    "diagram_type": "system_architecture",
    "direction": "TB",
    "nodes": [
        {"id": "ibkr", "label": "Interactive Brokers", "type": "external_api", "group": "external"},
        {"id": "fetcher", "label": "Data Fetcher", "type": "service", "group": "pipeline"},
        {"id": "pg", "label": "PostgreSQL", "type": "database", "group": "data"},
        {"id": "engine", "label": "Trendline Engine", "type": "ai_service", "group": "pipeline"},
        {"id": "backend", "label": "C# Backend", "type": "api", "group": "app"},
        {"id": "frontend", "label": "Next.js Frontend", "type": "frontend", "group": "app"},
    ],
    "edges": [
        {"from": "ibkr", "to": "fetcher", "label": "Market Data", "type": "http"},
        {"from": "fetcher", "to": "pg", "label": "Store", "type": "writes"},
        {"from": "pg", "to": "engine", "label": "Read", "type": "reads"},
        {"from": "engine", "to": "backend", "label": "Analysis", "type": "internal_http"},
        {"from": "backend", "to": "frontend", "label": "REST", "type": "http"},
    ],
    "groups": [
        {"id": "external", "label": "External"},
        {"id": "pipeline", "label": "Data Pipeline"},
        {"id": "data", "label": "Storage"},
        {"id": "app", "label": "Application"},
    ],
}


if __name__ == "__main__":
    scenarios = {
        "tapp_architecture": SCENARIO_1_TAPP,
        "request_flow": SCENARIO_2_REQUEST_FLOW,
        "lighthouse": SCENARIO_3_LIGHTHOUSE,
    }

    for name, scenario in scenarios.items():
        print(f"\n{'='*60}")
        print(f"  Scenario: {name}")
        print(f"{'='*60}")

        out_dir = str(Path(__file__).parent / "output" / name)
        results = run_pipeline(scenario, out_dir)

        for step in results["steps"]:
            status = step["status"]
            icon = "✓" if status == "ok" else "⚠" if "warning" in status else "○"
            print(f"  {icon} {step['step']}: {status}")

        if "mermaid" in results:
            print(f"\n  --- Mermaid Output ---")
            print("  " + results["mermaid"].replace("\n", "\n  "))
