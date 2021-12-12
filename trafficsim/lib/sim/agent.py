from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sim import model  # TODO(m-jeu): Check whether these imports make sense.

import mesa


class Car(mesa.Agent):
    """Vroom vroom."""

    def __init__(self, m: model.World, p_brake) -> None:
        super().__init__(m.next_id(), m)

        # overwrite self.model with proper type World instead of Model
        self.model: model.World = m

        self.velocity: int = 0  # speed
        self.distance_to_front_car = float('inf')  # distance in cell units to next car
        self.p_breaking: float = p_brake  # probability of braking

    def step(self) -> None:
        """Apply logic (like perceive) and stage changes for the next tick."""
        # 1
        if self.velocity < self.model.max_velocity:
            self.velocity += 1

    def advance(self) -> None:
        """Actually apply changes staged by Car.step()."""
        self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))

    def perceive(self) -> None:
        """Perceive the environment, in front of the car."""
        raise NotImplementedError()

    def act(self) -> None:
        """Apply the information from perceive, and take an action according to it."""
        raise NotImplementedError()
