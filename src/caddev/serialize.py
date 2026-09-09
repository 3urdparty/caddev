"""Serialize build123d shapes for the FreeCAD RPC bridge."""

from __future__ import annotations

import base64
import io
from typing import Any


def serialize_shape(
    shape: Any,
    *,
    component_id: str,
    name: str | None = None,
) -> dict:
    """Convert a build123d shape into an RPC-ready BREP payload."""
    wrapped = getattr(shape, "wrapped", None)

    if wrapped is None:
        raise TypeError(
            f"expected a build123d Shape, got {type(shape).__name__}"
        )

    brep = shape_to_brep(wrapped)

    return {
        "id": component_id,
        "name": name or component_id,
        "brep64": base64.b64encode(brep).decode("ascii"),
    }


def shape_to_brep(shape) -> bytes:
    """Serialize an OCP TopoDS_Shape to textual BREP bytes."""
    from OCP.BRepTools import BRepTools

    buf = io.BytesIO()
    BRepTools.Write_s(shape, buf)
    return buf.getvalue()
