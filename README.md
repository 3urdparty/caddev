<h1 align="center">caddev</h1>

<p align="center">
  <strong>Define parts in build123d. Assemble them in FreeCAD.</strong>
</p>

<p align="center">
  A development client for the Code Workbench bridge that keeps Python-authored
  parts as separate, native FreeCAD components.
</p>

`caddev` connects a normal Python development environment to the Code Workbench
running inside FreeCAD. Each component is built independently with
[build123d](https://github.com/gumyr/build123d), serialized as exact BREP geometry,
and sent to FreeCAD over a local RPC connection.

This separation gives each tool a clear responsibility:

- **build123d defines part geometry** in regular Python modules.
- **caddev watches, rebuilds, and synchronizes** those parts during development.
- **FreeCAD maintains components, placements, and assemblies** and provides the
  rest of the native CAD workflow.

Because components are updated by stable IDs, changing one Python part does not
flatten the project into a single compound or discard its placement in the FreeCAD
assembly.

## Why caddev?

- **Parts remain separate.** Every declared component is transferred and updated
  independently in the FreeCAD document.
- **Assemblies stay in FreeCAD.** Position and constrain components with FreeCAD's
  assembly tools while build123d remains focused on geometry.
- **Use your own editor.** Work in VS Code, Neovim, PyCharm, or any other Python
  environment and see saved changes appear in FreeCAD.
- **Keep the runtimes isolated.** build123d and OCP run in the client environment;
  FreeCAD does not need to import their Python bindings.
- **Transfer exact geometry.** Shapes cross the process boundary as OpenCASCADE
  BREP data rather than meshes.
- **Organize real projects.** Split reusable geometry, parts, assemblies, and
  utilities into ordinary Python packages.

## How it works

```text
Python development environment                 FreeCAD process
┌──────────────────────────────┐                ┌───────────────────────────┐
│ caddev                       │   JSON-RPC     │ Code Workbench bridge     │
│                              │ over localhost│                           │
│ project.py                   │ ─────────────► │ Native components         │
│ parts/*.py                   │  BREP + JSON   │ Placements and assemblies │
│ build123d + OCP              │                │ FreeCAD document          │
└──────────────────────────────┘                └───────────────────────────┘
```

The Code Workbench bridge publishes a small discovery file containing its local
address, protocol version, and session token. `caddev` uses it to establish an
authenticated JSON-RPC 2.0 connection, then sends a `component.update` request for
each part. Only serialized geometry and component metadata cross the boundary.

On Linux and macOS, the discovery file is read from:

```text
${XDG_CACHE_HOME:-~/.cache}/codecad/bridge.json
```

On Windows it is read from `%LOCALAPPDATA%\codecad\bridge.json`.

## Requirements

- Python 3.11 or later
- [build123d](https://github.com/gumyr/build123d)
- FreeCAD with the Code Workbench bridge installed and running
- [`uv`](https://docs.astral.sh/uv/) is recommended for project environments

`caddev` uses your project's Python environment. It does not download or manage
Python, build123d, OCP, or FreeCAD on your behalf.

## Install

This project is currently under development and is not yet published as a stable
package. Clone it and install it into a virtual environment:

```console
git clone <caddev-repository-url>
cd caddev
uv sync
```

To make the command available in another local project, add an editable source:

```console
uv add --editable /path/to/caddev
```

The equivalent `pip` command is:

```console
python -m pip install -e /path/to/caddev
```

## Quick start

### 1. Create a project

```console
caddev init my-cad-project
cd my-cad-project
```

Because `caddev` is not published yet, point the generated `pyproject.toml` at your
clone before installing the project environment:

```toml
[tool.uv.sources]
caddev = { path = "/path/to/caddev", editable = true }
```

Then install the environment:

```console
uv sync
```

The generated project starts with this structure:

```text
my-cad-project/
├── project.py
├── pyproject.toml
├── assemblies/
├── geometry/
├── parts/
│   └── example.py
└── utils/
```

### 2. Define a part

Each part module exposes a zero-argument build function that returns a build123d
shape:

```python
# parts/bracket.py
from build123d import Box, Cylinder, Part


def build() -> Part:
    plate = Box(60, 40, 6)
    hole = Cylinder(3, 6)
    return plate - hole
```

### 3. Register the component

Declare the parts that belong to the project in `project.py`:

```python
from caddev import Component, Project


project = Project(
    components=[
        Component(
            id="bracket",
            name="Mounting Bracket",
            module="parts.bracket",
        ),
    ]
)
```

`id` is the stable identity used to update the corresponding FreeCAD component.
`name` is its display name. By default, `caddev` calls `build()`; use the `factory`
field if the module exposes a differently named function.

### 4. Start FreeCAD and caddev

Start FreeCAD, activate Code Workbench, and ensure its RPC bridge is running. Then,
from the project directory, run:

```console
caddev dev
```

Running `caddev` without a subcommand does the same thing. The client connects to
the bridge, performs an initial build, and watches Python files for changes. Saving
a file rebuilds the project and updates its components in FreeCAD.

Now use FreeCAD to place the components and build the assembly. Subsequent geometry
updates keep each component's stable identity so the document can retain the
assembly-level state managed by FreeCAD.

## Component factories

A project can contain as many independently updated components as needed:

```python
from caddev import Component, Project


project = Project(
    components=[
        Component(id="base", name="Base Plate", module="parts.base"),
        Component(id="shaft", name="Drive Shaft", module="parts.shaft"),
        Component(
            id="cover",
            name="Upper Cover",
            module="parts.cover",
            factory="make_cover",
        ),
    ]
)
```

Factories currently take no arguments and must return an object with a build123d
`wrapped` shape. Parameters can still live in ordinary Python modules, dataclasses,
or other project code and be imported by the factory.

## Commands

| Command | Description | Status |
|---|---|---|
| `caddev` / `caddev dev` | Connect, build all components, and watch `.py` files | Available |
| `caddev init NAME` | Scaffold a new project | Available |
| `caddev build` | Build and synchronize once | Planned; command is currently a placeholder |
| `caddev status` | Report project and bridge status | Planned; command is currently a placeholder |

## Development

Install the repository environment with `uv`:

```console
uv sync
```

Run the included example while developing `caddev` itself:

```console
cd examples/example_project
uv sync
uv run caddev dev
```

The repository is organized around the client-side responsibilities:

```text
src/caddev/
├── commands/       CLI commands
├── discovery.py    FreeCAD bridge discovery and connection
├── loader.py       Project loading and module reloading
├── project.py      Project and component definitions
├── rpc.py          Newline-delimited JSON-RPC client
├── serialize.py    build123d/OCP to BREP serialization
└── watcher.py      Python source file watching
```

## Status

`caddev 0.1` is an early development release. The core live workflow—bridge
discovery, authenticated RPC connection, build123d shape serialization, independent
component updates, project reloading, and source watching—is implemented. The
one-shot `build` and diagnostic `status` commands are not implemented yet, and the
client and Code Workbench bridge must use the same protocol version.

## Security

CAD projects are Python programs and run with your user privileges. Only build
projects you trust. The RPC bridge listens on localhost and uses a per-session token,
but it should still be treated as a local development interface rather than a
network service.

## License

No license has been declared in this repository yet.
