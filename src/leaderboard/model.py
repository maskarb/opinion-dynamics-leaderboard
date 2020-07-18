from statistics import mean


def convert_opinion(agent_list, time):  # noqa: C901
    def get_threshold():
        high = int(len(agent_list) * 0.3)
        low = int(len(agent_list) * 0.7)
        return (high, low)

    def get_diff():
        min_opinion = min(a.od_opinion[time] for a in agent_list)
        max_opinion = max(a.od_opinion[time] for a in agent_list)
        return abs(max_opinion - min_opinion)

    def high_leader(i, attr):
        i += 1
        return mean([getattr(a, attr)[time] for a in agent_list[i : i + 3]])

    def mid_leader(i, attr):
        h = i - 1
        higher = [getattr(a, attr)[time] for a in agent_list[h : h - 2 : -1]]
        l = i + 1
        lower = [getattr(a, attr)[time] for a in agent_list[l : l + 2]]
        return mean(higher + lower)

    def low_leader(i, attr):
        i -= 1
        return mean([getattr(a, attr)[time] for a in agent_list[i : i - 3 : -1]])

    def calc_f(agent, diff_max):
        return 2 + (2 * agent.D[time] / diff_max)

    def calc_new_O(a):
        return a.od_opinion[time] - (a.od_opinion[time] - a.O_ave[time]) / a.F[time]

    def calc_for_thresholds(gattr, sattr):
        for i, a in enumerate(agent_list):
            if a.rank[time] < high_thresh:
                getattr(a, sattr).append(high_leader(i, gattr))
            elif low_thresh >= a.rank[time] >= high_thresh:
                getattr(a, sattr).append(mid_leader(i, gattr))
            else:
                getattr(a, sattr).append(low_leader(i, gattr))

    diff_max = get_diff()
    high_thresh, low_thresh = get_threshold()

    calc_for_thresholds("score", "S_ave")

    for a in agent_list:
        a.D.append(abs(a.score[time] - a.S_ave[time]))
        a.F.append(calc_f(a, diff_max))

    calc_for_thresholds("od_opinion", "O_ave")

    for a in agent_list:
        a.new_opinion.append(calc_new_O(a))

    return
