from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sim import model  # TODO(m-jeu): Check whether these imports make sense.

import mesa


class Car(mesa.Agent):
    """Vroom vroom."""

    def __init__(self, m: model.World) -> None:
        super().__init__(m.next_id(), m)
        # Add speed and other attributes here.

    def step(self) -> None:
        """Apply logic (like perceive) and stage changes for the next tick."""
        raise NotImplementedError()

    def advance(self) -> None:
        """Actually apply changes staged by Car.step()."""
        raise NotImplementedError()

    def perceive(self) -> None:
        """Perceive the environment, in front of the car."""
        raise NotImplementedError()

    def act(self) -> None:
        """Apply the information from perceive, and take an action according to it."""
        raise NotImplementedError()
