import numpy as np

from mesa import Agent


class DemandAgent(Agent):
    """An agent with initial opinion."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.od_opinion = [0]
        self.decision = [np.random.randint(0, 2)]  # [0]
        self.a = np.random.randint(0, 2, size=self.model.n_agents)
        self.b = np.random.randint(0, 2, size=self.model.n_agents)
        self.threshold = np.random.uniform(0.3, 0.9)  # 0.9
        self.rank = [0]

    def update_decision(self):
        # self.decision = 1
        # print('opinion', self.od_opinion, 'threshold', self.threshold)
        # print('O[-1]', self.od_opinion[-1])

        # Basset formulation:
        # if self.od_opinion[-1] >= self.threshold:
        #     self.decision.append(1)
        # else:
        #     self.decision.append(0)

        # Du formulation
        if self.decision[-1] == 0 and self.od_opinion[-1] < self.threshold:
            self.decision.append(0)
        else:
            self.decision.append(1)

    def update_opinion(self):  # noqa: C901
        gb = self.model.global_broadcast  # 0 or 1
        u_j = np.random.randint(0, 2)

        # Opinion from global_broadcast + social media:
        if self.model.scenario == 1:
            O_j = self.od_opinion[self.model.schedule.time]
            op_gb = (O_j + u_j * gb) / (1 + u_j)
            self.od_opinion.append(op_gb)

        # Opinion from global_broadcast + social media:
        elif self.model.scenario == 2:
            sum_aijOi = self.a[self.unique_id] * self.od_opinion[self.model.schedule.time]  # 0
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_aijOi += self.a[agent.unique_id] * agent.opinion[self.model.schedule.time]
            op_gb_sm = (sum_aijOi + u_j * gb) / (sum(self.a) + u_j)
            self.od_opinion.append(op_gb_sm)

        # Opinion from global_broadcast + neighbors:
        elif self.model.scenario == 3:
            O_j = self.od_opinion[self.model.schedule.time]
            sum_bijXi = self.b[self.unique_id] * self.decision[self.model.schedule.time]
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_bijXi += self.b[agent.unique_id] * agent.decision[self.model.schedule.time]
            op_gb_n = (O_j + sum_bijXi + u_j * gb) / (1 + sum(self.b) + u_j)
            self.od_opinion.append(op_gb_n)

        # Opinion from global_broadcast + social media + neighbors:
        elif self.model.scenario == 4:
            O_j = self.od_opinion[self.model.schedule.time]
            sum_aijOi = self.a[self.unique_id] * self.od_opinion[self.model.schedule.time]
            sum_bijXi = self.b[self.unique_id] * self.decision[self.model.schedule.time]
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_aijOi += self.a[agent.unique_id] * agent.opinion[self.model.schedule.time]
                    sum_bijXi += self.b[agent.unique_id] * agent.decision[self.model.schedule.time]
            op_gb_sm_n = (sum_aijOi + sum_bijXi + u_j * gb) / (sum(self.a) + sum(self.b) + u_j)
            self.od_opinion.append(op_gb_sm_n)

    def scores(self):
        shower_threshold = 0.75
        laundry_threshold = 0.50
        laundry_points = 75
        irrig_threshold = 0.30
        irrig_points = 50

        # Compare opinion and assign points
        if self.od_opinion >= shower_threshold:
            shower_points = 100
            self.score += shower_points
        elif self.od_opinion >= laundry_threshold:
            self.score += laundry_points
        elif self.od_opinion >= irrig_threshold:
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
        #     self.od_opinion.append(self.od_opinion[-1])
