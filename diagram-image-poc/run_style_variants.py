from __future__ import annotations

import json
from pathlib import Path

from exporters import available_styles, write_style_contact_sheet, write_styled_png
from planners import (
    build_data_flow,
    build_decision_flow,
    build_deployment,
    build_high_level_architecture,
    build_module_structure,
    build_request_flow,
    build_system_context,
    build_verification_flow,
)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def run() -> list[dict[str, object]]:
    root = Path(__file__).parent
    style_dir = root / "outputs" / "style_variants"
    style_dir.mkdir(parents=True, exist_ok=True)

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

    summary: list[dict[str, object]] = []
    for name, spec in graph_specs.items():
        style_paths: dict[str, str] = {}
        for style in available_styles():
            output_path = style_dir / f"{name}--{style}.png"
            write_styled_png(spec, str(output_path), style=style)
            style_paths[style] = str(output_path)
        contact_sheet_path = style_dir / f"{name}--contact-sheet.png"
        write_style_contact_sheet(spec.title, style_paths, str(contact_sheet_path))
        summary.append(
            {
                "name": name,
                "diagram_type": spec.diagram_type,
                "style_variants": style_paths,
                "contact_sheet_path": str(contact_sheet_path),
            }
        )

    _write_text(style_dir / "summary.json", json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    results = run()
    for item in results:
        print(f"name={item['name']} styles={len(item['style_variants'])}")
