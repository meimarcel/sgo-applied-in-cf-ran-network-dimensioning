#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: meimarcel
"""

class Player:
    def __init__(self,position, bestPosition, bestEval, numberOfVariables):
        self.position = position
        self.bestPosition = bestPosition
        self.bestEval = bestEval
        self.numberOfVariables = numberOfVariables
        self.v1 = [0] * numberOfVariables
        self.v0 = [0] * numberOfVariables
    