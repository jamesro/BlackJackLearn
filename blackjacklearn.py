import numpy as np
import matplotlib.pyplot as plt
from pickle import dump,load
from blackjack.player import Player
from bot import encodeState, addState

class Agent:
	def __init__(self):
		self.p = Player()
		self.actions = { 1 : self.p.hit,
						 2 : self.p.stand,
		 				 3 : self.p.double,
						 4 : self.p.split,
						}
		self.Q = np.array((("0010404",0.05,0.03,0.,0.07),
						("0000504",0.02,0.01,0.,-np.inf)),dtype=object)


	def chooseAction(self,s,epsilon):
		possibleActions = np.where(s!=-np.inf)[0][1:]
		
		if (np.random.rand()) <= epsilon:
			action = np.random.choice(possibleActions)
		else:
			action = np.argmax(s[1:]) + 1
		return action


	def getReward(self,p):
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


	def updateQ(self,Q,p,s,a,ns,na,r,mu,gamma):
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
				stateKey = encodeState(self.p)
				# If we haven't seen this state before, extend Q
				if stateKey not in self.Q[:,0]:
					self.Q = addState(stateKey,self.Q)
				
				stateIndex = np.where(stateKey==self.Q[:,0])[0][0]
				state = self.Q[stateIndex]
				
				a = self.chooseAction(state,epsilon)	
				self.actions[a]()

				nextStateKey = encodeState(self.p.table.hand,self.p.table.dealer_hand)

				if nextStateKey not in self.Q[:,0]:
					addState(nextStateKey)
					
				nextStateIndex = np.where(nextStateKey==self.Q[:,0])[0][0]
				nextState = self.Q[nextStateIndex]

				na = self.chooseAction(nextState,epsilon)
	
				reward += self.getReward(self.p)
					
				self.Q[stateIndex,a] += self.updateQ(self.Q,
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

	def play(self,nGames,plots=False):
		x = []
		for i in range(nGames):
			self.p.bet(1)
			if self.p.gameState != "InPlay": self.p.bet(1)
			
			while self.p.gameState == "InPlay":	
				stateKey = encodeState(self.p.table.hand,self.p.table.dealer_hand)
				
				stateIndex = np.where(stateKey==self.Q[:,0])[0][0]
				state = self.Q[stateIndex]
				
				a = self.chooseAction(state,epsilon=-np.inf)	
				self.actions[a]()

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





if __name__ == "__main__":
	agent = Agent()
	agent.learn(mu=0.75,gamma=0.15,epsilon=0.1,nGames=1000,plots=True)
	

