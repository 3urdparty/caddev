from __future__ import annotations

from pathlib import Path


def build(root: Path) -> None:
    print(f"Building CAD project: {root}")

    # Later:
    # project = load_project(root)
    # client = connect_freecad()
    # project.build_all(client)
