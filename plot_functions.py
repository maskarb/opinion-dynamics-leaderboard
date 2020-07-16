### load general modules
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

### load colormap packages
import seaborn as sns

# Plot all the opinions
def plot_colormap(O, agents, num_ticks):
    yticks = np.linspace(1, agents, num_ticks+1, dtype=np.int)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax = sns.heatmap(O, cmap="coolwarm", yticklabels=yticks, xticklabels=True, vmin=0, vmax=1, cbar_kws={'use_gridspec':False,'location':'top', 'ticks':[0,1]}) #cmap="RdBu_r"
    ax.figure.axes[-1].set_xlabel('$O_j$', size=16)
    plt.xticks(rotation=0)
    plt.gca().invert_yaxis()
    ax.set_yticks(yticks)
    plt.xscale('symlog')
    ax.set_xlabel('Time (days)', fontsize = 16)
    ax.set_ylabel('agent ID, j', fontsize = 16)
    plt.show()

# Plot opinions
def plot_agents(O, ts, agent_ID=None):
    fig, axes = plt.subplots(1, 1, figsize=(6, 5), sharex=True)
    # plot all the agents
    if not agent_ID:
        print('OOP-based code')
        # plt.plot(O, 'b-', label='Customer {}'.format(agent_ID))
        # plt.semilogx(list(range(0, ts + 1)), np.array(O).T)
        plt.plot(list(range(1, ts + 2)),  O)
    else:
        # plot an individual agent
        # plt.semilogx(list(range(0, ts + 1)),  O, 'b-', label='Customer {}'.format(agent_ID))
        plt.plot(list(range(1, ts + 2)),  O, 'b-', label='Customer {}'.format(agent_ID))
        plt.subplots_adjust(top = 0.95, bottom = 0.15)
    # axes.set_xscale('log')
    axes.legend(loc = 'best', prop = {'size': 10})
    axes.set_xlabel('Time (days)', fontsize = 16)
    axes.set_ylabel('Customer opinion, $O_j$', fontsize = 16)
    axes.set_ylim(0, 1)
    plt.show()

# Plot the mean and std dev of the opinions
def plot_mean_std(O_mean, O_std, ts):    
    fig, axes = plt.subplots(1, 1, figsize=(6, 5), sharex=True)
    plt.semilogx(list(range(1, ts+2)),  O_mean, label='$\mu$(O)')
    plt.semilogx(list(range(1, ts+2)),  O_std, label='$\sigma$(O)')
    axes.legend(loc = 'best', prop = {'size':10})
    axes.set_xlabel('Time (days)', fontsize = 16)
    axes.set_ylabel('Opinion', fontsize = 16)
    axes.set_ylim(0, 1)
    plt.show()