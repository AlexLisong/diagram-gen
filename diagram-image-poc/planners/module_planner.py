from __future__ import annotations

from extractors.repo_extractor import extract_repo_module_diagram
from schemas.graph_schema import GraphDiagramSpec


def build_module_structure(repo_path: str) -> GraphDiagramSpec:
    return extract_repo_module_diagram(repo_path)
