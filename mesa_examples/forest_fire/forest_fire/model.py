import mesa
from mesa.datacollection import DataCollector

from .agent import Tree
from .agent import Condition


class Forest(mesa.Model):
    """
    The model class holds the model-level attributes, manages the agents, and generally handles
    the global level of our model.

    There is only one model-level parameter: how many agents the model contains. When a new model
    is started, we want it to populate itself with the given number of agents.

    The scheduler is a special model component which controls the order in which agents are activated.
    """

    def __init__(self, width, height, density=0.65, seed=None):
        super().__init__()

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(width=width, height=height, torus=False)

        for _, pos in self.grid.coord_iter():
            if self.random.random() <= density:
                tree = Tree(self.next_id(), self)
                self.schedule.add(tree)
                self.grid.place_agent(tree, pos)

        self.datacollector = DataCollector(
            {
                str(Condition.FINE): lambda m: self.condition_count(m, Condition.FINE),
                str(Condition.ON_FIRE): lambda m: self.condition_count(m, Condition.ON_FIRE),
                str(Condition.BURNED_OUT): lambda m: self.condition_count(m, Condition.BURNED_OUT),
            }
        )

        self.running = True
        self.datacollector.collect(self)

        self.spark_fire()

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.schedule.step()

        if self.condition_count(self, Condition.ON_FIRE) == 0:
            self.running = False

        self.datacollector.collect(self)

    def spark_fire(self):
        count = self.schedule.get_agent_count()
        start = self.random.randint(1, count)
        self.schedule._agents[start].condition = Condition.ON_FIRE

    @staticmethod
    def condition_count(model, condition: Condition):
        return sum(tree.condition == condition for tree in model.schedule.agents)
