"""Renderers — convert specs into diagram DSL strings or HTML."""

from renderers.mermaid_renderer import render_mermaid
from renderers.plantuml_renderer import render_plantuml_sequence
from renderers.comparison_renderer import render_comparison_html

__all__ = ["render_mermaid", "render_plantuml_sequence", "render_comparison_html"]
