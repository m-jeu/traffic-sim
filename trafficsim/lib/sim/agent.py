from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sim import model

import mesa


class Car(mesa.Agent):
    """A Car (agent), which represents a car according to the Nagel-Schreckenberg Model.

    Attributes:
        velocity: The velocity (speed) of the car.
        color: The color of a car in RGB format.
    """

    def __init__(self, m: model.World, p_brake: float) -> None:
        """Initialize class instance.

        Args:
            m: The model/simulation which the car lives in.
            p_brake: The probability of braking without reason.
        """
        super().__init__(m.next_id(), m)

        # Overwrite self.model with proper type World instead of Model for type-hinting.
        self.model: model.World = m

        self.velocity: int = 0  # Speed (cells per step)
        self.p_brake: float = p_brake  # Probability of braking

        # Temporary color (RGB) to distinguish cars in the simulation. ex: (255, 10, 20)
        self.color = tuple([self.model.random.randint(0, 255) for i in range(3)])

    def step(self) -> None:
        """Apply logic (like perceive) and stage changes for the next tick."""
        # 1. Acceleration:
        # Cars not at the maximum velocity have their velocity increased by one unit.
        if self.velocity < self.model.max_velocity:
            self.velocity += 1

        # 2. Slowing down:
        # If the distance is smaller than the velocity, the velocity is reduced to the distance.
        distance = self.perceive()
        if distance is not None and distance < self.velocity:
            self.velocity = distance

        # 3. Randomization:
        # Speed of all cars that have a velocity of at least 1, is now reduced by one unit with a probability of p.
        if self.p_brake >= self.model.random.uniform(0, 1) and self.velocity >= 1:
            self.velocity -= 1

    def advance(self) -> None:
        """Actually apply changes staged by Car.step()."""
        # 4. Car motion:
        # cars are moved forward the number of cells equal to their velocity.
        self_x, self_y = self.pos
        new_x = self_x + self.velocity  # new x is current x + velocity
        self.model.grid.move_agent(self, pos=(new_x, self_y))

    def perceive(self) -> None or int:
        """Perceive the environment, in front of the car."""
        x_self, _ = self.pos
        # Fetch coordinates ahead of the car equal to the car's velocity.
        coords = [(x, 0) for x in range(x_self + 1, x_self + self.velocity + 1)]
        # Transform the coordinates to torus-compliant coordinates and check whether those coordinates are empty.
        position_is_empty = enumerate(map(self.model.grid.is_cell_empty, map(self.model.grid.torus_adj, coords)))
        # Return the distance of the first non-empty cell, or None.
        for dist, is_empty in position_is_empty:
            if not is_empty:
                return dist
        return None

    def act(self) -> None:
        """Apply the information from perceive, and take an action according to it."""
        raise NotImplementedError()
