from __future__ import annotations

import mesa
import mesa.time
import mesa.space
import numpy as np

from ..sim import agent  # TODO(m-jeu): Check whether these imports make sense.


class World(mesa.Model):
    """A world, in which vehicles move according to the Nagel-Schreckenberg Model.

    Currently represents one lane of traffic, might be expanded in the future.

    Attributes:
        schedule: mesa scheduler that activates the correct agent methods to run the simulation.
        grid: the grid (currently 1D) that agents are placed on.
        max_velocity: maximum speed cars are allowed to travel at."""

    def __init__(self, width: int,
                 amount_of_agents: int,
                 max_velocity: int) -> None:
        """Initialize class instance, and it's agents.

        Args:
            width: width of the lane.
            amount_of_agents: amount of Car agents to place on the grid.
            max_velocity: max_velocity attribute.

        Raises:
            ValueError if amount_of_agents exceeds width."""
        super().__init__()

        # Initialize world parameters
        self.schedule: mesa.time.SimultaneousActivation = mesa.time.SimultaneousActivation(self)
        self.grid: mesa.space.SingleGrid = mesa.space.SingleGrid(width, 1, torus=True)
        self.max_velocity: int = max_velocity

        # Initialize agents
        if amount_of_agents > width:
            raise ValueError(f"Amount of agents {amount_of_agents} may not exceed world width {width}.")

        agent_locations: np.ndarray = np.linspace(0, width, amount_of_agents, endpoint=False).astype(int)

        for loc in agent_locations:
            a: agent.Car = agent.Car(self, p_brake=0.05)
            self.schedule.add(a)
            self.grid.place_agent(a, (loc, 0))

    def step(self) -> None:
        """Continue the simulation by one tick."""
        self.schedule.step()

    def visualize(self) -> None:
        raise NotImplementedError()
