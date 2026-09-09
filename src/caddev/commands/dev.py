from __future__ import annotations

import traceback
from pathlib import Path

from caddev.discovery import connect_freecad
from caddev.loader import reload_project
from caddev.log import build, error, info, success, warning
from caddev.project import Project
from caddev.rpc import RpcClient
from caddev.watcher import watch_project


def dev(
    root: Path,
    project: Project,
) -> None:
    info(f"caddev running in {root}")

    client: RpcClient | None = None

    try:
        client = connect_freecad()

        _build(
            root,
            client,
            initial=True,
        )

        info("Watching for changes")
        info("Press Ctrl+C to stop")

        def on_change(paths: set[Path]) -> None:
            names = ", ".join(
                str(path.relative_to(root))
                if path.is_relative_to(root)
                else str(path)
                for path in sorted(paths)
            )

            build(f"Change detected: {names}")

            _build(
                root,
                client,
            )

        watch_project(
            root,
            on_change,
        )

    except KeyboardInterrupt:
        print()
        warning("Development server stopped")

    except Exception as exc:
        error(str(exc))
        traceback.print_exc()

    finally:
        if client is not None:
            client.close()


def _build(
    root: Path,
    client: RpcClient,
    *,
    initial: bool = False,
) -> None:
    try:
        build(
            "Initial build"
            if initial
            else "Rebuilding"
        )

        project = reload_project(root)

        project.build_all(client)

        success("Build completed")

    except Exception as exc:
        error(f"Build failed: {exc}")
        traceback.print_exc()
