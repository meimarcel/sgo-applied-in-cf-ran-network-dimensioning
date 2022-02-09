#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil
import math
import logging
import ILP as ilpS
import sys
import time
import random as rand
from docplex.mp.model import Model
import docplex.mp
from docplex.cp.model import *
import simpy
import functools
import random as np
import importlib
import csv
import numpy
import matplotlib.pyplot as plt
import pandas as pd
import time

# ==========================================================
#                        Testes Estáticos
# ==========================================================
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




number_of_rrhs = 5
incrementation = 5
epochs = 8 # ---> Aqui vc aumentao total de antenas ativas <--- 
util = ilpS.Util()
a = 0

for i in range(epochs):
	count_nodes = 0
	total_trafficl = 0.0
	count_lambdas = 0
	print("Execution {} with {} RRHs".format(i, number_of_rrhs))
	antenas = util.newCreateRRHs(number_of_rrhs)
	np.shuffle(antenas)
	ilp = ilpS.ILP(antenas, range(len(antenas)), ilpS.nodes, ilpS.lambdas, ilpS.Split)
	solution = ilp.run()
	solution_values = ilp.return_solution_values()
	ilp.print_var_values()
	ilp.updateValues(solution_values)
	ilp.update_splits(solution_values)
	Time.append(i)
	#solu = ilp.return_solution_values()
	delay_list.append(ilp.Latencia(solution_values))
	fog = ilp.Fog_Band(solution_values)
	fog_traffic.append(fog)
	total_trafficl = (number_of_rrhs *1966)
	total_traffic.append(total_trafficl)
	#ilp.mdl.print_information()
	#print("/n")
	cost = util.getPowerConsumption()
	E_correta.append(cost)
	rrhs.append(number_of_rrhs)
	count_nodes = 0
	Energy.append(solution.objective_value)
	solve_time.append(solution.solve_details.time)
	print("============================ /n")
	Atraso.append(ilp.Latencia(solution_values))
	#print(delay_list)

	#print("Gap Value: {}".format(get_objective_gaps(solution.objective_value, solution2.objective_value)))
	#gap = get_objective_gaps(solution.objective_value, solution2.objective_value)
	#gap2 = gap*100
	#print("Gap: {}%".format(gap2))
	#gap_list.append(gap2)
	#print(gap_list)

	countNodes(ilpS)
	for i in ilpS.nodeState:
		if i == 1:
			count_nodes += 1
	activated_nodes.append(count_nodes)
	for i in ilpS.lambda_state:
		if i == 1:
			count_lambdas += 1
	activated_lambdas.append(count_lambdas)
	if count_lambdas >0:
		if total_trafficl > 0 and total_trafficl > (count_lambdas * 10000.0):
			bloqueioFinal = total_trafficl - (count_lambdas * 10000.0)
			bloqueio.append(math.ceil(bloqueioFinal / 1966))
		else:
			bloqueio.append(0)
	else:
		bloqueio.append(0)
	if count_lambdas > 0:
		lambda_usage.append((number_of_rrhs*1966)/(count_lambdas*10000.0))
	else:
		lambda_usage.append(0)
	if act_cloud:
		cloud_use.append(act_cloud)
	else:
		cloud_use.append(0)
	act_cloud = 0
	if act_fog and fog > 0:
		fog_use.append(act_fog)
	else:
		fog_use.append(0)
	act_fog = 0
	importlib.reload(ilpS)
	#number_of_rrhs += incrementation
	a +=1
	print(a)
	if (a <= 12):
		cpu.append(psutil.cpu_percent())
		number_of_rrhs += incrementation
		#print("Hora:"+str(a)+" cpu Atual: %", psutil.cpu_percent())
	if (a > 12):
		cpu.append(psutil.cpu_percent())
		number_of_rrhs -= incrementation
		#print("Hora:"+str(a)+" cpu Atual: %", psutil.cpu_percent())

numpy.random.seed(1)
dados = pd.DataFrame(data={"Time": Time, "RRHs_ativos" : rrhs, "Energy_OS": Energy, "Solve_time_OS" : solve_time, "Cloud_use": cloud_use, "Fog_Use": fog_use, "Lambdas":activated_lambdas, "Fog_traffic": fog_traffic, "Total_Traffic":total_traffic, "Lambda_usage":lambda_usage, "Atraso" : Atraso, "Energia_correta": E_correta, "Bloqued": bloqueio, "Activated_nodes":activated_nodes, "CPU_Wastage":cpu})
dados.to_csv("static_r.csv", sep=';',index=False)

