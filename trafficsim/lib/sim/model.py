from __future__ import annotations


import abc

import mesa
import mesa.time
import mesa.space
import mesa.datacollection
import mesa.batchrunner
import numpy as np
import pandas as pd


from ..sim import agent


class _Road(mesa.Model, metaclass=abc.ABCMeta):
    AGENT_CLASS: type = agent.Car  # Default.  TODO(m-jeu): Is this a bad idea?

    def __init__(self,
                 agents_n: int,
                 lane_length: int,
                 max_velocity: int = 5,
                 p_brake: float = .0) -> None:
        super().__init__()

        self.max_velocity: int = max_velocity
        self.p_brake: float = p_brake
        self.lane_length: int = lane_length

        # TODO(m-jeu): Remove parameters from these methods and access through attributes
        # Initialize attributes specific to subclass.
        self.grid: mesa.space.Grid = self._grid(lane_length)
        self.schedule: mesa.time.BaseScheduler = self._schedule()
        self.CELL_AMOUNT: int = self._cell_amount(lane_length)

        # Initialize agents.
        agent_locations: np.ndarray = self._agent_locations(agents_n)
        for loc in agent_locations:
            a: agent.Car = self.AGENT_CLASS(self, p_brake=p_brake)  # TODO(m-jeu): p_brake passed to car, but max V isn't?
            self.schedule.add(a)
            self.grid.place_agent(a, tuple(loc))

        # Initialize data collector.
        self.data_collector: mesa.datacollection.DataCollector = mesa.datacollection.DataCollector(
            agent_reporters={
                "Velocity": "velocity"  # Keep track of velocity on agent-level.
            },
            model_reporters={
                # Keep track of average velocity over all agents per time step on model-level.
                "Average velocity": self.average_agent_velocity
            }
        )

    @abc.abstractmethod
    def _grid(self, lane_length: int) -> mesa.space.Grid:
        pass

    @abc.abstractmethod
    def _schedule(self) -> mesa.time.BaseScheduler:
        pass

    @abc.abstractmethod
    def _agent_locations(self, amount_of_agents: int) -> np.ndarray:
        pass

    @abc.abstractmethod
    def _cell_amount(self, lane_length: int) -> int:
        pass

    def step(self):
        """Continue the simulation by one tick."""
        self.data_collector.collect(self)
        self.schedule.step()

    def average_agent_velocity(self) -> float:
        return sum([agent.velocity for agent in self.schedule.agents]) / len(self.schedule.agents)


class OneLaneRoad(_Road):
    AGENT_CLASS: type = agent.Car

    def _grid(self, lane_length: int) -> mesa.space.Grid:
        self.grid: mesa.space.SingleGrid = mesa.space.SingleGrid(lane_length, 1, torus=True)
        self._CELL_AMOUNT: int = lane_length

    def _schedule(self) -> mesa.time.BaseScheduler:
        self.schedule: mesa.time.SimultaneousActivation = mesa.time.SimultaneousActivation(self)

    def _agent_locations(self, amount_of_agents: int) -> np.ndarray:
        return np.linspace(
            (0, 0), (self.lane_length, 0), amount_of_agents, endpoint=False
        ).astype(int)

    def _cell_amount(self, lane_length: int) -> int:
        return lane_length


class TwoLaneRoad(_Road):
    AGENT_CLASS: type = agent.TwoLaneCar

    def _grid(self, lane_length: int) -> mesa.space.Grid:
        self.grid: mesa.space.SingleGrid = mesa.space.SingleGrid(lane_length, 2, torus=True)
        self._CELL_AMOUNT: int = lane_length * 2

    def _schedule(self) -> mesa.time.BaseScheduler:
        self.schedule: mesa.time.StagedActivation = mesa.time.StagedActivation(self,
                                                                               ['step_lane_change', 'step', 'advance']
                                                                               )

    def _agent_locations(self, amount_of_agents: int) -> np.ndarray:
        """
        ______________
        |x  x  x  x  |
        |  x  x  x  x|
        ______________
        """
        x_positions_top: np.ndarray = np.linspace(0, self.lane_length, amount_of_agents, endpoint=False).astype(int)

        # Flip x-positions for bottom lane
        x_positions_bot: np.ndarray = (self.lane_length - 1) - x_positions_top

        top = map(lambda x: (x, 0), x_positions_top)
        bottom = map(lambda x: (x, 1), x_positions_bot)

        return np.ndarray(top).append(np.array(bottom))

    def _cell_amount(self, lane_length: int) -> int:
        return lane_length * 2
