import pybjagent

if __name__ == "__main__":
    agent = pybjagent.Agent()
    agent.learn(mu=0.75, gamma=0.15, epsilon=0.1, nGames=10000, plots=True)
