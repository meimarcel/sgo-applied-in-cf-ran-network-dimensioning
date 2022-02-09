from SGO.SGO import SGO

playerNumber = 30
substituteNumber = 3
kicksLimit = 100000
functionEvaluationLimit = 10000
numberOfVariables = 5 * 15

sgo = SGO(playerNumber, substituteNumber, kicksLimit, functionEvaluationLimit, numberOfVariables)
sgo.run()
