"""
Unified pipeline — generates all 10 diagram types as images.

Usage:
    python generate_all.py              # generate all
    python generate_all.py sequence     # generate one by name
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from schemas.graph_schema import DiagramSpec
from schemas.sequence_schema import SequenceSpec, SequenceStep, SequenceGroup
from schemas.comparison_schema import ComparisonSpec
from renderers.mermaid_renderer import render_mermaid
from renderers.plantuml_renderer import render_plantuml_sequence
from renderers.comparison_renderer import render_comparison_html
from exporters.image_exporter import export_mermaid_png, export_plantuml_png, export_html_to_png

from scenarios.all_scenarios import (
    SYSTEM_CONTEXT,
    HIGH_LEVEL_ARCHITECTURE,
    REQUEST_FLOW,
    SEQUENCE_AI_STREAMING,
    DATA_FLOW,
    MODULE_STRUCTURE,
    DEPLOYMENT,
    DECISION_FLOW,
    VERIFICATION_FLOW,
    BEFORE_AFTER,
)

OUTPUT_DIR = Path(__file__).parent / "output"

# ── Diagram type → renderer mapping ─────────────────────────────────

GRAPH_BASED = {
    "01_system_context": SYSTEM_CONTEXT,
    "02_architecture": HIGH_LEVEL_ARCHITECTURE,
    "03_request_flow": REQUEST_FLOW,
    "05_data_flow": DATA_FLOW,
    "06_module_structure": MODULE_STRUCTURE,
    "07_deployment": DEPLOYMENT,
    "08_decision_flow": DECISION_FLOW,
    "09_verification_flow": VERIFICATION_FLOW,
}


def generate_graph_diagram(name: str, data: dict) -> dict:
    """Generate a Mermaid-based diagram."""
    out_dir = OUTPUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = DiagramSpec(**data)
    mermaid = render_mermaid(spec)

    # Write artifacts
    (out_dir / "diagram.mmd").write_text(mermaid)
    (out_dir / "spec.json").write_text(
        json.dumps(spec.model_dump(by_alias=True), indent=2)
    )

    # Export PNG
    png_ok = export_mermaid_png(mermaid, str(out_dir / "diagram.png"))

    return {
        "name": name,
        "type": "mermaid",
        "title": spec.title,
        "nodes": len(spec.nodes),
        "edges": len(spec.edges),
        "png": png_ok,
        "mermaid_preview": mermaid[:200],
    }


def generate_sequence_diagram(name: str, data: dict) -> dict:
    """Generate a PlantUML sequence diagram."""
    out_dir = OUTPUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Parse steps — discriminate between SequenceStep and SequenceGroup
    parsed_steps = []
    for s in data.get("steps", []):
        if "steps" in s:
            parsed_steps.append(SequenceGroup(**s))
        else:
            parsed_steps.append(SequenceStep(**s))

    spec = SequenceSpec(
        title=data["title"],
        participants=[
            type(parsed_steps[0]).model_validate(p) if False
            else __import__("schemas.sequence_schema", fromlist=["Participant"]).Participant(**p)
            for p in data["participants"]
        ],
        steps=parsed_steps,
    )

    puml = render_plantuml_sequence(spec)

    (out_dir / "diagram.puml").write_text(puml)
    (out_dir / "spec.json").write_text(
        json.dumps(data, indent=2)
    )

    # Also generate a Mermaid sequence as fallback
    mermaid_seq = _sequence_to_mermaid(spec)
    (out_dir / "diagram.mmd").write_text(mermaid_seq)

    # Try PlantUML first, fall back to Mermaid
    png_ok = export_plantuml_png(puml, str(out_dir / "diagram.png"))
    if not png_ok:
        png_ok = export_mermaid_png(mermaid_seq, str(out_dir / "diagram.png"))

    return {
        "name": name,
        "type": "plantuml+mermaid",
        "title": spec.title,
        "participants": len(spec.participants),
        "steps": len(spec.steps),
        "png": png_ok,
    }


def _sequence_to_mermaid(spec: SequenceSpec) -> str:
    """Convert SequenceSpec to Mermaid sequenceDiagram (fallback renderer)."""
    lines = ["sequenceDiagram"]
    for p in spec.participants:
        if p.type == "actor":
            lines.append(f"  actor {p.id} as {p.label}")
        else:
            lines.append(f"  participant {p.id} as {p.label}")
    lines.append("")
    for step in spec.steps:
        if isinstance(step, SequenceGroup):
            lines.append(f"  {step.type} {step.label}")
            for s in step.steps:
                _add_mermaid_step(lines, s)
            if step.else_label:
                lines.append(f"  else {step.else_label}")
                for s in step.else_steps:
                    _add_mermaid_step(lines, s)
            lines.append("  end")
        else:
            _add_mermaid_step(lines, step)
    return "\n".join(lines)


def _add_mermaid_step(lines: list[str], step: SequenceStep) -> None:
    arrow = "-->>" if step.style == "dashed" else "->>"
    if step.is_return:
        arrow = "--)" if step.style == "dashed" else "-)"
    if step.from_id == step.to_id:
        lines.append(f"  {step.from_id} ->> {step.to_id}: {step.message}")
    else:
        lines.append(f"  {step.from_id} {arrow} {step.to_id}: {step.message}")
    if step.activate:
        lines.append(f"  activate {step.to_id}")
    if step.note:
        lines.append(f"  note right of {step.to_id}: {step.note}")
    if step.deactivate:
        # Deactivate the sender for return messages, receiver otherwise
        target = step.from_id if step.is_return else step.from_id
        lines.append(f"  deactivate {target}")


def generate_comparison(name: str, data: dict) -> dict:
    """Generate a before/after comparison HTML + PNG."""
    out_dir = OUTPUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = ComparisonSpec(**data)
    html = render_comparison_html(spec)

    (out_dir / "diagram.html").write_text(html)
    (out_dir / "spec.json").write_text(
        json.dumps(data, indent=2)
    )

    png_ok = export_html_to_png(html, str(out_dir / "diagram.png"))

    return {
        "name": name,
        "type": "html",
        "title": spec.title,
        "left_items": len(spec.left.items),
        "right_items": len(spec.right.items),
        "png": png_ok,
    }


def main(filter_name: str | None = None) -> None:
    results = []

    # Graph-based diagrams (Mermaid)
    for name, data in GRAPH_BASED.items():
        if filter_name and filter_name not in name:
            continue
        print(f"\n{'─'*50}")
        print(f"  Generating: {name}")
        print(f"{'─'*50}")
        r = generate_graph_diagram(name, data)
        icon = "✓" if r["png"] else "○"
        print(f"  {icon} {r['title']} ({r['nodes']} nodes, {r['edges']} edges)")
        results.append(r)

    # Sequence diagram (PlantUML + Mermaid fallback)
    name = "04_sequence"
    if not filter_name or filter_name in name:
        print(f"\n{'─'*50}")
        print(f"  Generating: {name}")
        print(f"{'─'*50}")
        r = generate_sequence_diagram(name, SEQUENCE_AI_STREAMING)
        icon = "✓" if r["png"] else "○"
        print(f"  {icon} {r['title']} ({r['participants']} participants, {r['steps']} steps)")
        results.append(r)

    # Before/After comparison (HTML)
    name = "10_before_after"
    if not filter_name or filter_name in name:
        print(f"\n{'─'*50}")
        print(f"  Generating: {name}")
        print(f"{'─'*50}")
        r = generate_comparison(name, BEFORE_AFTER)
        icon = "✓" if r["png"] else "○"
        print(f"  {icon} {r['title']}")
        results.append(r)

    # Summary
    print(f"\n{'='*50}")
    print(f"  SUMMARY: {len(results)} diagrams generated")
    print(f"{'='*50}")
    for r in results:
        icon = "✓" if r.get("png") else "○"
        print(f"  {icon} [{r['type']:>15}] {r['name']}")
    print(f"\n  Output: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None
    main(name_filter)
