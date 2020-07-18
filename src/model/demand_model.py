from mesa import Model
from mesa.time import RandomActivation

from leaderboard.model import convert_opinion
from model.demand_agent import DemandAgent
from utils.config import Config


class DemandModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, scenario, config_dikt, seed=None):
        assert N >= 10
        super().__init__(seed)
        self.config = Config(config_dikt)
        self.global_broadcast = 1
        self.scenario = scenario
        self.schedule = RandomActivation(self)
        self.n_agents = N
        for i in range(self.n_agents):
            ag = DemandAgent(i, self, "od_opinion")
            self.schedule.add(ag)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        for agent in self.schedule.agents:
            agent.update_decision()
        ranked_agents = sorted(self.schedule.agents, reverse=True)
        for i, agent in enumerate(ranked_agents):
            agent.rank.append(i)
        # self.give_agents_rank(ranked_agents)
        convert_opinion(ranked_agents, self.schedule.time)

    def opinion_rank(self, agent):
        return agent.od_opinion[self.schedule.time]

    def give_agents_rank(self, ranked_agents):
        self.current_opinion = 0
        self.current_rank = 0
        for i, agent in enumerate(ranked_agents):
            if agent.od_opinion[self.schedule.time] < self.current_opinion:
                self.current_rank = i

            self.current_opinion = agent.od_opinion[self.schedule.time]
            agent.rank.append(self.current_rank)
