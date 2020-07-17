from statistics import mean


def convert_opinion(agent_list, time):
    def get_threshold():
        high = int(len(agent_list) * 0.3)
        low = int(len(agent_list) * 0.7)
        return (high, low)

    def get_diff():
        min_opinion = min(a.opinion[time] for a in agent_list)
        max_opinion = max(a.opinion[time] for a in agent_list)
        return abs(max_opinion - min_opinion)

    def high_leader(i):
        i += 1
        return mean(a.opinion[time] for a in agent_list[i : i + 4])

    def mid_leader(i):
        h = i - 1
        higher = [a.opinion[time] for a in agent_list[h : h - 2 : -1]]
        l = i + 1
        lower = [a.opinion[time] for a in agent_list[l : l + 2]]
        return mean(higher + lower)

    def low_leader(i):
        i -= 1
        return mean(a.opinion[time] for a in agent_list[i : i - 4 : -1])

    _ = get_diff()
    high_thresh, low_thresh = get_threshold()

    for i, a in enumerate(agent_list):
        if a.rank > high_thresh:
            a.S_ave.append(high_leader(i))
        elif low_thresh <= a.rank <= high_thresh:
            a.S_ave.append(mid_leader(i))
        elif a.rank < low_thresh:
            a.S_ave.append(low_leader(i))
        else:
            print("You done fucked up")

    return
