from __future__ import annotations


import mesa
import mesa.time
import mesa.space
import numpy as np

import agent


class World(mesa.Model):
    """A world, in which vehicles move.

    Whether this is a lane, or a road, is yet to be determined."""

    def __init__(self, width: int,
                 amount_of_agents: int) -> None:
        """Initialize class instance."""
        super().__init__()

        # Initialize world parameters
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa.space.SingleGrid(width, 1, torus=True)

        # Initialize agents
        if amount_of_agents > width:
            raise ValueError(f"Amount of agents {amount_of_agents} may not exceed world width {width}.")

        agent_locations: np.ndarray = np.linspace(0, width, amount_of_agents, endpoint=False).astype(int)

        for loc in agent_locations:
            a = agent.Car(self)
            self.grid.place_agent(a, (loc, 0))


    def step(self) -> None:
        raise NotImplementedError()
