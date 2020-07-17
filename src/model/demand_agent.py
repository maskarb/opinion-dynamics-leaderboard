import numpy as np

from mesa import Agent


class DemandAgent(Agent):
    """An agent with initial opinion."""

    def __init__(self, unique_id, model, leaderboard):
        super().__init__(unique_id, model)
        self.type = leaderboard
        self.od_opinion = [0]
        self.decision = [np.random.randint(0, 2)]  # [0]
        self.a = np.random.randint(0, 2, size=self.model.n_agents)
        self.b = np.random.randint(0, 2, size=self.model.n_agents)
        self.threshold = np.random.uniform(0.3, 0.9)  # 0.9
        self.rank = [0]
        self.score = [0]
        self.O_ave = [0]
        self.S_ave = [0]
        self.D = [0]
        self.F = [0]
        self.new_opinion = [0]

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.od_opinion[self.time] == other.od_opinion[self.time]

    def __lt__(self, other):
        return self.od_opinion[self.time] < other.od_opinion[self.time]

    def __gt__(self, other):
        return self.od_opinion[self.time] > other.od_opinion[self.time]

    @property
    def time(self):
        return self.model.schedule.time

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
            O_j = getattr(self, self.type)[self.time]
            op_gb = (O_j + u_j * gb) / (1 + u_j)
            self.od_opinion.append(op_gb)

        # Opinion from global_broadcast + social media:
        elif self.model.scenario == 2:
            sum_aijOi = self.a[self.unique_id] * getattr(self, self.type)[self.time]  # 0
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_aijOi += self.a[agent.unique_id] * getattr(agent, agent.type)[self.time]
            op_gb_sm = (sum_aijOi + u_j * gb) / (sum(self.a) + u_j)
            self.od_opinion.append(op_gb_sm)

        # Opinion from global_broadcast + neighbors:
        elif self.model.scenario == 3:
            O_j = getattr(self, self.type)[self.time]
            sum_bijXi = self.b[self.unique_id] * self.decision[self.time]
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_bijXi += self.b[agent.unique_id] * agent.decision[self.time]
            op_gb_n = (O_j + sum_bijXi + u_j * gb) / (1 + sum(self.b) + u_j)
            self.od_opinion.append(op_gb_n)

        # Opinion from global_broadcast + social media + neighbors:
        elif self.model.scenario == 4:
            O_j = getattr(self, self.type)[self.time]
            sum_aijOi = self.a[self.unique_id] * getattr(self, self.type)[self.time]
            sum_bijXi = self.b[self.unique_id] * self.decision[self.time]
            for agent in self.model.schedule.agents:
                if agent.unique_id != self.unique_id:
                    sum_aijOi += self.a[agent.unique_id] * getattr(agent, agent.type)[self.time]
                    sum_bijXi += self.b[agent.unique_id] * agent.decision[self.time]
            op_gb_sm_n = (sum_aijOi + sum_bijXi + u_j * gb) / (sum(self.a) + sum(self.b) + u_j)
            self.od_opinion.append(op_gb_sm_n)

    def calculate_score(self):
        opinion = self.od_opinion[self.time]
        score = self.score[self.time]

        for ranking in self.model.config.ranking_attrs:
            threshold = self.model.config.get(ranking)
            if opinion >= threshold.threshold:
                score += threshold.points
                break
        self.score.append(score)

    def step(self):
        self.update_opinion()
        self.calculate_score()
        # self.update_decision()
        # self.update_decision()
        # if self.decision[-1] == 1:
        #     self.update_opinion()
        # else:
        #     self.od_opinion.append(self.od_opinion[-1])
