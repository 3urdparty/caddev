"""caddev command-line interface."""

from __future__ import annotations

import os
os.environ["FONTCONFIG_FILE"] = "/path/to/caddev/fontconfig/fonts.conf"
import argparse
from pathlib import Path

from .commands.build import build
from .commands.dev import dev
from .commands.init import init_project
from .commands.status import status
from .loader import load_project


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="caddev",
        description="Development tools for build123d + FreeCAD projects.",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "dev",
        help="Start the CAD development server.",
    )

    subparsers.add_parser(
        "build",
        help="Build and sync the CAD project once.",
    )

    subparsers.add_parser(
        "status",
        help="Show caddev and FreeCAD bridge status.",
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Create a new CAD project.",
    )

    init_parser.add_argument(
        "name",
        help="Project directory name.",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    # `caddev` without a subcommand behaves like `caddev dev`.
    command = args.command or "dev"

    match command:
        case "init":
            init_project(
                Path(args.name),
                project_name=args.name,
            )

        case "dev":
            root = Path.cwd()
            project = load_project(root)
            dev(root, project)

        case "build":
            root = Path.cwd()
            project = load_project(root)
            build(root, project)

        case "status":
            root = Path.cwd()
            project = load_project(root)
            status(root, project)

        case _:
            parser.error(f"unknown command: {command}")


if __name__ == "__main__":
    main()
