#!/usr/bin/python
# -*- coding: utf-8 -*-



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


