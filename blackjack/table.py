#!/usr/bin/python
# -*- coding: utf-8 -*-

from .cards import Deck
from .hand import Hand

class Table:
	def __init__(self):
		self.deck = Deck()
		self.splitHand = []
		
	def deal(self):
		try:
			self.hand = Hand(self.deck.pop(),self.deck.pop())
			self.dealer_hand = Hand(self.deck.pop())
			self.hole_card = self.deck.pop()			
		except IndexError:
			self.deck = Deck()
			return self.deal()

		print("\nDealing. \nDealer's hand: \t",self.dealer_hand,"[?] \nYour hand: \t",self.hand,"\n")





