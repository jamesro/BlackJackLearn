import pybjagent

if __name__ == "__main__":
    agent = pybjagent.Agent()
    learningSteps = agent.learn(mu=0.75, gamma=0.15, epsilon=0.1, nGames=10000, plots=True)

    [print(i) for i in learningSteps]