#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
import math
import logging
import ILP as ilpS
import sys
import time
import random as rand
#from docplex.mp.model import Model
#import docplex.mp
#from docplex.cp.model import *
import simpy
import functools
import random as np
import importlib
import csv
import numpy
import matplotlib.pyplot as plt
import pandas as pd
import time
from SGO.SGO import SGO

# ==========================================================
#                        Testes Estáticos
# ==========================================================


from SGO.SGO import SGO

#sgo = SGO(playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfRrh, numberOfVariables, target=target)
#sgo.run()
#sgo.retorno()


# Retornar o Gap
def get_objective_gaps(best_s, bound_s):
	'''
	Obtém os valores numéricos do intervalo entre o valor objetivo e o limite do objetivo.
	Para uma função objetivo única, temos: gap = | value - bound | / max (1e-10, | valor |)
	TODO: Para várias funções objetivo: cada intervalo é o intervalo entre o valor correspondente e o limite. 
	'''
	a = max(best_s, bound_s)
	b = min(best_s, bound_s)
	solution = math.fabs(a - b)/math.fabs(a)#1e-10
	return solution


def countNodes(ilp):
	global act_cloud, act_fog
	for i in range(len(ilp.nodeState)):
		if ilp.nodeState[i] == 1:
			if i == 0:
				act_cloud += 1
			else:
				act_fog += 1
rrhs = []
Atraso = []
Energy = []
gap_list = []
delay_list =[]
trans = []
latencia = []
solve_time = []
Splits_used = []
latencia_relaxed = []
solve_time_relaxed = []
Splits_used_relaxed = []
Energy_relaxed = []
Time = []
randomlist = []


rrhs = []
Atraso = []
Energy = []
EnergyUtil = []
gap_list = []
delay_list =[]
trans = []
latencia = []
solve_time = []
Splits_used = []
latencia_relaxed = []
solve_time_relaxed = []
Splits_used_relaxed = []
Energy_relaxed = []
Time = []
bloqueioFinal = 0.0
activated_nodes = []
Energy_f = []
lambda_usage = []
cloud_use = []
fog_use = []
activated_lambdas = []
fog_lamb_usage = []
cloud_lamb_usage = []
cloud_traffic = []
total_traffic = []
fog_traffic = []
act_cloud = 0
act_fog = 0
count_cloud = []
count_fog = []
cpu = []
bloqueio = []
E_correta = []

Block  = []
Split_E = []
Split_I = []
Split_D = []
Split_B = []
Cloud_traffic = []
Fog_traffic = []
Antenas= []
Traffic_Total = []
solver_time = []

number_of_rrhs = 5
incrementation = 5
epochs = 10 # ---> Aqui vc aumentao total de antenas ativas <--- 
util = ilpS.Util()
a = 0

playerNumber = 22
substituteNumber = 5
kicksLimit = 1000000
functionEvaluationLimit = 10000
numberOfRrh = 50
numberOfVariables = 5
target = 0

for i in range(epochs):
	startTime = time.time()
	total_traffic_cloud=0
	total_traffic_fog = 0
	bloqueio = 0
	count_nodes = 0
	total_trafficl = 0.0
	count_lambdas =0
	split_E = 0
	split_I = 0
	split_D = 0
	split_B = 0
	split_Bl = 0
	print("Execution {} with {} RRHs".format(i, number_of_rrhs))
	Antenas.append(number_of_rrhs)
	Traffic_Total.append(number_of_rrhs*1966)
	sgo = SGO(playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, number_of_rrhs, numberOfVariables, target=target)
	res = sgo.retorno()
	for i in range(len(res)):
		#print(i, res[i])
		try:
			if res[i][:1]==[1]:
				split_E+=1
			if res[i][1:2]==[1]:
				split_I+=1
			if res[i][2:3]==[1]:
				split_D+=1
			if res[i][3:]==[1]:
				split_B+=1
			if res[i][:]==[0, 0, 0, 0]:
				split_Bl +=1

		except:
			pass

		try:
			for j in res[i]:
				#print(j, res[i])
				if res[i].index(1) == 0:
					total_traffic_cloud +=1966
					total_traffic_fog +=0
					#split_E = res[i]
				if res[i].index(1) == 1:
					total_traffic_cloud += 674.4
					total_traffic_fog += 1291.6
					#split_I +=1
				if res[i].index(1) == 2:
					total_traffic_cloud += 119
					total_traffic_fog += 1847
					#split_D +=1
				if res[i].index(1) == 3:
					total_traffic_cloud += 74
					total_traffic_fog += 1892
					#split_B +=1
				bloqueio+=0
				#print(total_traffic_cloud, total_traffic_fog, split_E, split_I, split_D, split_B)
				#print(total_traffic_cloud, total_traffic_fog, split_E)
		except:
			bloqueio+=1966
			continue
		#print(bloqueio, split_E, split_I, split_D, split_B, split_Bl)
	Block.append(bloqueio)
	#print(Block)
	Split_E.append(split_E)
	Split_I.append(split_I)
	Split_D.append(split_D)
	Split_B.append(split_B)
	#print(Split_E)
	Cloud_traffic.append(total_traffic_cloud)
	Fog_traffic.append(total_traffic_fog)
	#print(Cloud_traffic)
	endTime = time.time()
	solver_time.append(endTime-startTime)
	if (a <= 12):
		cpu.append(psutil.cpu_percent())
		number_of_rrhs += incrementation
		#print("Hora:"+str(a)+" cpu Atual: %", psutil.cpu_percent())
	if (a > 12):
		cpu.append(psutil.cpu_percent())
		number_of_rrhs -= incrementation
		#print("Hora:"+str(a)+" cpu Atual: %", psutil.cpu_percent())


numpy.random.seed(1)
dados = pd.DataFrame(data={"Antenas": Antenas, "Cloud_traffic":Cloud_traffic, "Fog_traffic":Fog_traffic,"Traffic_Total":Traffic_Total, "Blocked": Block, "Split_E":Split_E, "Split_I":Split_I, "Split_D":Split_D, "Split_B":Split_B, "CPU_Wastage":cpu})
dados.to_csv("SGO_Static.csv", sep=';',index=False)

