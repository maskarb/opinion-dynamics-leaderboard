from mesa import Model
from mesa.datacollection import DataCollector
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
            ag = DemandAgent(i, self, "opinion_od")
            self.schedule.add(ag)
        self.datacollector = DataCollector(
            agent_reporters={"Opinion": "opinion_od", "New Opinion": "opinion_new", "Rank": "rank", "Score": "score"}
        )
        self.datacollector.collect(self)  # collect the initial values

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()  # calculate the OD opinion
        for agent in self.schedule.agents:
            agent.opinion_od = (
                agent.opinion_staged
            )  # after all OD opinions are calculated, replace old opinion with the staged opinion
            agent.update_decision()  # update the decision
        ranked_agents = sorted(self.schedule.agents, reverse=True)  # sort all the agents
        for i, agent in enumerate(ranked_agents):
            agent.rank = i  # give each agent it's rank
            agent.calculate_score()  # calculate the agent's score based on its rank
        convert_opinion(ranked_agents)  # calculate the new-opinion based on leaderboard dynamics
        self.datacollector.collect(self)  # collect all the agent attributes for this step
