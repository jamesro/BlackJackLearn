#!/usr/bin/python
# -*- coding: utf-8 -*-


import random


#Superclass
class Card:
	def __init__(self, rank, suit):
		self.suit = suit
		self.rank = rank
		self.hard, self.soft = self._points()
	def __str__(self):
		return "{rank}{suit}".format(**self.__dict__)
	

#Subclasses of Card
class NumberCard(Card):
	def _points(self):
		return int(self.rank), int(self.rank)

class AceCard(Card):
	def _points(self):
		return 1, 11

class FaceCard(Card):
	def _points(self):
		return 10, 10


# Factory function
def card_factory(rank, suit):
	"""Factory function for building a deck of cards, used in conjunction with
	the Card and Deck classes"""
	if rank ==1: return AceCard("A", suit)
	elif 2 <= rank < 11	: return NumberCard(str(rank), suit)
	elif 11<= rank < 14 : 
		name = { 11: 'J', 12: 'Q', 13: 'K' }[rank]
		return FaceCard(name, suit)
	else:
		raise Exception("Rank out of range") 








class Deck:
	def __init__(self,size=8):
		suits = ("♣","♦", "♥", "♠")
		self._cards = []
		for i in range(size):
			self._cards += [card_factory(rank,suit) for rank in range(1,14) for suit in suits]
		random.shuffle(self._cards)
		# burn = random.randint(1,52*size)
        # for i in range(burn): self.pop()
	def pop(self):
		return self._cards.pop()







class Hand:
	def __init__(self,*cards,is_split=False):
		self.cards = list(cards)
		self.is_split = is_split
	
	def total(self):
		delta_soft = max(c.soft-c.hard for c in self.cards)
		hard = sum(c.hard for c in self.cards)
		if hard + delta_soft <= 21: return hard + delta_soft
		return hard

	def __str__(self):
		return " ".join(map(str,self.cards))

	def __repr__(self):
		return "{__class__.__name__}({_cards_str})".format(
				__class__=self.__class__,
				_cards_str=", ".join(map(repr, self.cards)),
				**self.__dict__)
	
	def __contains__(self, rank):
		# allows one to test with: 'A' in hand
		# rather than: any(c.rank=='A' for c in hand.cards)
		# Lovely stuff.
		return any(c.rank==rank for c in self.cards)

	def __iadd__(self, card):
		self.cards.append(card)
		return self

	def __lt__(self, hand):
		return self.total() < hand.total()

	def __gt__(self,hand):
		return self.total() > hand.total()

	def __eq__(self,hand):
		return self.total() == hand.total()






class Table:
	def __init__(self):
		self.deck = Deck()

	def deal(self):
		try:
			self.hand = Hand(self.deck.pop(),self.deck.pop())
			self.dealer_hand = Hand(self.deck.pop())
			self.hole_card = self.deck.pop()			
		except IndexError:
			self.deck = Deck()
			return self.deal()

		print("\nDealing. \nDealer's hand: \t",self.dealer_hand,"[?] \nYour hand: \t",self.hand,"\n")







class Player:
	def __init__(self, bank=1000):
		self.gameState = ""
		self.table = Table()
		self.bank = bank
		self.wins = 0
		self.losses = 0
		self.pushes = 0
		self.naturals = 0



	def bet(self,amount):
		self.gameState = "InPlay"
		self.betAmount = amount
		self.bank -= self.betAmount
		print("Betting $",amount)
		self.table.deal()
		if self.table.hand.total() == 21:
			print("Blackjack.")
			self.endPlay(Natural
				=True)

	def hit(self,Double=False):
		self.table.hand += self.table.deck.pop()
		
		print("\nHit: ",self.table.hand,"\n")

		if self.table.hand.total() == 21:
			self.endPlay()
		elif self.table.hand.total() > 21:
			self._lose()
		elif Double==True: # You can't keep playing after doubling
			self.endPlay()
		


	def stand(self):
		self.table.dealer_hand += self.table.hole_card

		print("\nStand.\nDealer's hand: ",self.table.dealer_hand)
		self.endPlay()


	def double(self):
		if len(self.table.hand.cards) == 2:
			self.bank -= self.betAmount
			self.betAmount *= 2
			print("Double. Bet is $",self.betAmount)
			self.hit(Double=True)					
		elif len(self.table.hand.cards) > 2:
			raise DoubleError("Cannot double after hitting")


	def endPlay(self,Natural=False):
		while self.table.dealer_hand.total() < 17:
			self.table.dealer_hand += self.table.deck.pop()
			print("Dealer's hand: ",self.table.dealer_hand)
		
		if self.table.dealer_hand.total() == self.table.hand.total() <= 21:
			if Natural==True:
				self._natural()
			else:
				self._push()
		elif (self.table.dealer_hand > self.table.hand) and (self.table.dealer_hand.total() <= 21):
			self._lose()
		elif (self.table.dealer_hand.total() > 21) and (self.table.hand.total() <= 21):
			self._win()
		elif (self.table.dealer_hand < self.table.hand) and (self.table.hand.total() <= 21):
			self._win()

	def deckCheck(self):
		if len(self.table.deck._cards) <= 10:
			self.table.deck = Deck()

	def split(self):
		if self.table.hand.cards[0].hard == self.table.hand.cards[1].hard:
			if not self.table.hand.is_split:
				print("Split. Betting $",self.betAmount)
				self.bank -= self.betAmount
				self.table.other_hand = Hand(self.table.hand.cards[1], self.table.deck.pop(),is_split=True)
				self.table.hand = Hand(self.table.hand.cards[0], self.table.deck.pop(),is_split=True)

				print("Your first hand: ",self.table.hand)
			else:
				raise SplitError("Hand has already been split")
		else:
			raise SplitError("Hand cannot be split")

	def _endSplitGame(self):
		try: # if this is the end of the first of the two hands
			self.table.hand = self.table.other_hand
			del self.table.other_hand

			#self.gameState = "InPlay"
			print("Your second hand: ",self.table.hand)
			if self.table.hand.total() == 21:
				self.endPlay()
		except:
			pass


	def _win(self):
		self.gameState = "Won"
		self.bank += 2 * self.betAmount
		print("\nYou win. You have $",self.bank,"\n")
		
		self.wins += 1

		if self.table.hand.is_split:
			self._endSplitGame()

		self.deckCheck()
		


	def _lose(self):
		self.gameState = "Lost"
		print("\nYou lose. You have $",self.bank,"\n")
		
		self.losses += 1

		if self.table.hand.is_split:
			self._endSplitGame()

		self.deckCheck()


	def _natural(self):
		self.naturals += 1
		self.gameState = "Natural"
		self.bank += self.betAmount + 1.5*self.betAmount
		print("\nYou win. You have $",self.bank,"\n")

		if self.table.hand.is_split:
			self._endSplitGame()

		self.deckCheck()

	def _push(self):
		self.pushes += 1
		self.gameState = "Push"
		self.bank += self.betAmount
		print("\nDraw. You have $",self.bank,"\n")

		if self.table.hand.is_split:
			self._endSplitGame()
		
		self.deckCheck()








class SplitError(Exception):
	pass

class DoubleError(Exception):
	pass











if __name__ == "__main__":
	p = Player()






