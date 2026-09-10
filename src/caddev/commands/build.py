from __future__ import annotations

import traceback
from pathlib import Path

from caddev import Project
from caddev.discovery import connect_freecad
from caddev.loader import load_project
from caddev.log import build as log_build
from caddev.log import error, success


def build(root: Path, project:Project) -> None:
    root = root.resolve()

    client = None

    try:
        log_build(f"Building CAD project: {root}")

        client = connect_freecad()

        project.build_all(client)

        success("Build completed")

    except Exception as exc:
        error(f"Build failed: {exc}")
        traceback.print_exc()
        raise SystemExit(1) from exc

    finally:
        if client is not None:
            client.close()
