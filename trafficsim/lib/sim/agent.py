from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import model

import mesa


class Car(mesa.Agent):
    """Vroom vroom."""

    def __init__(self, m: model.World) -> None:
        super().__init__(m.next_id(), m)
        # Add speed and other attributes here.

    def step(self) -> None:
        raise NotImplementedError()

    def advance(self) -> None:
        raise NotImplementedError()

    def perceive(self) -> None:
        raise NotImplementedError()

    def act(self) -> None:
        raise NotImplementedError()
