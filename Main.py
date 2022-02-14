from SGO.SGO import SGO

playerNumber = 20
substituteNumber = 3
kicksLimit = 1000000
functionEvaluationLimit = 10000
numberOfRrh = 40
numberOfVariables = 4
target = 0

sgo = SGO(playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfRrh, numberOfVariables, target=target)
sgo.run()
