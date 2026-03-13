from extractors.repo_extractor import extract_repo_module_diagram


def extract_nextjs_module_diagram(repo_path: str):
    return extract_repo_module_diagram(repo_path)


__all__ = ["extract_nextjs_module_diagram", "extract_repo_module_diagram"]
