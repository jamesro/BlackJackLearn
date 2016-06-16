import numpy as np
import matplotlib.pyplot as plt
from pickle import dump,load
from blackjack.player import Player


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

            # x.append((1-self.p.losses/(i+1)))*100
            yield (1-self.p.losses/(i+1))*100
        # print("Wins: ",self.p.wins)
        # print("Losses: ", self.p.losses)
        # print("Pushes: ",self.p.pushes)
        # print("Naturals: ",self.p.naturals)
        # pcnt = 1.0 - (self.p.losses/nGames)
        # print("Percent not lost: ",pcnt*100,"%")
        #
        # # if plots:
        #     plt.plot(x)
        #     plt.ylabel("Percent won/drawn")
        #     plt.xlabel("Games played")
        #     plt.show()




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


def encode_state(hand, dealer_hand):
    """
    Return the state of the player's hand as
    a 7 digit string of numbers. Where information
    is encoded in the string, just like a credit card number.
    e.g.
        1001710
        |1|0|0|17|10|

    The first number is if the hand has an Ace or not(1,0)
    The second is if the hand has been hit yet (0,1)
    The third is if the hand is splittable (0,1)
    The fourth is the total of the hand (2-digit number)
    The fifth is the total of the dealer's hand (2-digit number).
    """

    s = ""
    if 'A' in hand:
        s += "1"
    else:
        s += "0"

    if len(hand.cards) == 2:
        s += "0"
    else:
        s += "1"

    if hand.is_split:
        s += "0"
    elif (hand.cards[0].hard == hand.cards[1].hard) and (len(hand.cards) == 2):
        s += "1"
    else:
        s += "0"

    hand_total = str(hand.total())
    if len(hand_total) == 1:
        s += "0" + hand_total
    else:
        s += hand_total

    dealer_total = str(dealer_hand.total())
    if len(dealer_total) == 1:
        s += "0" + dealer_total
    else:
        s += dealer_total

    return s
