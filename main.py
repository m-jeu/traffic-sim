import trafficsim
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}
    return portrayal

grid = CanvasGrid(agent_portrayal, 10, 1, 500, 500)

server = ModularServer(trafficsim.World,
                       [grid],
                       "Traffic simulation",
                       {'width':10, 'amount_of_agents':5, 'max_speed':5})

server.port = 8521
server.launch()