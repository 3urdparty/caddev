from __future__ import annotations

from dataclasses import dataclass, field

from build123d import Location, Part


@dataclass
class ComponentGeometry:
    shape: Part
    datums: dict[str, Location] = field(
        default_factory=dict
    )
