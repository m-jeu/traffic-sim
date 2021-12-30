from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from ..sim import model
import numpy as np


def agent_portrayal(agent):
    """Function defining the way a agent gets portrayed in the simulation"""
    # make a color gradient from red to green with a color for each possible velocity and index the agent's color.
    color = tuple(np.linspace(
        (255, 0, 0), (0, 255, 0), agent.model.max_velocity + 1
    )[agent.velocity])

    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "Color": f"rgb{color}",
        "Velocity": f"{agent.velocity}",
        "w": .7,
        "h": .5
    }
    return portrayal


chart = ChartModule([{"Label": "Average velocity",
                      "Color": "Black"}],
                    data_collector_name='data_collector')


def launch_gui(width=50, multi_lane=False):
    grid_height = 2 if multi_lane else 1
    width = width * 2 if multi_lane else width
    grid = CanvasGrid(
        portrayal_method=agent_portrayal,
        grid_width=width,
        grid_height=grid_height,
        canvas_width=1100,
        canvas_height=40
    )

    params = {
        'lane_length': width,
        'agents_n': UserSettableParameter(
            # start value = 1 / (max velocity + 1)
            'slider', 'Density of cars on the road', value=width//5, min_value=0, max_value=width,
            step=1),
        'max_velocity': UserSettableParameter(
            'slider', 'Max velocity', value=5, min_value=1, max_value=25, step=1),
        'p_brake': UserSettableParameter(
            'slider', 'Probability of braking', value=.05, min_value=0, max_value=1, step=.01
        )
    }

    if multi_lane:
        params['p_change'] = UserSettableParameter(
            'slider', 'Probability of lane-changing', value=1, min_value=0, max_value=1, step=.01
        )

    server = ModularServer(
        model.TwoLaneRoad if multi_lane else model.OneLaneRoad,
        [grid, chart],
        "Traffic simulation",
        model_params=params
    )
    server.launch(port=8521)
