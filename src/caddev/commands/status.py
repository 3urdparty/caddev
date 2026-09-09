from __future__ import annotations

from pathlib import Path


def status(root: Path) -> None:
    print(f"Project: {root}")

    # Later:
    # detect project.py
    # discover FreeCAD bridge
    # call bridge.hello
    # show bridge/version/document information
