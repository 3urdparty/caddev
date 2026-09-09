"""CAD project definition and build orchestration."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Callable

from .rpc import RpcClient
from .serialize import serialize_shape


BuildFunction = Callable[[], Any]


@dataclass
class Component:
    id: str
    module: str
    factory: str = "build"
    name: str | None = None

    def load_factory(self) -> BuildFunction:
        module = importlib.import_module(self.module)
        factory = getattr(module, self.factory)

        if not callable(factory):
            raise TypeError(
                f"{self.module}.{self.factory} is not callable"
            )

        return factory

    def build(self):
        return self.load_factory()()

@dataclass
class Project:
    components: list[Component] = field(default_factory=list)

    def build_component(
        self,
        component: Component,
        client: RpcClient,
    ) -> None:
        shape = component.build()

        payload = serialize_shape(
            shape,
            component_id=component.id,
            name=component.name,
        )

        client.call(
            "component.update",
            **payload,
        )

    def build_all(self, client: RpcClient) -> None:
        for component in self.components:
            self.build_component(component, client)
