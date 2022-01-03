from __future__ import annotations


import abc

import mesa
import mesa.time
import mesa.space
import mesa.datacollection
import mesa.batchrunner
import numpy as np


from ..sim import agent


class _Road(mesa.Model, metaclass=abc.ABCMeta):
    """Abstract road that implements a number of required features for agent-based simulation through mesa,
    models like the Nagel Schreckenberg model and expansions thereof specifically.

    Attributes:
        AGENT_CLASS: (constant class attribute) class of agent associated with road type.
        max_velocity: the maximum velocity in cells per timestep cars are allowed to go.
        p_brake: the probability cars have to randomly lower their velocity by one every timestep.
        lane_length: amount of cells a lane should be in the dimension that's not derermined by the type of road.
        CELL_AMOUNT: Amount of cells on the road (primarily to calculate the density with).
        schedule: """

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
        self.grid = self._grid(lane_length)
        self.schedule = self._schedule()
        self.CELL_AMOUNT: int = self._cell_amount(lane_length)

        # Initialize agents.
        agent_locations: np.ndarray = self._agent_locations(agents_n)

        for loc in agent_locations:
            a: agent.Car = self.AGENT_CLASS(self, p_brake=p_brake)  # TODO(m-jeu): p_brake passed to car, but max V isn't?
            self.schedule.add(a)
            self.grid.place_agent(a, tuple(loc))

        # Initialize data collector.
        self.data_collector: mesa.datacollection.DataCollector = mesa.datacollection.DataCollector(
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
        return mesa.space.SingleGrid(lane_length, 1, torus=True)

    def _schedule(self) -> mesa.time.BaseScheduler:
        return mesa.time.SimultaneousActivation(self)

    def _agent_locations(self, amount_of_agents: int) -> np.ndarray:
        return np.linspace(
            (0, 0), (self.lane_length, 0), amount_of_agents, endpoint=False
        ).astype(int)

    def _cell_amount(self, lane_length: int) -> int:
        return lane_length


class TwoLaneRoad(_Road):
    AGENT_CLASS: type = agent.TwoLaneCar

    def __init__(self,
                 agents_n: int,
                 lane_length: int,
                 max_velocity: int = 5,
                 p_brake: float = .0,
                 p_change: float = 1.0):
        super().__init__(agents_n, lane_length, max_velocity, p_brake)
        self.p_change = p_change

    def _grid(self, lane_length: int) -> mesa.space.Grid:
        return mesa.space.SingleGrid(lane_length, 2, torus=True)

    def _schedule(self) -> mesa.time.BaseScheduler:
        return mesa.time.StagedActivation(self,
                                          ['step_lane_change', 'step', 'advance']
                                          )

    def _agent_locations(self, amount_of_agents: int) -> np.ndarray:
        """
        ______________
        |x  x  x  x  |
        |  x  x  x  x|
        ______________
        """
        n_top = amount_of_agents//2
        n_bot = amount_of_agents - n_top

        x_positions_top: np.ndarray = np.linspace(0, self.lane_length, n_top, endpoint=False).astype(int)
        x_positions_bot: np.ndarray = np.linspace(0, self.lane_length, n_bot, endpoint=False).astype(int) - (
                    self.lane_length - 1)

        # Flip x-positions for bottom lane
        #x_positions_bot: np.ndarray = (self.lane_length - 1) - x_positions_top

        top = map(lambda x: (x, 0), x_positions_top)
        bottom = map(lambda x: (x, 1), x_positions_bot)
        return np.array([*list(top), *list(bottom)])

    def _cell_amount(self, lane_length: int) -> int:
        return lane_length * 2
