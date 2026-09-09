from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path

from .project import Project


IGNORED_ROOT_DIRS = {
    ".venv",
    "venv",
    ".git",
    ".cache",
    "__pycache__",
    "build",
    "dist",
}


def unload_project_modules(root: Path) -> None:
    root = root.resolve()

    for name, module in list(sys.modules.items()):
        file = getattr(module, "__file__", None)

        if file is None:
            continue

        try:
            module_path = Path(file).resolve()
            relative = module_path.relative_to(root)
        except (OSError, RuntimeError, ValueError):
            continue

        if relative.parts and relative.parts[0] in IGNORED_ROOT_DIRS:
            continue

        sys.modules.pop(name, None)

    importlib.invalidate_caches()


def load_project(root: Path) -> Project:
    root = root.resolve()
    path = root / "project.py"

    if not path.exists():
        raise RuntimeError(
            f"no project.py found in {root}"
        )

    root_str = str(root)

    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    spec = importlib.util.spec_from_file_location(
        "caddev_user_project",
        path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            f"could not load project file: {path}"
        )

    module = importlib.util.module_from_spec(spec)
    sys.modules["caddev_user_project"] = module
    spec.loader.exec_module(module)

    project = getattr(module, "project", None)

    if not isinstance(project, Project):
        raise RuntimeError(
            "project.py must define `project = Project(...)`"
        )

    return project


def reload_project(root: Path) -> Project:
    unload_project_modules(root)
    return load_project(root)
