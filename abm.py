import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pprint
from mesa.space import MultiGrid
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

### load some owned plot functions
from plot_functions import plot_colormap, plot_agents, plot_mean_std


class DemandAgent(Agent):
    """An agent with initial opinion."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.opinion = [0]
        self.decision = [np.random.randint(0, 2)] #[0]
        self.a = np.random.randint(0, 2, size=self.model.n_agents)
        self.b = np.random.randint(0, 2, size=self.model.n_agents)
        self.threshold = np.random.uniform(0.3, 0.9) # 0.9
        self.rank = [0]

    def update_decision(self):
        # self.decision = 1
        # print('opinion', self.opinion, 'threshold', self.threshold)
        # print('O[-1]', self.opinion[-1])

        ## Basset formulation:
        # if self.opinion[-1] >= self.threshold:
        #     self.decision.append(1)
        # else:
        #     self.decision.append(0)

        ## Du formulation
        if self.decision[-1] == 0 and self.opinion[-1] < self.threshold:
            self.decision.append(0)
        else:
            self.decision.append(1)

    def update_opinion(self):
        gb = self.model.global_broadcast # 0 or 1
        u_j = np.random.randint(0, 2)

        # Opinion from global_broadcast + social media:
        if self.model.scenario == 1:
            O_j = self.opinion[self.model.schedule.time]
            op_gb = (O_j + u_j * gb) / (1 + u_j)
            self.opinion.append(op_gb)

        # Opinion from global_broadcast + social media:
        elif self.model.scenario == 2:
            sum_aijOi = self.a[self.unique_id] * self.opinion[self.model.schedule.time] # 0
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_aijOi += self.a[agent.unique_id] * agent.opinion[self.model.schedule.time]
            op_gb_sm = (sum_aijOi + u_j * gb) / (sum(self.a) + u_j)
            self.opinion.append(op_gb_sm)

        # Opinion from global_broadcast + neighbors:
        elif self.model.scenario == 3:
            O_j = self.opinion[self.model.schedule.time]
            sum_bijXi = self.b[self.unique_id] * self.decision[self.model.schedule.time]
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_bijXi += self.b[agent.unique_id] * agent.decision[self.model.schedule.time]
            op_gb_n = (O_j + sum_bijXi + u_j * gb) / (1 + sum(self.b) + u_j)
            self.opinion.append(op_gb_n)

        # Opinion from global_broadcast + social media + neighbors:
        elif self.model.scenario == 4:
            O_j = self.opinion[self.model.schedule.time]
            sum_aijOi = self.a[self.unique_id] * self.opinion[self.model.schedule.time]
            sum_bijXi = self.b[self.unique_id] * self.decision[self.model.schedule.time]
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_aijOi += self.a[agent.unique_id] * agent.opinion[self.model.schedule.time]
                    sum_bijXi += self.b[agent.unique_id] * agent.decision[self.model.schedule.time]
            op_gb_sm_n = (sum_aijOi + sum_bijXi + u_j * gb) / (sum(self.a) + sum(self.b) + u_j)
            self.opinion.append(op_gb_sm_n)

    def scores(self):
        shower_threshold = 0.75
        laundry_threshold = 0.50
        laundry_points = 75
        irrig_threshold = 0.30
        irrig_points = 50

        # Compare opinion and assign points
        if self.opinion >= shower_threshold:
            shower_points = 100
            self.score += shower_points
        elif self.opinion >= laundry_threshold:
            self.score += laundry_points
        elif self.opinion >= irrig_threshold:
            self.score += irrig_points

    # def response_to_leaderboard(self):
    #     max(agent.opinion[time] for agent in self.model.schedule.agents)

        # aux = self.
        # for agent in self.model.schedule.agents:
        #     if agent.score
        # dmax =


    def step(self):
        self.update_opinion()
        # self.update_decision()
        # self.update_decision()
        # if self.decision[-1] == 1:
        #     self.update_opinion()
        # else:
        #     self.opinion.append(self.opinion[-1])

class DemandModel(Model):
    """A model with some number of agents."""

    def __init__(self, N, scenario):
        super().__init__()
        self.global_broadcast = 1
        self.scenario = scenario
        self.schedule = RandomActivation(self)
        self.n_agents = N
        for i in range(self.n_agents):
            ag = DemandAgent(i, self)
        self.schedule.add(ag)

    def opinion_rank(self, agent):
        return agent.opinion[self.schedule.time]

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        for agent in self.schedule.agents:
            agent.update_decision()
        ranked_agents = sorted(self.schedule.agents, key=self.opinion_rank, reverse=True)
        self.give_agents_rank(ranked_agents)

    def give_agents_rank(self, ranked_agents):
        self.current_opinion = 0
        self.current_rank = 0
        for i, agent in enumerate(ranked_agents):
            if agent.opinion[self.schedule.time] < self.current_opinion:
                self.current_rank = i

            self.current_opinion = agent.opinion[self.schedule.time]
            agent.rank.append(self.current_rank)
    # def step(self):
    #     """Advance the model by one step."""
    #     self.schedule.step()
    #     for agent in self.schedule.agents:
    #         agent.update_decision()

    #     ranked_agents = sorted(self.schedule.agents, key = self.opinion_rank, reverse=True)
    #     for i, agent in enumerate(ranked_agents):
    #         agent.rank.append(i)

def main():
    # for runs in range(0, 1):
    num_agents = 5 # 100
    time_steps = 5 # 30
    scenario = int(sys.argv[-1]) if len(sys.argv) > 1 else 1
    # Run the model
    model = DemandModel(num_agents, scenario)
    for i in range(time_steps):
        model.step()

    # Store the results
    all_opinion = np.zeros(shape=(time_steps+1, num_agents))
    for i, agent in enumerate(model.schedule.agents):
        all_opinion[:, i] = np.array(agent.opinion)
        print('Agent rank', agent.rank, 'Agent opinion', agent.opinion)

    # print the all_opinion array
    pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(all_opinion.T)

    # Plot the opinion of a single agent
    agent_ID = np.random.randint(0, num_agents)
    # plot_agents(all_opinion.T[agent_ID], time_steps, agent_ID)

    # Plot the colormap of all the agents' opiinions
    # plot_colormap(all_opinion.T, num_agents, num_ticks=5)

    # Plot the mean and the std dev of the Opinion
    # plot_mean_std(np.mean(all_opinion, axis = 1), np.std(all_opinion, axis = 1), time_steps)

    # Plot the opinion of all agents
    # print(all_opinion.shape)
    # plot_agents(all_opinion, time_steps)


if __name__ == "__main__":
    main()