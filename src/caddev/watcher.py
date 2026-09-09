"""Watch a build123d project for source changes."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from watchfiles import watch


ChangeHandler = Callable[[set[Path]], None]


def watch_project(
    root: Path,
    on_change: ChangeHandler,
) -> None:
    root = root.resolve()

    for changes in watch(
        root,
        debounce=300,
    ):
        paths = {
            Path(path).resolve()
            for _, path in changes
            if path.endswith(".py")
        }

        if paths:
            on_change(paths)
