from cards2 import *
import numpy as np
import matplotlib.pyplot as plt

def encodeState(player):
	"""
	Return the state of the player's hand as 
	a 7 digit string of numbers. Where information
	is encoded in the string, just like a credit card number.
	e.g.
		101710
		|1|0|17|10|

	The first number is if the hand has an Ace or not(1,0)
	The second is if the hand has been hit yet (0,1)
	The third is the total of the hand (2-digit number)
	The fourth is the total of the dealer's hand (2-digit number).
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


def addState(s,Q):
	Qrow = np.hstack((s,np.array((0.,0.,0.),dtype=object)))
		
	if s[1] == "1":		# Doubling is not allowed after hitting
		Qrow[-1] = -np.inf
	
	# Randomly initialize Q's available actions
	Qrow[1:3] = np.random.rand(2)*0.1
	
	return np.vstack((Q,Qrow))	
	


Q = np.array((("000404",0.5,0.3,0.),
	("000504",0.2,0.1,0.)),dtype=object)





p = Player()
mu = 0.7
gamma = 0.4
epsilon = 0.2
nGames = 50000

"""
Q-matrix:

	0	|  1  |   2   |    3   |   4   |
		|(Hit)|(Stand)|(Double)|(Split)|
 states |
    .   |
    .   |
"""




actions = { 1 : p.hit,
			2 : p.stand,
		 	3 : p.double,
			#4 : p.split,
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
		return -3
	elif p.gameState == "Won":
		return 3
	elif p.gameState == "InPlay":
		return 0
	elif p.gameState == "Push":
		return 1

def updateQ(Q,p,s,a,ns,na,r):
	if p.gameState != "InPlay":
		return mu*(r + gamma*(r - Q[s,a]))
	else:
		return mu*(r + gamma*Q[ns,na]-Q[s,a])

x = []

# Episodic epsilon-greedy algorithm
for i in range(nGames):
	
	p.bet(2)

	if p.gameState != "InPlay": p.bet(2)

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
print("Percent won: ",pcnt,"%")




plt.plot(x)
plt.ylabel("Percent won/drawn")
plt.xlabel("Games played")
plt.show()


# for line in Q:
# 	print(line[0]," ",np.argmax(line[1:]))
