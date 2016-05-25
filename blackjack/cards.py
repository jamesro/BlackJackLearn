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



