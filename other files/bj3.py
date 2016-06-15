from cards3 import *
import numpy as np
import matplotlib.pyplot as plt

from blackjack import player

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

	def addState(self,s):
		"""
		Q-matrix:

			0	|  1  |   2   |    3   |   4   |
				|(Hit)|(Stand)|(Double)|(Split)|
	 	 states |
	    	.   |
	    	.   |
		"""
		Qrow = np.hstack((s,np.array((0.,0.,0.,0.),dtype=object)))
			
		if s[1] == "1":		# Doubling is not allowed after hitting
			Qrow[-2] = -np.inf
		else:
			Qrow[-2] = np.random.rand(1)*0.1
		if s[2] == "0":
			Qrow[-1] = -np.inf
		else:
			Qrow[-1] = np.random.rand(1)*0.1
		# Randomly initialize Q's available actions
		Qrow[1:3] = np.random.rand(2)*0.1
		
		self.Q = np.vstack((self.Q,Qrow))	


	def getReward(self,p):
		if p.gameState == "Lost":
			return -1.0
		elif p.gameState == "Won":
			return 1.0
		elif p.gameState == "InPlay":
			return 0.1
		elif p.gameState == "Push":
			return 0.5


	def updateQ(self,Q,p,s,a,ns,na,r,mu,gamma):
		if p.gameState != "InPlay":
			return mu*(r + gamma*(r - Q[s,a]))
		else:
			return mu*(r + gamma*Q[ns,na]-Q[s,a])


	def learn(self,mu,gamma,epsilon,nGames,plots=True):
		x = []
		# Episodic epsilon-greedy algorithm
		for i in range(nGames):
			self.p.bet(1)
			if self.p.gameState != "InPlay": self.p.bet(1)
			
			while self.p.gameState == "InPlay":	
				stateKey = encodeState(self.p)
				# If we haven't seen this state before, extend Q
				if stateKey not in self.Q[:,0]:
					self.addState(stateKey)
				
				stateIndex = np.where(stateKey==self.Q[:,0])[0][0]
				state = self.Q[stateIndex]
				
				a = self.chooseAction(state,epsilon)	
				self.actions[a]()

				nextStateKey = encodeState(self.p)

				if nextStateKey not in self.Q[:,0]:
					self.addState(nextStateKey)
					
				nextStateIndex = np.where(nextStateKey==self.Q[:,0])[0][0]
				nextState = self.Q[nextStateIndex]

				na = self.chooseAction(nextState,epsilon)
	
				reward = self.getReward(self.p)
					
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




def encodeState(player):
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
	if 'A' in player.table.hand:
		s += "1"
	else:
		s += "0"
	
	if len(player.table.hand.cards)==2:
		s += "0"
	else:
		s += "1"
	
	if player.table.hand.is_split:
		s += "0"
	elif (player.table.hand.cards[0].hard == player.table.hand.cards[1].hard) and (len(player.table.hand.cards)==2):
		s += "1"
	else:
		s += "0"

	hand_total = str(player.table.hand.total())
	if len(hand_total) == 1:
		s += "0" + hand_total
	else:
		s += hand_total
	
	dealer_total =str(player.table.dealer_hand.total())
	if len(dealer_total) == 1:
		s += "0" + dealer_total
	else:
		s += dealer_total

	return s




if __name__ == "__main__":
	agent = Agent()
	agent.learn(mu=0.75,gamma=0.2,epsilon=0.1,nGames=5000)