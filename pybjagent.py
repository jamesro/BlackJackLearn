import numpy as np
import matplotlib.pyplot as plt
from pickle import dump,load
from blackjack.player import Player
from stateHandler import encode_state

class Agent:
    
    
    def __init__(self):
        self.p = Player()
        self.actions = { 1 : self.p.hit,
                         2 : self.p.stand,
                          3 : self.p.double,
                         4 : self.p.split,
                        }

        self.Q = np.empty([0,5],dtype=object)

    def choose_action(self,s,epsilon):
        possibleActions = np.where(s!=-np.inf)[0][1:]
        
        if (np.random.rand()) <= epsilon:
            action = np.random.choice(possibleActions)
        else:
            action = np.argmax(s[1:]) + 1
        return action


    def add_state(self,s):
        """
        Q-matrix:

            0    |  1  |   2   |    3   |   4   |
                |(Hit)|(Stand)|(Double)|(Split)|
          states |
            .   |
            .   |
        """
        Qrow = np.hstack((s,np.array((0.,0.,0.,0.),dtype=object)))
            
        if s[1] == "1":        # Doubling is not allowed after hitting
            Qrow[-2] = -np.inf
        else:
            Qrow[-2] = np.random.rand(1)[0]*0.1
        if s[2] == "0":
            Qrow[-1] = -np.inf
        else:
            Qrow[-1] = np.random.rand(1)[0]*0.1
        # Randomly initialize Q's available actions
        Qrow[1:3] = np.random.rand(2)*0.1
        
        self.Q = np.vstack((self.Q,Qrow))    


    def get_reward(self,p):
        if p.gameState == "Lost":
            return -1.0
        elif p.gameState == "Won":
            return 1.0
        elif p.gameState == "InPlay":
            return 0.1
        elif p.gameState == "Push":
            return 0.5
        elif p.gameState == "Natural":
            return 0.0


    def update_Q(self,Q,p,s,a,ns,na,r,mu,gamma):
        if p.gameState != "InPlay":
            return mu*(r + gamma*(r - Q[s,a]))
        else:
            return mu*(r + gamma*Q[ns,na]-Q[s,a])


    def learn(self,mu,gamma,epsilon,nGames,plots=False):
        x = []
        # Episodic epsilon-greedy algorithm
        for i in range(nGames):
            reward = 0 
            if len(self.p.table.splitHand)==0:
                self.p.bet(1)
                if self.p.gameState == "Natural": self.p.bet(1)
            else:
                self.p.table.hand = self.p.table.splitHand.pop()
                self.p.table.hand.is_split = False
                self.p.gameState = "InPlay"


            while self.p.gameState == "InPlay":    
                stateKey = encode_state(self.p.table.hand,self.p.table.dealer_hand)
                # If we haven't seen this state before, extend Q
                if stateKey not in self.Q[:,0]:
                    self.add_state(stateKey)
                
                stateIndex = np.where(stateKey==self.Q[:,0])[0][0]
                state = self.Q[stateIndex]
                
                a = self.choose_action(state,epsilon)    
                self.actions[a]()

                nextStateKey = encode_state(self.p.table.hand,self.p.table.dealer_hand)

                if nextStateKey not in self.Q[:,0]:
                    self.add_state(nextStateKey)
                    
                nextStateIndex = np.where(nextStateKey==self.Q[:,0])[0][0]
                nextState = self.Q[nextStateIndex]

                na = self.choose_action(nextState,epsilon)
    
                reward += self.get_reward(self.p)
                    
                self.Q[stateIndex,a] += self.update_Q(self.Q,
                                                    self.p,
                                                    stateIndex,
                                                    a,
                                                    nextStateIndex,
                                                    na,
                                                    reward,
                                                    mu=mu,
                                                    gamma=gamma)

            x.append((1-self.p.losses/(i+1)))

        print("Wins: ",self.p.wins)
        print("Losses: ", self.p.losses)
        print("Pushes: ",self.p.pushes)
        print("Naturals: ",self.p.naturals)
        pcnt = 1.0 - (self.p.losses/nGames)
        print("Percent not lost: ",pcnt*100,"%")

        if plots:
            plt.plot(x)
            plt.ylabel("Percent won/drawn")
            plt.xlabel("Games played")
            plt.show()




    def save(self,filename):
        dump(self.Q,open(filename,"wb"))


    def load(self,filename):
        Q = load(open(filename,"rb"))
        self.Q = Q


    def play(self,nGames):
        # Episodic epsilon-greedy algorithm
        for i in range(nGames):
            self.p.bet(1)
            if self.p.gameState != "InPlay": self.p.bet(1)
            
            while self.p.gameState == "InPlay":    
                stateKey = encode_state(self.p.table.hand,self.p.table.dealer_hand)
                
                stateIndex = np.where(stateKey==self.Q[:,0])[0][0]
                state = self.Q[stateIndex]
                
                a = self.choose_action(state,epsilon=-np.inf)    
                self.actions[a]()

        print("Wins: ",self.p.wins)
        print("Losses: ", self.p.losses)
        print("Pushes: ",self.p.pushes)
        print("Naturals: ",self.p.naturals)
        pcnt = 1.0 - (self.p.losses/nGames)
        print("Percent not lost: ",pcnt*100,"%")