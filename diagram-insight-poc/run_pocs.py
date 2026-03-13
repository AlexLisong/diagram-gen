from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from renderer import render_graphic, render_preview_html
from scenarios import all_specs


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def run() -> list[dict[str, Any]]:
    root = Path(__file__).parent
    output_dir = root / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict[str, Any]] = []
    for name, spec in all_specs().items():
        svg = render_graphic(spec)
        html = render_preview_html(spec, svg)
        json_payload = json.dumps(spec.model_dump(), indent=2)

        svg_path = output_dir / f"{name}.svg"
        html_path = output_dir / f"{name}.html"
        json_path = output_dir / f"{name}.json"

        _write_text(svg_path, svg)
        _write_text(html_path, html)
        _write_text(json_path, json_payload)

        summary.append(
            {
                "name": name,
                "graphic_type": spec.graphic_type,
                "title": spec.title,
                "svg_path": str(svg_path),
                "html_path": str(html_path),
                "json_path": str(json_path),
                "svg_sha256": _sha256(svg.encode("utf-8")),
                "html_sha256": _sha256(html.encode("utf-8")),
            }
        )

    _write_text(output_dir / "summary.json", json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    results = run()
    for item in results:
        print(f"name={item['name']} type={item['graphic_type']} svg={item['svg_path']}")
