#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import logging
#import cplex
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
import pandas as pd

# Bloqueio para o restante sobrante. 1 req = 614.4
#total traffic resto da divisão por req = req bloq
# ==============================
__author__ = 'Matias Romário'
__email__ = "matiasrps@ufba.br/matiasromario@ieee.org"
__version__ = '3.0'
# ==============================

act_cloud = 0
act_fog = 0
act_lambda = 0

fog_delay = 0.0000980654 # 10km
#cloud_delay = 0.0001961308 # 20 km
#fog_delay = 0.000024516 # 5 km
cloud_delay = 0.000049033 # 10km 0,000033356
ONU_delay = 0.0000016 # 1,6 µs
LC_delay = 0.0000015 # 1,5 µs 0.000069283

# Taxa CPRI 
Band = 1000000 #Very big Num
#cpri = [614.4, 122.88, 460.8, 552.96, 0] # Valores do tráfego por split

cpri = [1966, 74, 119, 674.4] 


#Use case: One-way latency DL bandwidth UL bandwidth.Source: 159_functional_splits_and_use_cases_for_sc_virtualization.pdf
#Latency_Req = [0.000050967, 0.000450967, 0.000450967, 0.001450967] # 1 ->C-RAN; 2 -> PHY; 3-> Split MAC ; 4-> PDCP-RLC. 0.00025 - cl_delay
Latency_Req = [0.0001, 0.0025, 0.0005, 0.00045] # 1 ->C-RAN; 2 -> PHY; 3-> Split MAC ; 4-> PDCP-RLC. 0.00025 - cl_delay
#Delay = [0.000049033, 0.000024516,0.000024516, 0.00098065, 0.00098065, 0.000049033, 0.000049033, 0.000049033]#Atraso de nó # Real
Delay = [0.000067033, 0.000024516,0.000024516, 0.000024516, 0.000024516]#Atraso de nó

cpri_rate = 614.4 # Taxa CPRI
wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0,10000.0, 10000.0, 10000.0, 10000.0, 10000.0]
lambda_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]

switch_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
rrhs_on_nodes = [0,0,0,0,0,0,0]
#Amount_onus = []
split_state = [0,0,0,0,0,0,0,0]


# rrhs
rrhs = range(0,1)
# total de nós 
nodes = range(0, 3)#4
#Total de Split
Split= range(0, 4) # São 4
# total de lambdas
#lambdas = range(0, 8)
lambdas = range(0, 9)
node_capacity = [40000, 20000, 20000, 10000, 9830.4] # Para o CPRI
#node_capacity = [78640, 29490, 29490, 29490, 9830.4] # Novo - 40 rrhs no CPRI 0
#node_capacity = [60000, 10000, 10000, 10000, 10000]#cf-ran and split
#node_capacity = [60000, 0]
proc_delay = [0.00001, 0.00002, 0.00002, 0.00002, 0.00002]


# Custo dos Nós
nodeCost = [600.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0]
# Custo do line card
lc_cost = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
# Custo split
s_cost = [0.0, 20.0, 15.0, 10.0, 5.0]
#Custo por Onu ativada
Onu_cost = 7.7
RRH_cost = 20
nodeState = [0,0,0,0,0,0,0]

lambda_node = [
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
]


