from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from exporters import png_bytes, svg_string, write_png, write_svg
from planners import (
    build_before_after,
    build_data_flow,
    build_decision_flow,
    build_deployment,
    build_high_level_architecture,
    build_module_structure,
    build_request_flow,
    build_sequence_diagram,
    build_system_context,
    build_verification_flow,
)
from renderers import comparison_html, mermaid_string, plantuml_string
from schemas import ComparisonDiagramSpec, GraphDiagramSpec, SequenceDiagramSpec


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_text(path, json.dumps(payload, indent=2))


def _render_mermaid_with_cli(input_path: Path, output_path: Path) -> bool:
    mmdc_path = shutil.which("mmdc")
    if not mmdc_path:
        return False

    config_path = Path(__file__).parent / "renderers" / "puppeteer-config.json"
    result = subprocess.run(
        [
            mmdc_path,
            "-p",
            str(config_path),
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-b",
            "transparent",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and output_path.exists()


def _graph_artifacts(name: str, spec: GraphDiagramSpec, output_dir: Path) -> dict[str, object]:
    mermaid_payload = mermaid_string(spec).encode("utf-8")
    mermaid_payload_again = mermaid_string(spec).encode("utf-8")
    svg_payload = svg_string(spec).encode("utf-8")
    svg_payload_again = svg_string(spec).encode("utf-8")
    png_payload = png_bytes(spec)
    png_payload_again = png_bytes(spec)

    mmd_path = output_dir / f"{name}.mmd"
    svg_path = output_dir / f"{name}.svg"
    png_path = output_dir / f"{name}.png"
    json_path = output_dir / f"{name}.json"
    mermaid_svg_path = output_dir / f"{name}.mermaid.svg"
    _write_text(mmd_path, mermaid_payload.decode("utf-8"))
    write_svg(spec, str(svg_path))
    write_png(spec, str(png_path))
    _write_json(json_path, spec.model_dump(by_alias=True))
    mermaid_cli_rendered = _render_mermaid_with_cli(mmd_path, mermaid_svg_path)

    summary: dict[str, object] = {
        "name": name,
        "diagram_type": spec.diagram_type,
        "renderer": "mermaid",
        "json_path": str(json_path),
        "dsl_path": str(mmd_path),
        "svg_path": str(svg_path),
        "png_path": str(png_path),
        "node_count": len(spec.nodes),
        "edge_count": len(spec.edges),
        "dsl_sha256": _sha256(mermaid_payload),
        "svg_sha256": _sha256(svg_payload),
        "png_sha256": _sha256(png_payload),
        "dsl_deterministic": mermaid_payload == mermaid_payload_again,
        "svg_deterministic": svg_payload == svg_payload_again,
        "png_deterministic": png_payload == png_payload_again,
        "mermaid_cli_rendered": mermaid_cli_rendered,
    }
    if mermaid_cli_rendered:
        summary["mermaid_svg_path"] = str(mermaid_svg_path)
    return summary


def _sequence_artifacts(name: str, spec: SequenceDiagramSpec, output_dir: Path) -> dict[str, object]:
    plantuml_payload = plantuml_string(spec).encode("utf-8")
    plantuml_payload_again = plantuml_string(spec).encode("utf-8")

    puml_path = output_dir / f"{name}.puml"
    json_path = output_dir / f"{name}.json"

    _write_text(puml_path, plantuml_payload.decode("utf-8"))
    _write_json(json_path, spec.model_dump(by_alias=True))

    return {
        "name": name,
        "diagram_type": spec.diagram_type,
        "renderer": "plantuml",
        "json_path": str(json_path),
        "dsl_path": str(puml_path),
        "participant_count": len(spec.participants),
        "step_count": len(spec.steps),
        "dsl_sha256": _sha256(plantuml_payload),
        "dsl_deterministic": plantuml_payload == plantuml_payload_again,
    }


def _comparison_artifacts(name: str, spec: ComparisonDiagramSpec, output_dir: Path) -> dict[str, object]:
    html_payload = comparison_html(spec).encode("utf-8")
    html_payload_again = comparison_html(spec).encode("utf-8")

    html_path = output_dir / f"{name}.html"
    json_path = output_dir / f"{name}.json"

    _write_text(html_path, html_payload.decode("utf-8"))
    _write_json(json_path, spec.model_dump())

    return {
        "name": name,
        "diagram_type": spec.diagram_type,
        "renderer": "html_template",
        "json_path": str(json_path),
        "dsl_path": str(html_path),
        "column_count": 2,
        "dsl_sha256": _sha256(html_payload),
        "dsl_deterministic": html_payload == html_payload_again,
    }


def run() -> list[dict[str, object]]:
    root = Path(__file__).parent
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)

    graph_specs = {
        "system_context": build_system_context(),
        "high_level_architecture": build_high_level_architecture(),
        "request_flow": build_request_flow(),
        "module_structure": build_module_structure(str(root)),
        "decision_flow": build_decision_flow(),
        "verification_flow": build_verification_flow(),
        "data_flow": build_data_flow(),
        "deployment": build_deployment(),
    }
    sequence_specs = {"streaming_sequence": build_sequence_diagram()}
    comparison_specs = {"manual_vs_agentic": build_before_after()}

    summary: list[dict[str, object]] = []
    for name, spec in graph_specs.items():
        summary.append(_graph_artifacts(name, spec, output_dir))
    for name, spec in sequence_specs.items():
        summary.append(_sequence_artifacts(name, spec, output_dir))
    for name, spec in comparison_specs.items():
        summary.append(_comparison_artifacts(name, spec, output_dir))

    _write_text(output_dir / "summary.json", json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    results = run()
    for item in results:
        details = [f"name={item['name']}", f"renderer={item['renderer']}"]
        if "node_count" in item:
            details.append(f"nodes={item['node_count']}")
        if "participant_count" in item:
            details.append(f"participants={item['participant_count']}")
        details.append(f"dsl_deterministic={item['dsl_deterministic']}")
        print(" ".join(details))
