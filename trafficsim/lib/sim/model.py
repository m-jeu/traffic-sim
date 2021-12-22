from __future__ import annotations


import mesa
import mesa.time
import mesa.space
import mesa.datacollection
import mesa.batchrunner
import numpy as np
import pandas as pd


from ..sim import agent


class World(mesa.Model):
    """A world, in which vehicles move according to the Nagel-Schreckenberg Model.

    Currently represents one lane of traffic, might be expanded in the future.

    Attributes:
        schedule: mesa scheduler that activates the correct agent methods to run the simulation.
        grid: the grid (currently 1D) that agents are placed on.
        max_velocity: maximum speed cars are allowed to travel at.
        data_collector:
            mesa data collector that keeps track of both agent level and model level variables."""

    def __init__(self, width: int,
                 density: float,
                 max_velocity: int,
                 p_brake: float,
                 car_cls: type = agent.Car) -> None:
        """Initialize class instance, and it's agents.

        Args:
            width: width of the lane.
            density: density of cars per grid cell.
            max_velocity: max_velocity attribute.
            p_brake: TODO(m-jeu)
            car_cls: TODO(m-jeu)

        Raises:
            ValueError if amount_of_agents exceeds width."""
        super().__init__()

        amount_of_agents: int = round(density * width)

        # Initialize world parameters
        self.schedule: mesa.time.SimultaneousActivation = mesa.time.SimultaneousActivation(self)
        self.grid: mesa.space.SingleGrid = mesa.space.SingleGrid(width, 1, torus=True)
        self.max_velocity: int = max_velocity

        # Initialize agents
        if amount_of_agents > width:
            raise ValueError(f"Amount of agents {amount_of_agents} may not exceed world width {width}.")

        agent_locations: np.ndarray = np.linspace(0, width, amount_of_agents, endpoint=False).astype(int)

        for loc in agent_locations:
            a: agent.Car = car_cls(self, p_brake=p_brake)
            self.schedule.add(a)
            self.grid.place_agent(a, (loc, 0))

        # Initialize data collector
        self.data_collector: mesa.datacollection.DataCollector = mesa.datacollection.DataCollector(
            agent_reporters={
                "Velocity": "velocity"  # Keep track of velocity on agent-level.
            },
            model_reporters={
                # Keep track of average velocity over all agents per timestep on model-level.
                "Average velocity": World.average_agent_velocity
            }
        )

    def step(self) -> None:
        """Continue the simulation by one tick."""
        self.data_collector.collect(self)
        self.schedule.step()

    def visualize(self) -> None:
        raise NotImplementedError()

    def average_agent_velocity(self) -> float:
        return sum([agent.velocity for agent in self.schedule.agents]) / len(self.schedule.agents)

    @classmethod
    def experiment(cls,
                   p_brake_permutations: int = 10,
                   width: int = 50,
                   max_velocity: int = 5):  # TODO(m-jeu): Make modular.
        batch_runner: mesa.batchrunner.BatchRunner = mesa.batchrunner.BatchRunner(
            cls,
            variable_parameters={
                "density": np.linspace(0, 1, width)[1:],  # Density of 0 cars per cell causes problems.
                "p_brake": np.linspace(0, 1, p_brake_permutations)
            },
            fixed_parameters={
                "width": width,
                "max_velocity": max_velocity
            },
            iterations=1,
            max_steps=10,
            model_reporters={
                "Average Velocity": lambda m: m.data_collector.get_model_vars_dataframe()["Average velocity"]
            }
        )

        batch_runner.run_all()

        return batch_runner.get_model_vars_dataframe()


