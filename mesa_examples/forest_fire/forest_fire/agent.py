from enum import StrEnum

import mesa
from mesa.space import Position


class Condition(StrEnum):
    FINE = "Fine"
    ON_FIRE = "On Fire"
    BURNED_OUT = "Burned Out"


class Tree(mesa.Agent):  # noqa
    """
    An agent
    """

    def __init__(self, unique_id, model):
        """
        Customize the agent
        """
        super().__init__(unique_id, model)
        self.condition = Condition.FINE

    def step(self):
        """
        Modify this method to change what an individual agent will do during each step.
        Can include logic based on neighbors states.
        """
        if self.condition == Condition.ON_FIRE:
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.condition == Condition.FINE:
                    neighbor.condition = Condition.ON_FIRE
            self.condition = Condition.BURNED_OUT
