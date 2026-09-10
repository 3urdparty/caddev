"""Add components to a caddev project."""

from __future__ import annotations

import re
from pathlib import Path

from caddev.log import success


PART_TEMPLATE = '''\
from build123d import Part


def build() -> Part:
    raise NotImplementedError
'''


def add_part(
    root: Path,
    *,
    name: str,
) -> None:
    root = root.resolve()

    project_file = root / "project.py"
    parts_dir = root / "parts"

    if not project_file.exists():
        raise RuntimeError(
            f"no caddev project found in {root}"
        )

    module_name = _snake_case(name)
    display_name = _display_name(module_name)

    part_file = parts_dir / f"{module_name}.py"

    if part_file.exists():
        raise RuntimeError(
            f"part already exists: {part_file}"
        )

    parts_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    part_file.write_text(
        PART_TEMPLATE,
        encoding="utf-8",
    )

    _append_component(
        project_file,
        component_id=module_name,
        name=display_name,
        module=f"parts.{module_name}",
    )

    success(f"Created part: {module_name}")


def _append_component(
    project_file: Path,
    *,
    component_id: str,
    name: str,
    module: str,
) -> None:
    source = project_file.read_text(
        encoding="utf-8"
    )

    marker = "    ]\n)"

    if marker not in source:
        raise RuntimeError(
            "could not locate components list in project.py"
        )

    component = (
        "        Component(\n"
        f'            id="{component_id}",\n'
        f'            name="{name}",\n'
        f'            module="{module}",\n'
        "        ),\n"
    )

    source = source.replace(
        marker,
        component + marker,
        1,
    )

    project_file.write_text(
        source,
        encoding="utf-8",
    )


def _snake_case(value: str) -> str:
    value = re.sub(
        r"(?<!^)(?=[A-Z])",
        "_",
        value,
    )
    value = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        value,
    )

    return value.strip("_").lower()


def _display_name(value: str) -> str:
    return value.replace("_", " ").title()
