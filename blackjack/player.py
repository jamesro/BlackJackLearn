#!/usr/bin/python
# -*- coding: utf-8 -*-

from .cards import *
from .hand import Hand
from .table import Table

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
		if len(self.table.deck._cards) <= 15:
			self.table.deck = Deck()

	def split(self):
		if self.table.hand.cards[0].hard == self.table.hand.cards[1].hard:
			if not self.table.hand.is_split:
				print("Split. Betting $",self.betAmount)
				self.bank -= self.betAmount
				self.table.splitHand.append(Hand(self.table.hand.cards[1], self.table.deck.pop(),is_split=True))
				self.table.hand = Hand(self.table.hand.cards[0], self.table.deck.pop(),is_split=True)

				print("Your first hand: ",self.table.hand)
			else:
				raise SplitError("Hand has already been split")
		else:
			raise SplitError("Hand cannot be split")

	# def _endSplitGame(self):
	# 	try: # if this is the end of the first of the two hands
	# 		self.table.hand = self.table.other_hand
	# 		del self.table.other_hand

	# 		#self.gameState = "InPlay"
	# 		print("Your second hand: ",self.table.hand)
	# 		if self.table.hand.total() == 21:
	# 			self.endPlay()
	# 	except:
	# 		pass


	def _win(self):
		self.gameState = "Won"
		self.bank += 2 * self.betAmount
		print("\nYou win. You have $",self.bank,"\n")
		
		self.wins += 1

		# if self.table.hand.is_split:
		# 	self._endSplitGame()

		self.deckCheck()
		


	def _lose(self):
		self.gameState = "Lost"
		print("\nYou lose. You have $",self.bank,"\n")
		
		self.losses += 1

		# if self.table.hand.is_split:
		# 	self._endSplitGame()

		self.deckCheck()


	def _natural(self):
		self.naturals += 1
		self.gameState = "Natural"
		self.bank += self.betAmount + 1.5*self.betAmount
		print("\nYou win. You have $",self.bank,"\n")

		# if self.table.hand.is_split:
		# 	self._endSplitGame()

		self.deckCheck()

	def _push(self):
		self.pushes += 1
		self.gameState = "Push"
		self.bank += self.betAmount
		print("\nDraw. You have $",self.bank,"\n")

		# if self.table.hand.is_split:
		# 	self._endSplitGame()
		
		self.deckCheck()








class SplitError(Exception):
	pass

class DoubleError(Exception):
	pass
