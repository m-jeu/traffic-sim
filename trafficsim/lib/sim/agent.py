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

    def _perceive(self):
        return self._find_car(self.pos, x_dir=1)

    def _find_car(self, pos, x_dir):
        """Function to calculate the gap of a certain position (pos) to the first car in a certain direction (x_dir)"""
        x, y = pos
        x_offset = 0
        while abs(x_offset) <= self.model.grid.width:
            x_offset += x_dir  # add direction to the total offset distance
            # check if the cell at the offset is not empty
            if not self.model.grid.is_cell_empty(self.model.grid.torus_adj((x + x_offset, y))):
                break
        # distance to the other car's cell - 1 is the gap
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


class TwoLaneCar(Car):
    """A Car (agent), which represents a car according to the RNSL model, capable of lane-changing in a 2 lane world.
    """
    def __init__(self, m: model.World, p_brake: float, p_change=1) -> None:
        """Initialize class instance.

        Args:
            m: The model/simulation which the car lives in.
            p_brake: The probability of braking without reason.
            p_change: The probability of lane-changing given the safety-rules allow it.
        """
        super().__init__(m, p_brake)

        self.p_change = p_change

    def _lane_change_perceive(self):
        """
        Get the perceptions needed to decide if a lane-change is possible.

        Returns:
            gap, gap0 and gap0back representing the distance of the gap in front of the car, in front of the car on the
            other lane and behind the car on the other lane.
        """
        x, y = self.pos
        other_lane = 0 if y else 1  # get index of other lane: current lane is 0 then 1 else 0
        gap = self._perceive()  # get gap in front
        # check if there are cars adjacent on the other lane
        if not self.model.grid.is_cell_empty(self.model.grid.torus_adj((x, other_lane))):
            # if there are cars the gap0's are 0
            gap0, gap0back = 0, 0
        # else find the actual gap
        else:
            gap0 = self._find_car((x, other_lane), x_dir=1)
            gap0back = self._find_car((x, other_lane), x_dir=-1)

        return gap, gap0, gap0back

    def safety_rules(self):
        """Function to return values regarding the safety rules of a lane change."""
        gapl = min([self.velocity + 1, self.model.max_velocity])
        gap0l = gapl
        gap0backl = self.model.max_velocity
        return gapl, gap0l, gap0backl

    def lane_change(self):
        x, y = self.pos
        self.model.grid.move_agent(self, pos=(x, 0 if y else 1))  # move the agent to the other lane

    def check_safety_rules(self):
        """Function the check if the safety-rules are all True to consider if a lane-change is possible
           Returns:
               True if a lane-change is safe.
               False if a lane-change is not safe."""

        gap, gap0, gap0back = self._lane_change_perceive()  # get gaps
        gapl, gap0l, gap0backl = self.safety_rules()  # get safety rules for gaps
        return gap < gapl and gap0 > gap0l and gap0back > gap0backl  # rule 1 and 2 and 3

    def step_lane_change(self):
        # if the rules are safe and lane switch probability
        if self.check_safety_rules() and self.model.random.uniform(0, 1) < self.p_change:
            self.lane_change()
