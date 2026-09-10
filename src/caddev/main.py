"""caddev command-line interface."""

from __future__ import annotations

import os
from pathlib import Path
os.environ["FONTCONFIG_FILE"] = "/path/to/caddev/fontconfig/fonts.conf"
from .commands.dev import dev

def configure_fontconfig() -> None:
    config_dir = (
        Path(__file__).resolve().parent
        / "fontconfig"
    )

    os.environ["FONTCONFIG_FILE"] = str(
        config_dir / "fonts.conf"
    )

    os.environ["FONTCONFIG_PATH"] = str(
        config_dir
    )

configure_fontconfig()

import argparse
from pathlib import Path
from .commands.add import add_part
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

    add_parser = subparsers.add_parser(
        "add",
        help="Add an item to the CAD project.",
    )

    add_subparsers = add_parser.add_subparsers(
        dest="add_type",
        required=True,
    )

    add_part_parser = add_subparsers.add_parser(
        "part",
        help="Add a new part.",
    )

    add_part_parser.add_argument(
        "name",
        help="Part name.",
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

        case "add":
            root = Path.cwd()

            match args.add_type:
                case "part":
                    add_part(
                        root,
                        name=args.name,
                    )

        case _:
            parser.error(f"unknown command: {command}")


if __name__ == "__main__":
    main()
