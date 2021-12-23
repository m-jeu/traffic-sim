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

    def _perceive(self):
        return self._find_car(self.pos, x_dir=1)

    def _find_car(self, pos, x_dir):
        x, y = pos
        x_offset = 0

        while abs(x_offset) <= self.model.grid.width:
            x_offset += x_dir
            if not self.model.grid.is_cell_empty(self.model.grid.torus_adj((x + x_offset, y))):
                break
        return abs(x_offset) - 1

    def _accelerate(self):
        # 1. Acceleration:
        # Cars not at the maximum velocity have their velocity increased by one unit.
        self.velocity = min([self.velocity + 1, self.model.max_velocity])

    def _slow_down(self):
        # 2. Slowing down:
        # If the distance is smaller than the velocity, the velocity is reduced to the distance.
        self.velocity = min([self._perceive(), self.velocity])

    def _random_brake(self):
        # 3. Randomization:
        # Speed of all cars that have a velocity of at least 1, is now reduced by one unit with a probability of p.
        if self.model.random.uniform(0, 1) < self.p_brake:
            self.velocity = max([self.velocity - 1, 0])

    def _car_motion(self):
        # 4. Car motion:
        # cars are moved forward the number of cells equal to their velocity.
        self_x, self_y = self.pos
        new_x = self_x + self.velocity  # new x is current x + velocity
        self.model.grid.move_agent(self, pos=(new_x, self_y))

    def step(self) -> None:
        """Apply logic (like perceive) and stage changes for the next tick."""
        self._accelerate()  # rule 1
        self._slow_down()  # rule 2
        self._random_brake()  # rule 3

    def advance(self) -> None:
        """Actually apply changes staged by Car.step()."""
        self._car_motion()  # rule 4


class AdvancedCar(Car):
    def __init__(self, m: model.World, p_brake: float) -> None:
        """Initialize class instance.

        Args:
            m: The model/simulation which the car lives in.
            p_brake: The probability of braking without reason.
        """
        super().__init__(m, p_brake)

        self.p_change = 1

    def _lane_change_perceive(self):
        x, y = self.pos
        other_lane = 0 if y else 1  # 0 => 1 else 1 => 0
        gap = self._find_car((x, y), x_dir=1)
        gap0 = self._find_car((x, other_lane), x_dir=1)
        gap0back = self._find_car((x, other_lane), x_dir=-1)

        if not self.model.grid.is_cell_empty(self.model.grid.torus_adj((x, other_lane))):
            gap0, gap0back = 0, 0
        return gap, gap0, gap0back

    def safety_rules(self):
        gapl = min([self.velocity + 1, self.model.max_velocity])
        gap0l = gapl
        gap0backl = self.model.max_velocity

        return gapl, gap0l, gap0backl

    def lane_change(self):
        x, y = self.pos
        self.model.grid.move_agent(self, pos=(x, 0 if y else 1))

    def check_safety_rules(self):
        gap, gap0, gap0back = self._lane_change_perceive()
        gapl, gap0l, gap0backl = self.safety_rules()
        return gap < gapl and gap0 > gap0l and gap0back > gap0backl  # rule 1 and 2 and 3

    def step_lane_change(self):
        if self.check_safety_rules() and self.model.random.uniform(0, 1) < self.p_change:
            self.lane_change()
