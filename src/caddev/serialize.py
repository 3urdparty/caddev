from __future__ import annotations

import base64
import io
from typing import Any
from build123d import Location, Part
from .geometry import ComponentGeometry


def serialize_component(
    result: Part | ComponentGeometry,
    *,
    component_id: str,
    name: str | None = None,
) -> dict:
    if isinstance(result, ComponentGeometry):
        shape = result.shape
        datums = result.datums
    elif isinstance(result, Part):
        shape = result
        datums = {}
    else:
        raise TypeError(
            "build() must return Part or ComponentGeometry, "
            f"got {type(result).__name__}"
        )

    wrapped = getattr(shape, "wrapped", None)

    if wrapped is None:
        raise TypeError(
            f"expected build123d Part, "
            f"got {type(shape).__name__}"
        )

    brep = shape_to_brep(wrapped)

    return {
        "id": component_id,
        "name": name or component_id,
        "brep64": base64.b64encode(
            brep
        ).decode("ascii"),
        "datums": {
            datum_id: serialize_location(location)
            for datum_id, location in datums.items()
        },
    }


def serialize_location(
    location: Location,
) -> dict:
    position, rotation = location.to_tuple()

    return {
        "position": list(position),
        "rotation": list(rotation),
    }


def shape_to_brep(shape) -> bytes:
    from OCP.BRepTools import BRepTools

    buf = io.BytesIO()
    BRepTools.Write_s(shape, buf)

    return buf.getvalue()

