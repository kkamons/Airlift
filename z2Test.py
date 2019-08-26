#base codes
#3244, 3240, 5551, 4454, C4324, 3412, C4135, 5694, 3052, C4242, C3104, C8248
bcList = ['3244', '3240', '5551', '4454', 'C4324', '3412', 'C4135', '5649', '3052', 'C4242', 'C3104', 'C8248']
radiusList = [3260, 3260, 3226, 3221, 3249, 3260, 3189, 3012, 3267, 3202, 3327, 3614]
demand = [792, 576, 10, 2, 38, 27, 3, 3, 3, 1, 4, 1]
from ortools.linear_solver import pywraplp
import math
solver = pywraplp.Solver('FacilityLocator',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

varList=[[0,0,0,0,0,0,0,0,0,0,0,0] for i in range(0,12)]

yList= [0,0,0,0,0,0,0,0,0,0,0,0]
for y in range(0,len(bcList)):
    yList[y] = solver.IntVar(0,1,bcList[y])

for to in range(0,len(bcList)):
    for fro in range(0,len(bcList)):
        varList[to][fro] = solver.IntVar(0,solver.infinity(), bcList[fro]+'-'+bcList[to]) 
           
costMatrix = [[0,0,0,0,0,0,0,0,0,0,0,0] for i in range(0,12)]
for to in range(0,len(bcList)):
    for fro in range(0,len(bcList)):
        costMatrix[to][fro] = abs(radiusList[to]-radiusList[fro])

objective = solver.Objective()
for to in range(0,len(bcList)):
	for fro in range(0,len(bcList)):
		print(varList[to][fro])
		print(costMatrix[to][fro],' -- ',type(costMatrix[to][fro]))
		objective.SetCoefficient(varList[to][fro], costMatrix[to][fro])
        
objective.SetMinimization()

constraintList = [0,0,0,0,0,0,0,0,0,0,0,0]
for to in range(0,len(bcList)):
	constraintList[to] = solver.Constraint(demand[to],demand[to])
	# print(demand[to], ' here ')
	for fro in range(0,len(bcList)):
		constraintList[to].SetCoefficient(varList[fro][to], 1)
        
constraintY = solver.Constraint(1,1)
# print(len(yList))
# print(yList)
for i in range(0,len(yList)):
    constraintY.SetCoefficient(yList[i],1)
    
logConstraints = [0,0,0,0,0,0,0,0,0,0,0,0]
for i in range(0,len(logConstraints)):
    logConstraints[i] = solver.Constraint(-solver.infinity(),0)
    logConstraints[i].SetCoefficient(yList[i], -2000)
    for j in range(0,len(bcList)):
        logConstraints[i].SetCoefficient(varList[i][j], 1)
        
solver.Solve()
print(objective.Value())
print('Number of variables =', solver.NumVariables())
print('Number of constraints =', solver.NumConstraints())

for i in range(0, len(yList)):
    print(yList[i], ': ', yList[i].solution_value())
sum = 0   
for i in range(0, len(yList)):
    for j in range(0, len(yList)):
        sum = sum + varList[i][j].solution_value()*costMatrix[i][j]

