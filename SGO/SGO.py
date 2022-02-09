#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: meimarcel
"""

from copy import copy
from SGO.Player import Player
import time
import numpy as np
from math import e
from Restriction import Restricao

class SGO:
    def __init__(self, playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfVariables, 
                 target=None, moveOffProbability=0.2, moveForwardAfterMoveOffProbability=0.05, 
                 substitutionProbability=0.1, inertiaWeight=0.191, cognitiveWeight=0.191, socialWeight=0.618):
        self.playerNumber = playerNumber
        self.substituteNumber = substituteNumber
        self.kicksLimit = kicksLimit
        self.functionEvaluationLimit=functionEvaluationLimit
        self.numberOfVariables = numberOfVariables
        self.target = target
        self.moveOffProbability = moveOffProbability
        self.moveForwardAfterMoveOffProbability = moveForwardAfterMoveOffProbability
        self.substitutionProbability = substitutionProbability
        self.inertiaWeight = inertiaWeight
        self.cognitiveWeight = cognitiveWeight
        self.socialWeight = socialWeight
        self.dataFit = []
        self.globalBestPosition = []
        self.globalBestEval = 10e10000
    
    def run(self):
        players = []
        substitutePlayers = []
        functionEval = 0
        
        print("---------------------------EXECUTING---------------------------")
        startTime = time.time()
        
        players = self.__initPopulation()
        substitutePlayers = self.__initSubstitutes(players)
        functionEval += self.playerNumber
        
        for kick in range(self.kicksLimit):
            print("Iteration :",kick,"BestEval =",self.globalBestEval,"BestPositions =",self.globalBestPosition)
            self.dataFit.append(self.globalBestEval)
            
            if(self.target != None and self.globalBestEval <= self.target):
                break;
            
            if(functionEval == self.functionEvaluationLimit):
                    break;
            
            potentialBestEval = 10e10000
            potentialBestPosition = []
            
            for player in players:
                
                if np.random.rand() <= self.moveOffProbability:
                    self.__move_off(player)
                    
                    if np.random.rand() <= self.moveForwardAfterMoveOffProbability:
                        self.__move_forward(player)

                else:
                    self.__move_forward(player)
                
                eval = self.__evaluate(player.position)
                functionEval += 1
                
                if eval < player.bestEval:
                    player.bestEval = eval
                    player.bestPosition = player.position.copy()
            
                if eval < potentialBestEval:
                    potentialBestEval = eval
                    potentialBestPosition = player.position.copy()
                
                if(functionEval == self.functionEvaluationLimit):
                    break;
            
            if potentialBestEval < self.globalBestEval:
                self.globalBestEval = potentialBestEval
                self.globalBestPosition = potentialBestPosition.copy()
            
            if np.random.rand() <= self.substitutionProbability:
                playerIndex = np.random.randint(self.playerNumber)
                substituteIndex = np.random.randint(self.substituteNumber)
                
                if substitutePlayers[substituteIndex].bestEval < players[playerIndex].bestEval:
                    players[playerIndex].bestEval = substitutePlayers[substituteIndex].bestEval
                    players[playerIndex].position = substitutePlayers[substituteIndex].bestPosition.copy()
                    players[playerIndex].bestPosition = substitutePlayers[substituteIndex].bestPosition.copy()

            playersSorted = players.copy()
            playersSorted.sort(key=lambda x: x.bestEval)
            
            playerIndex = 0
            for i in range(self.substituteNumber):
                if playersSorted[playerIndex].bestEval < substitutePlayers[i].bestEval:
                    substitutePlayers.insert(i, Player(playersSorted[playerIndex].bestPosition.copy(), playersSorted[playerIndex].bestPosition.copy(), playersSorted[playerIndex].bestEval, playersSorted[playerIndex].numberOfVariables))
                    substitutePlayers.pop()
                    playerIndex += 1
        
        endTime = time.time()
        print("")
        print("Execution Time: %fs" %(endTime-startTime))
        print("Function Evaluations:",functionEval)
        print("------------------------------END------------------------------")
                    
                    
            
    def __initPopulation(self):
        players = []
        self.globalBestEval = 1e1000
    
        
        for i in range(self.playerNumber):
            position = list(np.random.choice([0,1], self.numberOfVariables))
            
            eval = self.__evaluate(position)
            player = Player(position, position, eval, self.numberOfVariables)
            players.append(player)
            
            if player.bestEval < self.globalBestEval:
                self.globalBestEval = player.bestEval
                self.globalBestPosition = player.position.copy()
            
        return players
            
    def __initSubstitutes(self, players):
        substitutes = []
        
        playersSorted = players.copy()
        playersSorted.sort(key=lambda x: x.bestEval)
        
        for player in playersSorted[:self.substituteNumber]:
            substitutes.append(Player(player.bestPosition.copy(), player.bestPosition.copy(), player.bestEval, player.numberOfVariables))
        
        return substitutes
    
    def __evaluate(self, position):
        return Restricao().energy(position)
    
    def __move_off(self, player):
        player.position = list(np.random.choice([0,1], self.numberOfVariables))
    
    def __move_forward(self, player):
        bestPosition = player.bestPosition.copy()
        
        for i in range(self.numberOfVariables):
            if bestPosition[i] == 1:
                d11 = self.cognitiveWeight * np.random.rand()
                d01 = self.cognitiveWeight * np.random.rand() * -1
                d12 = self.socialWeight * np.random.rand()
                d02 = self.socialWeight * np.random.rand() * -1
            else:
                d11 = self.cognitiveWeight * np.random.rand() * -1
                d01 = self.cognitiveWeight * np.random.rand()
                d12 = self.socialWeight * np.random.rand() * -1
                d02 = self.socialWeight * np.random.rand()

            player.v1[i] = (self.inertiaWeight * player.v1[i]) + d11 + d12
            player.v0[i] = (self.inertiaWeight * player.v0[i]) + d01 + d02
            
            if player.position[i] == 0:
                if np.random.rand() < self.__sig(player.v1[i]):
                    player.position[i] = 1
                else:
                    player.position[i] = 0
            else:
                if np.random.rand() < self.__sig(player.v0[i]):
                    player.position[i] = 0
                else:
                    player.position[i] = 1
    
    
    def __sig(self, v):
        return 1 / (1 + (e ** (-v)))