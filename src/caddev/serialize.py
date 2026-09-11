from __future__ import annotations

import base64
import io
from typing import Any

from build123d import Location, Part

from .geometry import (
    Appearance,
    ComponentGeometry,
    FeatureGeometry,
    Material,
)


def serialize_component(
    result: Part | ComponentGeometry,
    *,
    component_id: str,
    name: str | None = None,
) -> dict[str, Any]:
    if isinstance(result, Part):
        result = ComponentGeometry.from_shape(
            result
        )

    if not isinstance(
        result,
        ComponentGeometry,
    ):
        raise TypeError(
            "build() must return Part or "
            "ComponentGeometry, "
            f"got {type(result).__name__}"
        )

    return {
        "id": component_id,
        "name": name or component_id,
        "features": {
            feature_id: serialize_feature(
                feature
            )
            for feature_id, feature
            in result.features.items()
        },
        "datums": {
            datum_id: serialize_location(
                location
            )
            for datum_id, location
            in result.datums.items()
        },
    }


def serialize_feature(
    feature: FeatureGeometry,
) -> dict[str, Any]:
    wrapped = getattr(
        feature.shape,
        "wrapped",
        None,
    )

    if wrapped is None:
        raise TypeError(
            "FeatureGeometry.shape must be "
            "a build123d Part"
        )

    brep = shape_to_brep(
        wrapped
    )

    return {
        "name": feature.name,
        "brep64": base64.b64encode(
            brep
        ).decode("ascii"),
        "appearance": (
            serialize_appearance(
                feature.appearance
            )
            if feature.appearance
            else None
        ),
        "location": serialize_location(
            feature.location
        ),
        "material": (
            serialize_material(
                feature.material
            )
            if feature.material
            else None
        ),
    }


def serialize_appearance(
    appearance: Appearance,
) -> dict[str, Any]:
    return {
        "color": (
            list(appearance.color)
            if appearance.color
            else None
        ),
        "transparency": (
            appearance.transparency
        ),
        "shininess": (
            appearance.shininess
        ),
    }


def serialize_material(
    material: Material,
) -> dict[str, Any]:
    return {
        "name": material.name,
        "density": material.density,
        "youngs_modulus": (
            material.youngs_modulus
        ),
        "poisson_ratio": (
            material.poisson_ratio
        ),
        "description": (
            material.description
        ),
    }


def serialize_location(
    location: Location,
) -> dict[str, Any]:
    position, rotation = (
        location.to_tuple()
    )

    return {
        "position": list(position),
        "rotation": list(rotation),
    }


def shape_to_brep(
    shape,
) -> bytes:
    from OCP.BRepTools import BRepTools

    buffer = io.BytesIO()

    BRepTools.Write_s(
        shape,
        buffer,
    )

    return buffer.getvalue()
