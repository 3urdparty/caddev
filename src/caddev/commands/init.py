"""Create a new caddev project."""

from __future__ import annotations

from pathlib import Path


PROJECT_TEMPLATE = '''\
from caddev import Component, Project


project = Project(
    components=[
        Component(
            id="example",
            name="Example Part",
            module="parts.example",
        ),
    ]
)
'''


EXAMPLE_PART_TEMPLATE = '''\
from build123d import Box, Part


def build() -> Part:
    return Box(20, 20, 10)
'''


PYPROJECT_TEMPLATE = '''\
[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "build123d",
    "caddev",
]

[tool.basedpyright]
typeCheckingMode = "standard"

[tool.uv.sources]
# During caddev development, replace this with your local path:
# caddev = {{ path = "../caddev", editable = true }}
'''


GITIGNORE_TEMPLATE = '''\
.venv/
__pycache__/
*.pyc
dist/
build/
'''


PACKAGE_DIRS = (
    "geometry",
    "parts",
    "assemblies",
    "utils",
)


def init_project(
    root: Path,
    *,
    project_name: str,
) -> None:
    root = root.resolve()

    if root.exists() and any(root.iterdir()):
        raise RuntimeError(
            f"directory is not empty: {root}"
        )

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    for directory in PACKAGE_DIRS:
        package = root / directory

        package.mkdir(
            parents=True,
            exist_ok=True,
        )

        (package / "__init__.py").write_text(
            "",
            encoding="utf-8",
        )

    (root / "project.py").write_text(
        PROJECT_TEMPLATE,
        encoding="utf-8",
    )

    (root / "pyproject.toml").write_text(
        PYPROJECT_TEMPLATE.format(
            project_name=project_name,
        ),
        encoding="utf-8",
    )

    (root / ".gitignore").write_text(
        GITIGNORE_TEMPLATE,
        encoding="utf-8",
    )

    (root / "parts" / "example.py").write_text(
        EXAMPLE_PART_TEMPLATE,
        encoding="utf-8",
    )

    print(f"Created CAD project: {root}")
