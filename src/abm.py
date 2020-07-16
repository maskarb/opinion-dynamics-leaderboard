import sys

import numpy as np

from model.demand_model import DemandModel

# load some owned plot functions
# from utils.plot_functions import plot_colormap, plot_agents, plot_mean_std


def main():
    # for runs in range(0, 1):
    num_agents = 5  # 100
    time_steps = 5  # 30
    scenario = int(sys.argv[-1]) if len(sys.argv) > 1 else 1
    # Run the model
    model = DemandModel(num_agents, scenario)
    for i in range(time_steps):
        model.step()

    # Store the results
    all_opinion = np.zeros(shape=(time_steps + 1, num_agents))
    for i, agent in enumerate(model.schedule.agents):
        all_opinion[:, i] = np.array(agent.od_opinion)
        print("Agent rank", agent.rank, "Agent opinion", agent.od_opinion)

    # print the all_opinion array
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(all_opinion.T)

    # Plot the opinion of a single agent
    # agent_ID = np.random.randint(0, num_agents)
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
