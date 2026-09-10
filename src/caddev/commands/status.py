from __future__ import annotations

from pathlib import Path

from caddev import Project
from caddev.discovery import connect_freecad
from caddev.loader import load_project
from caddev.log import error, info, success


def status(root: Path, project:Project) -> None:
    root = root.resolve()

    info(f"Project: {root}")


    success(
        f"Project loaded ({len(project.components)} components)"
    )

    client = None

    try:
        client = connect_freecad()

        hello = client.call(
            "bridge.hello",
            rpc_timeout=5.0,
        )

        success("FreeCAD bridge connected")

        freecad_version = hello.get("freecad")
        protocol = hello.get("protocol")

        if freecad_version is not None:
            info(f"FreeCAD: {freecad_version}")

        if protocol is not None:
            info(f"Bridge protocol: {protocol}")

        document = client.call(
            "document.info",
            rpc_timeout=5.0,
        )

        info(
            f"Document: "
            f"{document.get('label') or document.get('name')}"
        )

        remote_components = document.get(
            "components",
            [],
        )

        info(
            f"FreeCAD components: "
            f"{len(remote_components)}"
        )

    except Exception as exc:
        error(f"FreeCAD bridge unavailable: {exc}")

    finally:
        if client is not None:
            client.close()
