from cards3 import *
import numpy as np
import matplotlib.pyplot as plt

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



"""
Q-matrix:

	0	|  1  |   2   |    3   |   4   |
		|(Hit)|(Stand)|(Double)|(Split)|
 states |
    .   |
    .   |
"""
def addState(s,Q):
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
	
	return np.vstack((Q,Qrow))	
	


Q = np.array((("0010404",0.05,0.03,0.,0.07),
	("0000504",0.02,0.01,0.,-np.inf)),dtype=object)





p = Player()
mu = 0.75
gamma = 0.2
epsilon = 0.1
nGames = 10000





actions = { 1 : p.hit,
			2 : p.stand,
		 	3 : p.double,
			4 : p.split,
}

def chooseAction(s):
	possibleActions = np.where(s!=-np.inf)[0][1:]
		
	if (np.random.rand()) <= epsilon:
		action = np.random.choice(possibleActions)
	else:
		action = np.argmax(s[1:]) + 1
	return action


def getReward(p):
	if p.gameState == "Lost":
		return -1.0
	elif p.gameState == "Won":
		return 1.0
	elif p.gameState == "InPlay":
		return 0.1
	elif p.gameState == "Push":
		return 0.5

def updateQ(Q,p,s,a,ns,na,r):
	if p.gameState != "InPlay":
		return mu*(r + gamma*(r - Q[s,a]))
	else:
		return mu*(r + gamma*Q[ns,na]-Q[s,a])

x = []

# Episodic epsilon-greedy algorithm
for i in range(nGames):
	
	p.bet(1)

	if p.gameState != "InPlay": p.bet(1)

	while p.gameState == "InPlay":	

		stateKey = encodeState(p)
		
		# If we haven't seen this state before, extend Q
		if stateKey not in Q[:,0]:
			Q = addState(stateKey,Q)
		
		stateIndex = np.where(stateKey==Q[:,0])[0][0]
		state = Q[stateIndex]

		
		a = chooseAction(state)
		
		
		actions[a]()

		nextStateKey = encodeState(p)

		if nextStateKey not in Q[:,0]:
			Q = addState(nextStateKey,Q)
			
		nextStateIndex = np.where(nextStateKey==Q[:,0])[0][0]
		nextState = Q[nextStateIndex]

		na = chooseAction(nextState)
		
		reward = getReward(p)
			
		Q[stateIndex,a] += updateQ(Q,p,stateIndex,a,nextStateIndex,na,reward)

	x.append((1-p.losses/(i+1)))




print("Wins: ",p.wins)
print("Losses: ", p.losses)
print("Pushes: ",p.pushes)
print("Naturals: ",p.naturals)
pcnt = 1.0 - (p.losses/nGames)
print("Percent won: ",pcnt*100,"%")




# plt.plot(x)
# plt.ylabel("Percent won/drawn")
# plt.xlabel("Games played")
# plt.show()
