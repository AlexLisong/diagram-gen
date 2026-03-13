from __future__ import annotations

from schemas.comparison_schema import ComparisonColumn, ComparisonDiagramSpec


def build_before_after() -> ComparisonDiagramSpec:
    return ComparisonDiagramSpec(
        title="Manual vs Agentic Video Prep",
        left=ComparisonColumn(
            title="Before",
            items=[
                "Read repo manually",
                "Draft slides from scratch",
                "Rewrite facts across docs and script",
            ],
        ),
        right=ComparisonColumn(
            title="After",
            items=[
                "Ingest repo, docs, and cloud snapshot",
                "Generate diagram-backed slide draft",
                "Verify claims before export",
            ],
        ),
        notes=[
            "This renderer is HTML-first so it can be screenshotted into slides.",
        ],
        source_refs=["synthetic:before_after"],
    )
