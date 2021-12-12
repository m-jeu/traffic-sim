from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

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
                                'amount_of_agents': 5,
                                'max_velocity': 5,
                                'p_break': .05
                            }
                            )
    server.launch(port=8521)
