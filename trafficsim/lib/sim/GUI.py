from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from ..sim import model


def agent_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "Color": f"rgb{agent.color}",
        "w": 1,
        "h": 1
    }
    return portrayal


width = 50
cell_size = 15

grid = CanvasGrid(
    portrayal_method=agent_portrayal,
    grid_width=width,
    grid_height=1,
    canvas_width=width * cell_size,
    canvas_height=cell_size
)


def launch_gui():
    server = ModularServer(
                            model.World,
                            [grid],
                            "Traffic simulation",
                            {
                                'width': width,
                                'amount_of_agents': UserSettableParameter(
                                    'slider', 'N agents', value=5, min_value=1, max_value=width, step=1),
                                'max_velocity': UserSettableParameter(
                                    'slider', 'Max velocity', value=5, min_value=1, max_value=25, step=1),
                                'p_brake': UserSettableParameter(
                                    'slider', 'Probability braking', value=.05, min_value=0, max_value=1, step=.01)
                            }
                            )
    server.launch(port=8521)


