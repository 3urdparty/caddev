from __future__ import annotations

from typing import Any

from .discovery import get_freecad_client


def highlight(
    component_id: str,
    feature_id: str,
    subelements: list[str],
) -> dict[str, Any]:
    client = get_freecad_client()

    return client.call(
        "debug.highlight",
        component_id=component_id,
        feature_id=feature_id,
        subelements=subelements,
    )