#Classe ILP
class ILP(object):

	# Iniciando
	def __init__(self, rrh, rrhs, nodes, lambdas, Split):
		self.rrh = rrh
		self.fog = []
		for i in rrh:
			self.fog.append(i.rrhs_matrix)
		self.rrhs = rrhs
		self.nodes = nodes
		self.lambdas = lambdas
		self.Split = Split

	def run(self):
		self.buildModel()
		sol = self.solveILP()
		return sol

	#Roteiro de execução
	def run_relaxed(self):
		self.buildModel_relaxed()
		sol = self.solveILP()
		return sol


	# Construção do modelo inteior
	def buildModel(self):
		self.mdl = Model()

		cpx = self.mdl.get_engine().get_cplex()
		#================ Variáveis de decisão ================
		self.x = self.mdl.binary_var_dict([(i,j,w,s) for i in self.rrhs for j in self.nodes for w in self.lambdas for s in self.Split], name = 'Rrh/Node/Lambda/Split: ')
		self.k = self.mdl.binary_var_dict([(w, j, s) for w in self.lambdas for j in self.nodes for s in self.Split], name = 'Lambda/Nonde/Split: ')
		self.y = self.mdl.binary_var_dict([(i,j) for i in self.rrhs for j in self.nodes], name = 'RRH/Node: ')
		self.xn = self.mdl.binary_var_dict([(j) for j in self.nodes], name = 'Node activated: ')
		self.z = self.mdl.binary_var_dict([(w, j) for w in self.lambdas for j in self.nodes], name = 'Lambda/Node: ')
		self.t = self.mdl.binary_var_dict([(i,j,s) for i in self.rrhs for j in self.nodes for s in self.Split], name = 'RRH/Node/Split: ')
		self.s = self.mdl.binary_var_dict([(i,s) for i in self.rrhs for s in self.Split], name = 'Rhh/Split: ')
		self.g = self.mdl.binary_var_dict([(i,j,w,s) for i in self.rrhs for j in self.nodes for w in self.lambdas for s in self.Split], name = 'Redirections: ')
		self.e = self.mdl.binary_var_dict([(j) for j in self.nodes], name = "Switch/Node")



	# ================ Constraints desenhadas ================
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w,s] for j in self.nodes for w in self.lambdas for s in self.Split) == 2 for i in self.rrhs) # 2 VPONs
		self.mdl.add_constraints(self.mdl.sum(self.z[w,j] for j in self.nodes) <= 1 for w in self.lambdas) # Um nó por Lâmbda
		#self.mdl.add_constraints(self.mdl.sum(self.z[w,j] for w in self.lambdas)<= self.xn[j] for j in self.nodes)
		self.mdl.add_constraints(self.mdl.sum(self.s[i,s] for s in self.Split) == 1 for i in self.rrhs) # 1 Split iguais por rrh
		self.mdl.add_constraints(self.mdl.sum(self.y[i,j] for j in self.nodes) == 2 for i in self.rrhs)# serão dois nós por rrhs
		self.mdl.add_constraints(self.mdl.sum(self.y[i,j] for j in self.nodes[0:1]) == 1 for i in self.rrhs)# 1 obrigatoriamente na nuvem
		self.mdl.add_constraints(self.y[i,0] == 1 for i in self.rrhs) # invés do for
		self.mdl.add_constraints(self.t[i,j,s] <= self.mdl.sum(self.s[i,s]) for s in self.Split for j in self.nodes for i in self.rrhs)
		self.mdl.add_constraints(self.t[i,j,s] == self.mdl.sum(self.x[i,j,w,s] for w in self.lambdas) for w in self.lambdas for j in self.nodes for i in self.rrhs for s in self.Split)

		
		#Restrições de Capacidade de Banda - Restrições para quebra do CPRI - nó 0 é nuvem e nó 1 é fog
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w,s] * cpri[s] for s in self.Split for i in self.rrhs for j in self.nodes[0:1]) <= wavelength_capacity[w] for w in self.lambdas) 
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w,s] * (cpri[0] - cpri[s]) for s in self.Split for i in self.rrhs for j in self.nodes[1:]) <= wavelength_capacity[w] for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w,s] * cpri[s] for s in self.Split for i in self.rrhs for w in self.lambdas) <= node_capacity[j] for j in self.nodes[0:1]) # Nó zero pega a parte da cpri com split
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w,s] * (cpri[0] - cpri[s]) for s in self.Split for i in self.rrhs for w in self.lambdas) <= node_capacity[j] for j in self.nodes[1:])# nó de fog pega o remanescente


		self.mdl.add_constraints(Band*self.xn[j] >= self.mdl.sum(self.x[i,j,w,s] for s in self.Split for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(self.xn[j] <= self.mdl.sum(self.x[i,j,w,s] for s in self.Split for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(Band*self.z[w,j] >= self.mdl.sum(self.x[i,j,w,s] for s in self.Split for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.z[w,j] <= self.mdl.sum(self.x[i,j,w,s] for s in self.Split for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(Band*self.y[i,j] >= self.mdl.sum(self.x[i,j,w,s] for s in self.Split for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		#self.mdl.add_constraints(self.z[w,j] <= lambda_node[w][j] for w in self.lambdas for j in self.nodes)

		#Switch node
		self.mdl.add_constraints(Band*self.e[j] >= self.mdl.sum(self.y[i,j] for i in self.rrhs) for j in self.nodes)
		self.mdl.add_constraints(self.e[j] <= self.mdl.sum(self.y[i,j] for i in self.rrhs)  for j in self.nodes)


	#================ Solver ================
	def solveILP(self):
		self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes) + self.mdl.sum(self.z[w,j] * lc_cost[w] for w in self.lambdas for j in self.nodes) + self.mdl.sum(self.s[i,s] * s_cost[s] for s in self.Split for i in self.rrhs))

		#self.sol = self.mdl.solve(log_output=True) #- Mostra o relatório de gap
		self.mdl.parameters.lpmethod = 6
		self.mdl.parameters.timelimit = 500
		self.sol = self.mdl.solve()
		#self.sol.display()
		#self.sol = self.mdl.solve(log_output=True)
		#self.mdl.print_information()
		return self.sol




	#printar valores de variáveis
	def print_var_values(self):

		for i in self.x:
			if self.x[i].solution_value >= 1:
				print("{} is {}".format(self.x[i], self.x[i].solution_value))

		for i in self.s:
			if self.s[i].solution_value >= 1:
				print("{} is {}".format(self.s[i], self.s[i].solution_value))

		for i in self.k:
			if self.k[i].solution_value >= 1:
				print("{} is {}".format(self.k[i], self.k[i].solution_value))

		for i in self.t:
			if self.t[i].solution_value >= 1:
				print("{} is {}".format(self.t[i], self.t[i].solution_value))

		for i in self.y:
			if self.y[i].solution_value >= 1:
				print("{} is {}".format(self.y[i], self.y[i].solution_value))

		for i in self.xn:
			if self.xn[i].solution_value >= 1:
				print("{} is {}".format(self.xn[i], self.xn[i].solution_value))

		for i in self.z:
			if self.z[i].solution_value >= 1:
				print("{} is {}".format(self.z[i], self.z[i].solution_value))

		for i in self.e:
			if self.e[i].solution_value >= 1:
				print("{} is {}".format(self.e[i], self.e[i].solution_value))

		for i in self.g:
			if self.g[i].solution_value >= 1:
				print("{} is {}".format(self.g[i], self.g[i].solution_value))



	#print
	def print_var_values_relaxed(self):
		for i in self.x:
			if self.x[i].solution_value >0:
				#self.x[i].solution_value == 1.0
				print("{} is {}".format(self.x[i], self.x[i].solution_value))

		for i in self.s:
			if self.s[i].solution_value >0:
				print("{} is {}".format(self.s[i], self.s[i].solution_value))
				#self.s[i].solution_value == round(self.s[i].solution_value,2)
				#print("{} is {}".format(self.s[i], round(self.s[i].solution_value,2)))

		for i in self.k:
			if self.k[i].solution_value >0:
				print("{} is {}".format(self.k[i], self.k[i].solution_value))

		for i in self.t:
			if self.t[i].solution_value >0:
				#self.t[i].update(1.0)
				print("{} is {}".format(self.t[i], self.t[i].solution_value))
				#print("{} is {}".format(self.t[i], round(self.t[i].solution_value,2)))

		for i in self.g:
			if self.g[i].solution_value >0:
				print("{} is {}".format(self.g[i], self.g[i].solution_value))

		for i in self.y:
			if self.y[i].solution_value >0:
				print("{} is {}".format(self.y[i], self.y[i].solution_value))
				#print("{} is {}".format(self.y[i], round(self.y[i].solution_value,2)))

		for i in self.e:
			if self.e[i].solution_value >0:
				print("{} is {}".format(self.e[i], self.e[i].solution_value))

		for i in self.xn:
			if self.xn[i].solution_value >0:
				print("{} is {}".format(self.xn[i], self.xn[i].solution_value))

		for i in self.z:
			if self.z[i].solution_value >0:
				print("{} is {}".format(self.z[i], self.z[i].solution_value))


	# Retornar valores
	def return_solution_values(self):
		self.var_x = []
		self.var_y = []
		self.var_xn = []
		self.var_k = []
		self.var_s = []
		self.var_t = []
		self.var_z = []
		self.var_e = []
		self.var_g = []

		for i in self.x:
			if self.x[i].solution_value >= 1:
				self.var_x.append(i)

		for i in self.k:
			if self.k[i].solution_value >= 1:
				self.var_k.append(i)

		for i in self.y:
			if self.y[i].solution_value >= 1:
				self.var_y.append(i)

		for i in self.xn:
			if self.xn[i].solution_value >= 1:
				self.var_xn.append(i)

		for i in self.s:
			if self.s[i].solution_value >= 1:
				self.var_s.append(i)

		for i in self.t:
			if self.t[i].solution_value >= 1:
				self.var_t.append(i)

		for i in self.z:
			if self.z[i].solution_value >= 1:
				self.var_z.append(i)

		for i in self.e:
			if self.e[i].solution_value >= 1:
				self.var_e.append(i)

		for i in self.g:
			if self.g[i].solution_value >= 1:
				self.var_g.append(i)


		solution = Solution(self.var_x, self.var_z, self.var_k, self.var_s, self.var_y, self.var_xn, self.var_t, self.var_g, self.var_e)
		return solution

	# Retornar relaxações1
	def return_solution_values_relaxed(self):
		self.var_x = []
		self.var_u = []
		self.var_y = []
		self.var_xn = []
		self.var_g = []
		self.var_k = []
		self.var_s = []
		self.var_t = []
		self.var_z = []
		#self.var_u = []
		self.var_g = []
		self.var_e = []


		for i in self.x:
			if self.x[i].solution_value > 0:
				self.var_x.append(i)

		for i in self.k:
			if self.k[i].solution_value > 0:
				self.var_k.append(i)

		for i in self.t:
			if self.t[i].solution_value > 0:
				self.var_t.append(i)

		for i in self.y:
			if self.y[i].solution_value > 0:
				self.var_y.append(i)

		for i in self.xn:
			if self.xn[i].solution_value > 0:
				self.var_xn.append(i)

		for i in self.s:
			if self.s[i].solution_value > 0:
				self.var_s.append(i)

		for i in self.e:
			if self.e[i].solution_value > 0:
				self.var_e.append(i)

		for i in self.g:
			if self.g[i].solution_value > 0:
				self.var_g.append(i)

		for i in self.t:
			if self.t[i].solution_value > 0:
				self.var_t.append(i)

		for i in self.z:
			if self.z[i].solution_value > 0:
				self.var_z.append(i)

		solution = Solution(self.var_x, self.var_z, self.var_k, self.var_s, self.var_y, self.var_xn, self.var_t, self.var_g, self.var_e)
		return solution



	# Função para verificar os resultados gerados em cada interação 0.0, 5.0, 4.0, 3.0, 2.0, 1.0
	def updateValues(self, solution):
		self.updateRRH(solution)
		for key in solution.var_x:
			node_id = key[1]
			lambda_id = key[2]
			split_id = key[3]
			rrhs_on_nodes[node_id] += 1
			if nodeState[node_id] == 0:
				nodeState[node_id] = 1
			if lambda_state[lambda_id] == 0:
				#delay_tot += LC_Delay
				lambda_state[lambda_id] = 1
			if split_state[split_id] == 0:
				split_state[split_id] = 1

	
	def update_splits(self, solution):
		self.updateRRH(solution)
		for i in solution.var_x:
			node_id = i[1]
			lambda_id = i[2]
			split_id = i[3]
			if split_id == 0 and node_id >=1:
				rrhs_on_nodes[node_id] -= 1
				if len(range(rrhs_on_nodes[node_id])) <= 0:
					nodeState[node_id] = 0
				if len(range(rrhs_on_nodes[node_id])) <= 0 and lambda_state[lambda_id] == 1 and wavelength_capacity[lambda_id] == 10000.0:
					split_state[split_id] = 0
					lambda_state[lambda_id] = 0
			if split_id == 7 and node_id ==0:
				rrhs_on_nodes[node_id] -= 1
				if len(range(rrhs_on_nodes[node_id])) == 0:
					nodeState[node_id] = 0
				if lambda_state[lambda_id] == 1 and wavelength_capacity[lambda_id] == 10000.0:
					split_state[split_id] = 0
					lambda_state[lambda_id] = 0
			else:
				pass



	# Banda direcionada para a Nuvem
	def Cloud_Band(self,solution):
		self.updateRRH(solution)
		total_traffic = 0.0
		for key in solution.var_x:
			node_id = key[1]
			split_id = key[3]
			if nodeState[node_id] ==1:
				if node_id == 0:
					total_traffic += cpri[split_id]
		return total_traffic

	def Fog_Band(self,solution):
		total_traffic = 0.0
		self.updateRRH(solution)
		for key in solution.var_x:
			node_id = key[1]
			split_id = key[3]
			if nodeState[node_id] ==1:
				if node_id >= 1:
					total_traffic += (cpri[0] - cpri[split_id])
		return total_traffic

	#put the solution values into the RRH
	def updateRRH(self,solution):
			for i in range(len(self.rrh)):
				self.rrh[i].var_x = solution.var_x[i]
				#self.rrh[i].var_t = solution.var_t[i]


	def deallocateRRH(self, rrh):
		#take the decision variables on the rrh and release the resources
		#take the node, lambda and DU
		node_id = rrh.var_x[1]
		rrhs_on_nodes[node_id] -= 1
		lambda_id = rrh.var_x[2]
		split_id = rrh.var_x[3]
		#wavelength_capacity[lambda_id] += cpri_rate
		#find the wavelength
		if node_id <= 0:
			wavelength_capacity[lambda_id] += cpri[split_id]
		else:
			wavelength_capacity[lambda_id] += (cpri[0]-cpri[split_id])
		if wavelength_capacity[lambda_id] == 10000.0 and lambda_state[lambda_id] == 1:
			lambda_state[lambda_id] = 0
			lc_cost[lambda_id] = 20.0
			for i in range(len(lambda_node[lambda_id])):
				lambda_node[lambda_id][i] = 1
		if switchBandwidth[node_id] == 10000.0 and switch_state[node_id] == 1:
			switch_state[node_id] = 0
			switch_cost[node_id] = 15.0
		if rrhs_on_nodes[node_id] == 0 and nodeState[node_id] == 1:
			nodeState[node_id] = 0
			if node_id == 0:
				nodeCost[node_id] = 600.0
			else:
				nodeCost[node_id] = 500.0
		#print("RRH {} was deallocated".format(rrh.id))
		#if split_state[split_id] == 1 and 

	# Matias novo
	def Delay_total(self, solution):
		total_delay = 0.0
		transmission_delay = 0.0
		object_delay = 0.0
		object2_delay = 0.0
		transport = 0
		#onu_delay = 0.0
		lc_delay = 0.0
		#Latency_Req = [0.00025, 0.4, 0.03, 0.002, 0.006, 0.008] # 1 ->C-RAN; 2 -> PHY; 3-> Split MAC ; 4-> PDCP-RLC.
		count_lambdas = 0
		lan = []
		lat_tot = 0.0
		count = 1
		rrhs = 0
		total_delay_f = 0
		for s in solution.var_x:
			rrh = s[0]
			node = s[1]
			wavelenght = s[2]
			split = s[3]
			if node == 0 and nodeState[node] ==1:
				if rrh >=0:
					rrhs =1 + rrhs
				else:
					rrhs = 0
				transport = (rrhs*ONU_delay) /18
		#print("transpote: {}".format(transport))
		for key in solution.var_xn:
			#print(key)
			if key == 0 and nodeState[key] ==1:
				transmission_delay = cloud_delay
		for t in solution.var_z:
			lambda_id = t[0]
			if lambda_id >= 0:
				object2_delay += LC_delay
			else:
				pass
		total_delay_f = object2_delay + transmission_delay + transport
		return total_delay_f
		#return onu_delay + object2_delay + transmission_delay




	#reset the values of the entry parameters
	def resetValues(self):
		global rrhs_on_nodes, lambda_node, du_processing, du_state, nodeState, nodeCost, du_cost, lc_cost, switchBandwidth, switch_cost 
		global wavelength_capacity, lambda_state, switch_state
		#to keep the amount of RRHs being processed on each node

		# Taxa CPRI 
		Band = 1000000 #Very big Num
		cpri = [614.4, 122.88, 184.32, 215.04, 307.2, 552.96, 491.52, 460.8] # Valores do tráfego por split

		#Use case: One-way latency DL bandwidth UL bandwidth.Source: 159_functional_splits_and_use_cases_for_sc_virtualization.pdf
		Latency_Req = [0.025, 0.4, 0.03, 0.02, 0.06, 0.08] # 1 ->C-RAN; 2 -> PHY; 3-> Split MAC ; 4-> PDCP-RLC.
		Delay = [0.000392262, 0.000098065,0.000098065, 0.00098065, 0.00098065, 0.000049033, 0.000049033, 0.000049033]#Atraso de nó
		DL_bandwidth = [1075, 152, 152, 151] # Source - https://scf.io/en/theme_documents/Virtualization.php
		cpri_rate = 614.4 # Taxa CPRI

		wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0,10000.0, 10000.0, 10000.0, 10000.0, 10000.0]
		lambda_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]

		fog_delay = 0.0000980654 # 10km
		cloud_delay = 0.0001961308 # 20 km
		#fog_delay = 0.0001961308 # 20 km
		#cloud_delay = 0.000392262 # 40km
		ONU_delay = 0.0000075 # 7,5 µs
		LC_delay = 0.0000015 # 1,5 µs

		switch_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		rrhs_on_nodes = [0,0,0,0,0,0,0]
		split_state = [0,0,0,0,0,0,0,0]
		# rrhs
		rrhs = range(0,1)
		# total de nós #TODO resolver conflito ao aumentar os nós
		nodes = range(0, 6)
		#Total de Split TODO: precisa de ajuste
		Split= range(1, 6)
		# total de lambdas
		lambdas = range(0, 15)
		#node_capacity = [39321.6, 9830.4, 9830.4, 9830.4, 9830.4, 9830.4, 9830.4, 9830.4, 9830.4]
		node_capacity = [58982.4, 19660.8, 19660.8, 19660.8, 19660.8, 19660.8, 19660.8] #96 cloud; 16 fog
		#node_capacity = [29491.2, 9830.4, 9830.4, 9830.4, 9830.4]

		# Custo dos Nós
		nodeCost = [600.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0, 300.0]
		# Custo do line card
		lc_cost = [20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]
		# Custo split
		s_cost = [0.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0]
		#Custo por Onu ativada
		Onu_cost = 7.7
		RRH_cost = 20
		nodeState = [0,0,0,0,0,0,0]

		lambda_node = [
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		[1,1,1,1,1,1],
		]


	def Latencia(self, solution):
		total_delay = 0.0
		transmission_delay = 0.0
		object_delay = 0.0
		object2_delay = 0.0
		onu_delay = 0.0
		lc_delay = 0.0
		Latency_Req = [0.00025, 0.4, 0.03, 0.002, 0.006, 0.008] # 1 ->C-RAN; 2 -> PHY; 3-> Split MAC ; 4-> PDCP-RLC.
		count_lambdas = 0
		lan = []
		lat_tot = 0.0
		count = 1
		for key in solution.var_xn:
			#print(key)
			if key == 0 and nodeState[key] ==1:
				total_delay = cloud_delay
			#if key >=1 and nodeState[key]==1:
				#total_delay += fog_delay
		#print("Total de nós: {}".format(len(solution.var_xn)))
		if len(solution.var_xn) == 0:
			transmission_delay = 0
		else:
			transmission_delay = total_delay/len(solution.var_xn)
		#print("latencia de transmissão: {}".format(transmission_delay))
		for i in solution.var_x:
			rrh_id = i[0]
			#lambda_id = i[2]
			split_id = i[3]
			if rrh_id >=0:
				onu_delay += (ONU_delay/10)
		for t in solution.var_z:
			lambda_id = t[0]
			if lambda_id >= 0:
				object2_delay = LC_delay + object2_delay
		#print(lambda_id)
		Ativation_delay =  object2_delay + onu_delay
		if len(solution.var_xn) == 0:
			object_delay = 0
		else:
			object_delay = onu_delay/(len(solution.var_x))
		#print("total da solução x {}".format(len(solution.var_x)))
		#print("Atraso onu: {}".format(object_delay))
		#print("Atraso de ativação {}".format(Ativation_delay))
		#print("Latência atual = {} do Split {} e Latência da Split {}".format(object_delay + object2_delay + transmission_delay, split_id, Latency_Req[split_id]))
		#print("Sobra da latência {}".format(Latency_Req[split_id] - (object_delay + object2_delay + transmission_delay)))
		return object_delay + object2_delay + transmission_delay



	#
	def Latencia_trans(self, solution):
		total_delay = 0.0
		transmission_delay = 0.0
		Latency_Req = [0.00025, 0.4, 0.03, 0.002, 0.006, 0.008] # 1 ->C-RAN; 2 -> PHY; 3-> Split MAC ; 4-> PDCP-RLC.
		if range(len(solution.var_xn)) == 0:
			transmission_delay = 0
		for key in solution.var_xn:
			#print(key)
			if key == 0 and nodeState[key] ==1:
				total_delay = cloud_delay
			if key >=1 and nodeState[key]==1:
				total_delay += fog_delay
		#print("Total de nós: {}".format(len(solution.var_xn)))
		if len(solution.var_xn) == 0:
			transmission_delay == 0
		else:
			transmission_delay = total_delay/len(solution.var_xn)
		#print("latencia de transmissão: {}".format(transmission_delay))
		return transmission_delay





# Encapsula os valores da solução
class Solution(object):
	def __init__(self, var_x, var_z, var_s, var_y, var_t, var_xn, var_k, var_e, var_g):
		self.var_k = var_k
		self.var_x = var_x
		self.var_xn = var_xn
		self.var_s = var_s
		self.var_t = var_t
		self.var_y = var_y
		self.var_z = var_z
		self.var_g = var_g
		#self.var_u = var_u
		self.var_e = var_e



class RRH(object):
	def __init__(self, aId, rrhs_matrix):
		self.id = aId
		self.rrhs_matrix = rrhs_matrix
		self.var_xy = None
		self.var_u = None


# Classe para gerar os logs. TODO: anteção aos update dos valores
class Util(object):
	def countRrhs(self):
		global total_cloud
		for i in range(len(nodeState)):
			if nodeState[i] == 1:
				if i == 0:
					total_cloud = rrhs_on_nodes[0]*cpri_rate
				else:
					total_cloud =0
				return total_cloud


	# criar uma lista de RRHs com seus próprios nós de processamento conectados
	def newCreateRRHs(self, amount):
		rrhs = []
		for i in range(amount):
			r = RRH(i, [1,0,0,0,0,0])
			rrhs.append(r)
		self.setMatrix(rrhs)
		return rrhs

	# define o rrhs_matrix para cada rrh criado
	def setMatrix(self, rrhs):
		count = 1
		for r in rrhs:
			if count <= len(r.rrhs_matrix)-1:
				r.rrhs_matrix[count] = 1
				count += 1
			else:
				count = 1
				r.rrhs_matrix[count] = 1
				count += 1

	#compute the power consumption at the moment
	def getPowerConsumption(self):
		netCost = 0.0
		#compute all activated nodes
		for i in range(len(nodeState)):
			if nodeState[i] == 1:
				if i == 0:
					netCost += 600.0
				else:
					netCost += 300.0
		for w in lambda_state:
			if w == 1:
				netCost += 20.0
		for s in switch_state:
			if s == 1:
				netCost += 15.0
		return netCost

	def countNodes(self):
		global act_cloud, act_fog
		for i in range(len(nodeState)):
			if nodeState[i] == 1:
				if i == 0:
					act_cloud += 1
				else:
					act_fog += 1
		return act_fog

	def countlambdas(self):
		global act_lambda
		for i in range(len(lambda_state)):
			if lambda_state[i] == 1:
				if i == 0:
					act_lambda += 1
				else:
					act_lambda += 1
		return act_lambda

# media etático - 49.166666667
# Retornar o Gap
def get_gaps(best_s, bound_s):
	'''
	Obtém os valores numéricos do intervalo entre o valor objetivo e o limite do objetivo.
	Para uma função objetivo única, temos: gap = | value - bound | / max (Val | valor |)
	TODO: Para várias funções objetivo: cada intervalo é o intervalo entre o valor correspondente e o limite. 
	'''
	a = max(best_s, bound_s)
	b = min(best_s, bound_s)
	solution = math.fabs(a - b)/math.fabs(a)#
	return solution


'''
u = Util()
antenas = u.newCreateRRHs(35)
np.shuffle(antenas)
ilp = ILP(antenas, range(len(antenas)), nodes, lambdas, Split)
solution = ilp.run()
solu = ilp.return_solution_values()
#ilp.print_var_values()
ilp.updateValues(solu)
#geral = len(antenas)*1000

print("---------------- ILP --------------------------")
print("Tempo: {}".format(solution.solve_details.time))
print("Energia_ideal: {}".format(solution.objective_value))
print("Energia: {}".format(u.getPowerConsumption()))
print("tráfego na fog atualizado: {}".format(ilp.Fog_Band(solu)))
print("tráfego na coud atualizado: {}".format(ilp.Cloud_Band(solu)))
#print("Atraso total: {}".format(ilp.Delay_total(solu)))
print("---------------- ILP --------------------------")
'''
