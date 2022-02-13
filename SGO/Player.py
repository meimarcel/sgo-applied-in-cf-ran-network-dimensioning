#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: meimarcel
"""

class Player:
    def __init__(self,position, bestPosition, bestEvals, numberOfRrh, numberOfVariables):
        self.position = position
        self.bestPosition = bestPosition
        self.bestEvals = bestEvals
        self.numberOfRrh = numberOfRrh
        self.numberOfVariables = numberOfVariables
        self.v1 = [[0] * numberOfVariables for i in range(numberOfRrh)]
        self.v0 = [[0] * numberOfVariables for i in range(numberOfRrh)]
    
    def getBestEval(self):
        return sum(self.bestEvals)
        