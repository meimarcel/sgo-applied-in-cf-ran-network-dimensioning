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

	def energy(self, sol):
		#antenas = np.array_split(sol, (len(sol)/15))
		antenas = [sol[x:x+15] for x in range(0, len(sol), 15)]
		Cloud_traffic = 0
		Fog_Traffic = 0
		cost = 0
		#print(antenas)
		trafego = len(antenas) * 1966
		antenas_count = [sol[x:x+15] for x in range(0, len(sol), 15)]
		#print("Tráfego total {}".format(trafego))
		for i in range(len(antenas)):
			#print(i)
			Total_traffic = 0
			Total_traffic = i*1966
			self.node_id = antenas_count[i][0:3]
			self.lambda_id = antenas_count[i][3:11]
			self.split_id = antenas_count[i][11:15]
			#print("Split_ID {}".format(self.split_id))
			#print("VPONs_ID {}".format(self.lambda_id))
			#print("Node_ID {}".format(self.node_id))
			#print("Antena {} = {}".format(i,antenas_count[i]))


			####################################################### RESTRIÇÃO SPLIT ==============================================		
			#Restrição 1 - Um Split por Antena - Se mais de 1 ou não tiver pelo menos 1 -> custo alto
			if self.duplicatas(self.split_id, 1)>1:
				cost +=1000000
			if self.split_id.count(1) == 0:
				cost += 1000000

			#######################################################################################################################
			#Se a nuvem ou uma fog não estiver ativa, custo alto
			if self.duplicatas(self.node_id, 1) == 0:
				cost += 1000000


			####################################################### RESTRIÇÃO VPONs ==============================================
			#Restrição 2: Quantidade de comprimentos de onda
			if Total_traffic > self.duplicatas(self.lambda_id, 1)*10000:
				#print("Trafego total é {} com {} vpons".format(Total_traffic, self.duplicatas(self.lambda_id, 1)*10000))
				cost +=100000

			####################################################### RESTRIÇÃO NODE_SPLIT ==============================================
			#Split 0 -> apenas a nuvem; Split1_2 -> Nuvem e Fog, Split 3 -> apenas a Fog
			if self.split_id[0] == 1 and self.node_id[0] == 1:
				cost+=0
			if self.split_id[0] ==1 and self.node_id[0]==0:
				cost+= 1000000
			if self.split_id[0] ==1 and self.duplicatas(self.node_id, 1)!= 1:
				cost+= 1000000
			if (self.split_id[1] ==1 or self.split_id[2] ==1)  and self.node_id[0]==0: #se split 2 ou 3 ativas e não tiver nuvem ativa .....
				cost+= 1000000
			if (self.split_id[1] ==1 or self.split_id[2] ==1)  and self.duplicatas(self.node_id, 1)!= 2: #se split 2 ou 3 ativas e não tiver pelo menos 2 nós ativos .....
				cost+= 1000000
			if self.split_id[3] == 1 and self.node_id[0] == 1:
				cost+= 1000000
			if self.split_id[3] == 1 and self.duplicatas(self.node_id, 1)!= 1:
				cost+= 1000000


			####################################################### RESTRIÇÃO DE CAPACIDADE ==============================================
			# restrição de capacidadeda (esse tá bagunçado kkk)
			if self.split_id[0] == 1:
				Cloud_traffic += i*self.ecpri_split[0]
				Fog_Traffic +=0
				if Cloud_traffic <= self.Node_Capacity[0]:
					cost+=0
				else:
					cost +=1000000

			if self.split_id[3] == 1:
				Cloud_traffic += 0
				Fog_Traffic +=self.ecpri_split[0]
				if self.duplicatas(self.node_id, 1)!= 0 and Fog_Traffic <= self.Node_Capacity[self.node_id.index(1)]:
					cost +=0
				else:
					cost +=1000000

			if (self.split_id[1] == 1 or self.split_id[2] ==1):
				Cloud_traffic += self.ecpri_split[self.split_id.index(1)]
				Fog_Traffic += self.ecpri_split[0] - self.ecpri_split[self.split_id.index(1)]
				if Cloud_traffic > self.Node_Capacity[0]:
					cost +=1000000
				if Fog_Traffic > self.Node_Capacity[1] or Fog_Traffic > self.Node_Capacity[2]:
					cost +=1000000

			#################################################################### Pega o Estado e Calcula o custo #####################

			if self.node_id[0]== 1 and self.NodeState[0] ==0:
				#print("O Izão {} e o node id {}".format(i, self.node_id[0]))
				cost = 600
				if self.NodeState[0] == 0:
					self.NodeState[0] = 1
					#print(self.NodeState)
			if self.node_id[1] == 1 and self.NodeState[1] ==0:
				cost += 300
				if self.NodeState[1] ==0:
					self.NodeState[1] =1
					#print(self.NodeState)
			if self.node_id[2] == 1 and self.NodeState[2] ==0:
				cost += 300
				if self.NodeState[2] ==0:
					self.NodeState[2] =1
					#print(self.NodeState)



			#Lambdas
			if self.lambda_id[0]== 1 and self.LambdasState[0] ==0:
				#print("O Izão {} e o node id {}".format(i, self.node_id[0]))
				cost += 20
				if self.LambdasState[0] == 0:
					self.LambdasState[0] = 1
			if self.lambda_id[1] == 1 and self.LambdasState[1] ==0:
				cost += 20
				if self.LambdasState[1] ==0:
					self.LambdasState[1] =1
			if self.lambda_id[2] == 1 and self.LambdasState[2] ==0:
				cost += 20
				if self.LambdasState[2] ==0:
					self.LambdasState[2] =1
			if self.lambda_id[3]== 1 and self.LambdasState[0] ==0:
				#print("O Izão {} e o node id {}".format(i, self.node_id[0]))
				cost += 20
				if self.LambdasState[3] == 0:
					self.LambdasState[3] = 1
			if self.lambda_id[4] == 1 and self.LambdasState[4] ==0:
				cost += 20
				if self.LambdasState[4] ==0:
					self.LambdasState[4] =1
			if self.lambda_id[5] == 1 and self.LambdasState[5] ==0:
				cost += 20
				if self.LambdasState[5] ==0:
					self.LambdasState[5] =1
			if self.lambda_id[6] == 1 and self.LambdasState[6] ==0:
				cost += 20
				if self.LambdasState[6] ==0:
					self.LambdasState[6] =1
			if self.lambda_id[7] == 1 and self.LambdasState[7] ==0:
				cost += 20
				if self.LambdasState[7] ==0:
					self.LambdasState[7] =1


			#print(cost)			
					#print("Estado dos nós {}".format(self.NodeState))
		return cost




	######################################################### Parâmetros para Teste ###############################################################

ww = [1,0,1,1,1,0,0,0,0,1,1,0,0,0,1,1,0,1,1,1,0,0,0,0,1,1,0,1,0,0,0,0,1,1,1,0,0,0,0,1,1,0,0,0,1,0,0,1,1,1,0,0,0,0,1,1,0,0,0,1,1,1,0,1,1,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1]# 

if __name__ == "__main__":
	test = Restricao()
	print(test.energy(ww))





