#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import itertools
import operator


class Restricao:

	def __init__(self):
		self.NodeState = [0,0,0] #verificar o estado ativo ou não do nó
		self.LambdasState = [0,0,0,0,0,0,0,0] #verificar o estado ativo ou não do VPON
		self.SPlitState = [0,0,0,0] #verificar o estado ativo ou não

		self.node_id = []
		self.lambda_id = []
		self.split_id= []
		self.State = []
		self.Node_Capacity = [40000, 20000, 20000]
		self.ecpri_split = [1966, 74, 119, 675] #largura de banda demandada por split
		self.fog_maxCapaticy= []
		#calcula a energia em pós processamento. Lista_total = a lista com todos os resultados
		self.cloud_vpons = [0,0,0,0]
		self.fog_vpons = [0,0,0,0]
	
 	#função para verificar elementos repetidos na lista
	def duplicatas(slef, lst, x):
		interator = 0
		for ele in lst:
			if (ele == x):
				interator = interator + 1
		return interator

	# def energy(self, sol):
	# 	#antenas = np.array_split(sol, (len(sol)/15))
	# 	antenas = [sol[x:x+4] for x in range(0, len(sol), 4)]
	# 	Cloud_traffic = 0
	# 	Fog_Traffic = 0
	# 	cost = 0
	# 	#print(antenas)
	# 	trafego = len(antenas) * 1966
	# 	antenas_count = [sol[x:x+4] for x in range(0, len(sol), 4)]
	# 	#print("Tráfego total {}".format(trafego))
	# 	for i in range(len(antenas)):
	# 		#print(i)
	# 		Total_traffic = 0
	# 		Total_traffic = (i+1)*1966
	# 		#self.node_id = antenas_count[i][0:3]
	# 		#self.lambda_id = antenas_count[i][3:11]
	# 		self.split_id = antenas_count[i][0:4]
	# 		#print("Split_ID {}".format(self.split_id))
	# 		#print("VPONs_ID {}".format(self.lambda_id))
	# 		#print("Node_ID {}".format(self.node_id))
	# 		#print("Antena {} = {}".format(i,antenas_count[i]))
	# 		#print("Tráfego é: {}".format((i+1)*1966))


	# 		####################################################### RESTRIÇÃO SPLIT ==============================================		
	# 		#Restrição 1 - Um Split por Antena - Se mais de 1 ou não tiver pelo menos 1 -> custo alto

	# 		if self.split_id.count(1) == 1:
	# 			cost += 0
	# 		if self.split_id.count(1) == 2:
	# 			cost += 20000
	# 		if self.split_id.count(1) == 3:
	# 			cost += 50000
	# 		if self.split_id.count(1) == 4:
	# 			cost += 100000
			
					

	# 		if Total_traffic<=40000:
	# 			if self.split_id[0]==1:
	# 				cost+=0
	# 			if self.split_id[1]==1:
	# 				cost+=100
	# 			if self.split_id[2]==1:
	# 				cost+=500
	# 			if self.split_id[3]==1:
	# 				cost+=1000

	# 		if Total_traffic>40000:
	# 			if self.split_id[0]==1:
	# 				cost+=1000
	# 			if self.split_id[0]==0:
	# 				cost+=0


	# 	return cost

	def energy(self, rrh, sol):
		#print(i)
		Total_traffic = 0
		Total_traffic = (rrh+1)*1966
		#self.node_id = antenas_count[i][0:3]
		#self.lambda_id = antenas_count[i][3:11]
		self.split_id = sol
		#print("Split_ID {}".format(self.split_id))
		#print("VPONs_ID {}".format(self.lambda_id))
		#print("Node_ID {}".format(self.node_id))
		#print("Antena {} = {}".format(i,antenas_count[i]))
		#print("Tráfego é: {}".format((i+1)*1966))
		cost = 0

		####################################################### RESTRIÇÃO SPLIT ==============================================		
		#Restrição 1 - Um Split por Antena - Se mais de 1 ou não tiver pelo menos 1 -> custo alto

		if self.split_id.count(1) == 1:
			cost += 0
		if self.split_id.count(1) == 2:
			cost += 20000
		if self.split_id.count(1) == 3:
			cost += 50000
		if self.split_id.count(1) == 4:
			cost += 100000

		if Total_traffic<=37000:
			if self.split_id[0]==1:
				cost+=0
			if self.split_id[1]==1:
				cost+=100
			if self.split_id[2]==1:
				cost+=500
			if self.split_id[3]==1:
				cost+=1000

		if Total_traffic>37000:
			if self.split_id[0]==1:
				cost+=1000
			if self.split_id[0]==0:
				cost+=0
    
		return cost




	######################################################### Parâmetros para Teste ###############################################################

#ww = [1,0,1,1,1,0,0,0,0,1,1,0,0,0,1,1,0,1,1,1,0,0,0,0,1,1,0,1,0,0,0,0,1,1,1,0,0,0,0,1,1,0,0,0,1,0,0,1,1,1,0,0,0,0,1,1,0,0,0,1,1,1,0,1,1,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1]# 
ww = [[0, 0, 1, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 1, 1, 1], [1, 0, 0, 0], [1, 1, 1, 0], [1, 0, 0, 0], [1, 0, 1, 0], [0, 1, 0, 0]]
if __name__ == "__main__":
	test = Restricao()
	for i in range(len(ww)):
		print(test.energy(i,ww[i]))





