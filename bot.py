#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np


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
        
    if s[1] == "1":     # Doubling is not allowed after hitting
        Qrow[-1] = -np.inf
    
    # Randomly initialize Q's available actions
    Qrow[1:3] = np.random.rand(2)*0.1
    
    return np.vstack((Q,Qrow))  
    