"""
Configure visualization elements and instantiate a server
"""
import mesa

from .model import Forest # noqa
from .agent import Condition

HEIGHT = 100
WIDTH = 100

condition_colors = {
    Condition.FINE: "Green",
    Condition.ON_FIRE: "Red",
    Condition.BURNED_OUT: "Black",
}

def circle_portrayal_example(agent):
    if agent is None:
        return

    color = condition_colors[agent.condition]

    return {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "r": 0.5,
        "Color": color,
    }


canvas_element = mesa.visualization.CanvasGrid(
    circle_portrayal_example, WIDTH, HEIGHT, 500, 500
)
chart_element = mesa.visualization.ChartModule(
    [{"Label": label, "Color": color} for (label, color) in condition_colors.items()]
)
pie_chart = mesa.visualization.PieChartModule(
    [{"Label": label, "Color": color} for (label, color) in condition_colors.items()]
)

model_kwargs = {"width": WIDTH, "height": HEIGHT, "density": mesa.visualization.Slider("Tree Density", 0.65, 0.01, 1, 0.01)}

server = mesa.visualization.ModularServer(
    Forest,
    [canvas_element, pie_chart, chart_element],
    "ForestFire",
    model_kwargs,
)
