from math import ceil
from statistics import mean


def convert_opinion(agent_list):  # noqa: C901

    num_agents = len(agent_list)
    n_comp = ceil(num_agents * 0.3)
    O_ave = [0] * num_agents
    S_ave = [0] * num_agents
    D = [0] * num_agents
    F = [0] * num_agents

    def get(lis, a):
        return lis[a.id]

    def get_threshold():
        high = int(len(agent_list) * 0.3)
        low = int(len(agent_list) * 0.7)
        return (high, low)

    def get_diff():
        min_opinion = min(a.opinion_od for a in agent_list)
        max_opinion = max(a.opinion_od for a in agent_list)
        return abs(max_opinion - min_opinion)

    def high_leader(i, attr):
        i += 1
        return mean([getattr(a, attr) for a in agent_list[i : i + n_comp]])

    def mid_leader(i, attr):
        half_comp = ceil(n_comp / 2)
        h = i - 1
        higher = [getattr(a, attr) for a in agent_list[h : h - half_comp : -1]]
        l = i + 1
        lower = [getattr(a, attr) for a in agent_list[l : l + half_comp]]
        return mean(higher + lower)

    def low_leader(i, attr):
        i -= 1
        return mean([getattr(a, attr) for a in agent_list[i : i - n_comp : -1]])

    def calc_f(a, diff_max):
        return 2 + (2 * get(D, a) / diff_max)

    def calc_new_O(a):
        return a.opinion_od - (a.opinion_od - get(O_ave, a)) / get(F, a)

    def calc_for_thresholds(gattr, sattr):
        for i, a in enumerate(agent_list):
            if a.rank < high_thresh:
                setattr(a, sattr, high_leader(i, gattr))
            elif low_thresh >= a.rank >= high_thresh:
                setattr(a, sattr, mid_leader(i, gattr))
            else:
                setattr(a, sattr, low_leader(i, gattr))

    diff_max = get_diff()
    high_thresh, low_thresh = get_threshold()

    calc_for_thresholds("score", "S_ave")

    for a in agent_list:
        D[a.id] = abs(a.score - get(S_ave, a))
        F[a.id] = calc_f(a, diff_max)

    calc_for_thresholds("opinion_od", "O_ave")

    for a in agent_list:
        a.opinion_new = calc_new_O(a)

    return
