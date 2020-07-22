from random import choice

import numpy as np

from mesa import Agent


class DemandAgent(Agent):
    """An agent with initial opinion."""

    def __init__(self, unique_id, model, leaderboard):
        super().__init__(unique_id, model)
        self.id = unique_id
        self.type = leaderboard
        self.a = np.random.randint(0, 2, size=self.model.n_agents)
        self.b = np.random.randint(0, 2, size=self.model.n_agents)
        self.decision = np.random.randint(0, 2)
        self.threshold = np.random.uniform(0.3, 0.9)
        self.opinion_new = 0
        self.opinion_od = 0
        self.opinion_staged = 0
        self.rank = 0
        self.score = 0

    def __eq__(self, other):
        return (self.__class__, self.opinion_od) == (other.__class__, other.opinion_od)

    def __lt__(self, other):
        """Compare opinion_od. Ties are broken on score."""
        return (self.opinion_od, self.score) < (other.opinion_od, other.score)

    def __gt__(self, other):
        """Compare opinion_od. Ties are broken on score."""
        return (self.opinion_od, self.score) > (other.opinion_od, other.score)

    def __str__(self):
        int_formatter = "{:4d}".format
        float_formatter = "{:.5f}".format
        np.set_printoptions(formatter={"float_kind": float_formatter, "int_kind": int_formatter})
        df = self.model.datacollector.get_agent_vars_dataframe().query(f"AgentID == {self.id}")
        return (
            f"Agent ID: {self.id} | Rank: {df.Rank.values} | Opinion: {df.Opinion.values} | Score: {df.Score.values}"
        )

    @property
    def u(self):
        return self.u_j[self.time]

    @property
    def influence(self):
        return np.random.randint(0, 2)

    @property
    def opinion(self):
        return getattr(self, self.type)

    @property
    def sum_a(self):
        return sum(self.a)

    @property
    def sum_b(self):
        return sum(self.b)

    @property
    def time(self):
        return self.model.schedule.time

    def update_decision(self):
        # self.decision = 1
        # print('opinion', self.opinion_od, 'threshold', self.threshold)
        # print('O[-1]', self.last_decision)

        # Basset formulation:
        # if self.decision >= self.threshold:
        #     self.decision = 1
        # else:
        #     self.decision = 0

        # Du formulation
        if self.decision == 0 and self.opinion_od < self.threshold:
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
        score = self.score
        for ranking in self.model.config.ranking_attrs:
            threshold = self.model.config.get(ranking)
            if self.opinion_od >= threshold.threshold:
                score += threshold.points
                break
        self.score = score

    def scenario_1(self, gb, u_j):
        op_gb = (self.opinion + u_j * gb) / (1 + u_j)
        self.opinion_staged = op_gb

    def scenario_2(self, gb, u_j):
        paired_agent = choice(self.model.schedule.agents)
        do_i_influence_the_other = self.influence * self.opinion_od
        was_i_influenced = paired_agent.influence * paired_agent.opinion_od
        paired_staged = (paired_agent.opinion_od + u_j * gb) / (1 + u_j)
        if do_i_influence_the_other:
            paired_staged = (self.opinion_od + paired_agent.opinion_od + u_j * gb) / (2 + u_j)
        my_staged = (self.opinion_od + u_j * gb) / (1 + u_j)
        if was_i_influenced:
            my_staged = (self.opinion_od + paired_agent.opinion_od + u_j * gb) / (2 + u_j)
        self.opinion_od = my_staged
        paired_agent.opinion_od = paired_staged

    def scenario_3(self, gb, u_j):
        sum_bijXi = self.b[self.id] * self.decision
        for agent in self.model.schedule.agents:
            if agent.id != self.id:
                sum_bijXi += self.b[agent.id] * agent.decision
        op_gb_n = (self.opinion + sum_bijXi + u_j * gb) / (1 + self.sum_b + u_j)
        self.opinion_staged = op_gb_n

    def scenario_4(self, gb, u_j):
        sum_aijOi = self.a[self.id] * self.opinion
        sum_bijXi = self.b[self.id] * self.decision
        for agent in self.model.schedule.agents:
            if agent.id != self.id:
                sum_aijOi += self.a[agent.id] * self.opinion
                sum_bijXi += self.b[agent.id] * agent.decision
        op_gb_sm_n = (sum_aijOi + sum_bijXi + u_j * gb) / (self.sum_a + self.sum_b + u_j)
        self.opinion_staged = op_gb_sm_n

    def step(self):
        self.update_opinion()
