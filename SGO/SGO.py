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
    def __init__(self, playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfRrh, numberOfVariables,
                 target=None, moveOffProbability=0.1, moveForwardAfterMoveOffProbability=0.05, 
                 substitutionProbability=0.1, inertiaWeight=0.191, cognitiveWeight=0.191, socialWeight=0.618):
        self.playerNumber = playerNumber
        self.substituteNumber = substituteNumber
        self.kicksLimit = kicksLimit
        self.functionEvaluationLimit=functionEvaluationLimit
        self.numberOfRrh=numberOfRrh
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
        self.globalBestEval = 10e1000000000000000
        self.globalBestEvals = []
    
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
            print("Evals:",self.globalBestEvals)
            eval,total_cloud,total_fog = self.__evaluate(self.globalBestPosition)
            print("Cloud", total_cloud, "Fog", total_fog)
            self.dataFit.append(self.globalBestEval)
            
            if(self.target != None and self.globalBestEval <= self.target):
                break;
            
            if(functionEval == self.functionEvaluationLimit):
                break;
            
            potentialBestEval = 10e1000000000000000
            potentialBestEvals = []
            potentialBestPosition = []
            
            for player in players:
                
                if np.random.rand() <= self.moveOffProbability:
                    self.__move_off(player)
                    
                    if np.random.rand() <= self.moveForwardAfterMoveOffProbability:
                        self.__move_forward(player)

                else:
                    self.__move_forward(player)
                
                evals,*resto = self.__evaluate(player.position)
                functionEval += 1

                for e in range(len(evals)):
                    if evals[e] < player.bestEvals[e]:
                        player.bestEvals[e] = evals[e]
                        player.bestPosition[e] = player.position[e].copy()
                
                evals,*resto = self.__evaluate(player.bestPosition)
                functionEval += 1
                
                player.bestEvals = evals.copy()

                if player.getBestEval() < potentialBestEval:
                    potentialBestEval = player.getBestEval()
                    potentialBestEvals = player.bestEvals.copy()
                    potentialBestPosition = [pp.copy() for pp in player.bestPosition]
                
                if(functionEval == self.functionEvaluationLimit):
                    break;
            
            if potentialBestEval < self.globalBestEval:
                self.globalBestEval = potentialBestEval
                self.globalBestEvals = potentialBestEvals.copy()
                self.globalBestPosition = [pp.copy() for pp in potentialBestPosition]
            
            if np.random.rand() <= self.substitutionProbability:
                playerIndex = np.random.randint(self.playerNumber)
                substituteIndex = np.random.randint(self.substituteNumber)
                
                if substitutePlayers[substituteIndex].getBestEval() < players[playerIndex].getBestEval():
                    players[playerIndex].bestEvals = substitutePlayers[substituteIndex].bestEvals.copy()
                    players[playerIndex].position = [pp.copy() for pp in substitutePlayers[substituteIndex].bestPosition]
                    players[playerIndex].bestPosition = [pp.copy() for pp in substitutePlayers[substituteIndex].bestPosition]

            playersSorted = players.copy()
            playersSorted.sort(key=lambda x: x.getBestEval())
            
            playerIndex = 0
            for i in range(self.substituteNumber):
                if playersSorted[playerIndex].getBestEval() < substitutePlayers[i].getBestEval():
                    substitutePlayers.insert(i, Player([pp.copy() for pp in playersSorted[playerIndex].bestPosition], [pp.copy() for pp in playersSorted[playerIndex].bestPosition], playersSorted[playerIndex].bestEvals.copy(), playersSorted[playerIndex].numberOfRrh, playersSorted[playerIndex].numberOfVariables))
                    substitutePlayers.pop()
                    playerIndex += 1        

        total = self.globalBestPosition
        #print(total)
        for t in range(len(total)):
            #Node_id = total[t][0:3]
            #Lambda_id = total[t][3:11]
            Split_id = total[t][0:4]
            print("Split_ID {}; and Antenas {}".format(Split_id, t))


        endTime = time.time()
        print("")
        print("Execution Time: %fs" %(endTime-startTime))
        print("Function Evaluations:",functionEval)
        print("------------------------------END------------------------------")
                    
                    
            
    def __initPopulation(self):
        players = []
        self.globalBestEval = 10e1000000000000000
    
        
        for i in range(self.playerNumber):
            position = [list(np.random.choice([0,1], self.numberOfVariables)) for x in range(self.numberOfRrh)]
            
            for x in range(self.numberOfRrh):
                position[x][0] = 1
            
            evals,*resto = self.__evaluate(position)
            player = Player([pp.copy() for pp in position], [pp.copy() for pp in position], evals.copy(), self.numberOfRrh, self.numberOfVariables)
            players.append(player)
            
            if player.getBestEval() < self.globalBestEval:
                self.globalBestEval = player.getBestEval()
                self.globalBestEvals = player.bestEvals.copy()
                self.globalBestPosition = [pp.copy() for pp in player.position]
            
        return players
            
    def __initSubstitutes(self, players):
        substitutes = []
        
        playersSorted = players.copy()
        playersSorted.sort(key=lambda x: x.getBestEval())
        
        for player in playersSorted[:self.substituteNumber]:
            substitutes.append(Player([pp.copy() for pp in player.bestPosition], [pp.copy() for pp in player.bestPosition], player.bestEvals.copy(), player.numberOfRrh, player.numberOfVariables))
        
        return substitutes
    
    def __evaluate(self, position):
        evals = []
        
        total_traffic_cloud = 0
        total_traffic_fog = 0
        
        for x in range(self.numberOfRrh):
            eval, total_traffic_cloud, total_traffic_fog = Restricao().energy(total_traffic_cloud, total_traffic_fog, position[x])
            evals.append(eval)
                         
        return evals, total_traffic_cloud, total_traffic_fog
    
    def __move_off(self, player):
        #player.position = list(np.random.choice([0,1], self.numberOfVariables))
        
        for x in range(self.numberOfRrh):
            for y in range(self.numberOfVariables):
                if np.random.rand() < 0.5:
                    if player.position[x][y] == 1:
                        player.position[x][y] = 0
                    else:
                        player.position[x][y] = 1
        
        for x in range(self.numberOfRrh):
            if player.position[x].count(1) == 0:
                player.position[x][0] = 1
    
    def __move_forward(self, player):
        bestPosition = player.bestPosition.copy()
        
        for i in range(self.numberOfRrh):
            for j in range(self.numberOfVariables):
                if bestPosition[i][j] == 1:
                    d11 = self.cognitiveWeight * np.random.rand()
                    d01 = self.cognitiveWeight * np.random.rand() * -1
                    d12 = self.socialWeight * np.random.rand()
                    d02 = self.socialWeight * np.random.rand() * -1
                else:
                    d11 = self.cognitiveWeight * np.random.rand() * -1
                    d01 = self.cognitiveWeight * np.random.rand()
                    d12 = self.socialWeight * np.random.rand() * -1
                    d02 = self.socialWeight * np.random.rand()

                player.v1[i][j] = (self.inertiaWeight * player.v1[i][j]) + d11 + d12
                player.v0[i][j] = (self.inertiaWeight * player.v0[i][j]) + d01 + d02
                
                if player.position[i][j] == 0:
                    if np.random.rand() < self.__sig(player.v1[i][j]):
                        player.position[i][j] = 1
                    else:
                        player.position[i][j] = 0
                else:
                    if np.random.rand() < self.__sig(player.v0[i][j]):
                        player.position[i][j] = 0
                    else:
                        player.position[i][j] = 1
            
            
            if player.position[i].count(1) == 0:
                player.position[i][0] = 1
    
    
    def __sig(self, v):
        return 1 / (1 + (e ** (-v)))
