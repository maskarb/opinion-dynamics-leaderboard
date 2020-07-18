import numpy as np

from mesa import Agent


class DemandAgent(Agent):
    """An agent with initial opinion."""

    def __init__(self, unique_id, model, leaderboard):
        super().__init__(unique_id, model)
        self.id = unique_id
        self.type = leaderboard
        self._od_opinion = [0]
        self._decision = [np.random.randint(0, 2)]  # [0]
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
    def decision(self):
        return self._decision[self.time]

    @property
    def last_decision(self):
        return self._decision[-1]

    @property
    def last_od_opinion(self):
        return self.od_opinion[-1]

    @property
    def od_opinion(self):
        return self._od_opinion

    @property
    def opinion(self):
        return getattr(self, self.type)[self.time]

    @property
    def sum_a(self):
        return sum(self.a)

    @property
    def sum_b(self):
        return sum(self.b)

    @property
    def time(self):
        return self.model.schedule.time

    @decision.setter
    def decision(self, val):
        self._decision.append(val)

    @od_opinion.setter
    def od_opinion(self, val):
        self._od_opinion.append(val)

    def update_decision(self):
        # self.decision = 1
        # print('opinion', self.od_opinion, 'threshold', self.threshold)
        # print('O[-1]', self.last_decision)

        # Basset formulation:
        # if self.last_decision >= self.threshold:
        #     self.decision = 1
        # else:
        #     self.decision = 0

        # Du formulation
        if self.last_decision == 0 and self.last_od_opinion < self.threshold:
            self.decision = 0
        else:
            self.decision = 1

    def update_opinion(self):  # noqa: C901
        gb = self.model.global_broadcast  # 0 or 1
        u_j = np.random.randint(0, 2)

        # Opinion from global_broadcast + social media:
        if self.model.scenario == 1:
            self.scenario_1(gb, u_j)

        # Opinion from global_broadcast + social media:
        elif self.model.scenario == 2:
            self.scenario_2(gb, u_j)

        # Opinion from global_broadcast + neighbors:
        elif self.model.scenario == 3:
            self.scenario_3(gb, u_j)

        # Opinion from global_broadcast + social media + neighbors:
        elif self.model.scenario == 4:
            self.scenario_4(gb, u_j)

    def calculate_score(self):
        opinion = self.od_opinion[self.time]
        score = self.score[self.time]

        for ranking in self.model.config.ranking_attrs:
            threshold = self.model.config.get(ranking)
            if opinion >= threshold.threshold:
                score += threshold.points
                break
        self.score.append(score)

    def scenario_1(self, gb, u_j):
        op_gb = (self.opinion + u_j * gb) / (1 + u_j)
        self.od_opinion = op_gb

    def scenario_2(self, gb, u_j):
        sum_aijOi = self.a[self.id] * self.opinion  # 0
        for agent in self.model.schedule.agents:
            if agent.id != self.id:
                sum_aijOi += self.a[agent.id] * self.opinion
        op_gb_sm = (sum_aijOi + u_j * gb) / (self.sum_a + u_j)
        self.od_opinion = op_gb_sm

    def scenario_3(self, gb, u_j):
        sum_bijXi = self.b[self.id] * self.decision
        for agent in self.model.schedule.agents:
            if agent.id != self.id:
                sum_bijXi += self.b[agent.id] * agent.decision
        op_gb_n = (self.opinion + sum_bijXi + u_j * gb) / (1 + self.sum_b + u_j)
        self.od_opinion = op_gb_n

    def scenario_4(self, gb, u_j):
        sum_aijOi = self.a[self.id] * self.opinion
        sum_bijXi = self.b[self.id] * self.decision
        for agent in self.model.schedule.agents:
            if agent.id != self.id:
                sum_aijOi += self.a[agent.id] * self.opinion
                sum_bijXi += self.b[agent.id] * agent.decision
        op_gb_sm_n = (sum_aijOi + sum_bijXi + u_j * gb) / (self.sum_a + self.sum_b + u_j)
        self.od_opinion = op_gb_sm_n

    def step(self):
        self.update_opinion()
        self.calculate_score()
