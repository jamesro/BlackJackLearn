def encode_state(hand,dealer_hand):
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
	
	if len(hand.cards)==2:
		s += "0"
	else:
		s += "1"
	
	if hand.is_split:
		s += "0"
	elif (hand.cards[0].hard == hand.cards[1].hard) and (len(hand.cards)==2):
		s += "1"
	else:
		s += "0"

	hand_total = str(hand.total())
	if len(hand_total) == 1:
		s += "0" + hand_total
	else:
		s += hand_total
	
	dealer_total =str(dealer_hand.total())
	if len(dealer_total) == 1:
		s += "0" + dealer_total
	else:
		s += dealer_total

	return s
