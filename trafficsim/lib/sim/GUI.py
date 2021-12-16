from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from ..sim import model


def agent_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "Filled": "true",
        "Layer": 0,
        "Color": f"rgb{agent.color}",
        "Velocity": f"{agent.velocity}",
        "w": .7,
        "h": .25
    }
    return portrayal


width = 50
cell_size = 15

grid = CanvasGrid(
    portrayal_method=agent_portrayal,
    grid_width=width,
    grid_height=1,
    canvas_width=1100,
    canvas_height=50
)

chart = ChartModule([{"Label": "Average velocity",
                      "Color": "Black"}],
                    data_collector_name='data_collector')


def launch_gui():
    server = ModularServer(
        model.World,
        [grid, chart],
        "Traffic simulation",
        {
            'width': width,
            'density': UserSettableParameter(
                # start value = 1 / (max velocity + 1)
                'slider', 'Density of cars on the road', value=1 / (5 + 1), min_value=0, max_value=1, step=1/width),
            'max_velocity': UserSettableParameter(
                'slider', 'Max velocity', value=5, min_value=1, max_value=25, step=1),
            'p_brake': UserSettableParameter(
                'slider', 'Probability of braking', value=.05, min_value=0, max_value=1, step=.01)
        }
    )
    server.launch(port=8521)
