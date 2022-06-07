from SGO.SGO import SGO

playerNumber = 22
substituteNumber = 5
kicksLimit = 1000000
functionEvaluationLimit = 10000
numberOfRrh = 50
numberOfVariables = 5
target = 0

sgo = SGO(playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfRrh, numberOfVariables, target=target)
#sgo.run()
sgo.retorno()
