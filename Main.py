from SGO.SGO import SGO

playerNumber = 50
substituteNumber = 10
kicksLimit = 1000000
functionEvaluationLimit = 100000
numberOfRrh = 30
numberOfVariables = 4
target = 0

sgo = SGO(playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfRrh, numberOfVariables, target=target)
sgo.run()
