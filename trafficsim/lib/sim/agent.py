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
        self.p_breaking: float = p_brake  # probability of braking

    def step(self) -> None:
        """Apply logic (like perceive) and stage changes for the next tick."""

        # 1. Acceleration: Cars not at the maximum velocity have their velocity increased by one unit.
        if self.velocity < self.model.max_velocity:
            self.velocity += 1

        # 3 Speed of all cars that have a velocity of at least 1, is now reduced by one unit with a probability of p.
        if self.p_breaking >= self.model.random.uniform(0, 1):
            self.velocity -= 1

    def advance(self) -> None:
        """Actually apply changes staged by Car.step()."""
        self.model.grid.move_agent(self, (self.pos[0] + self.velocity, self.pos[1]))

    def perceive(self) -> int or None:  # TODO(m-jeu): Untested!
        """Perceive the environment, in front of the car."""
        x_self, _ = self.pos
        coords = [(x, 0) for x in range(x_self + 1, x_self + self.velocity + 1)]
        position_is_empty = enumerate(map(lambda c: self.model.grid.is_cell_empty(c),
                                          map(self.model.grid.torus_adj, coords)))
        for dist, is_empty in position_is_empty:
            if not is_empty:
                return dist
        return None

    def act(self) -> None:
        """Apply the information from perceive, and take an action according to it."""
        raise NotImplementedError()
