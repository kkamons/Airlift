from ortools.linear_solver import pywraplp
import pandas as pd
import matplotlib.pyplot as plt
import math

# First we read in the files and set our google OR tools solver
solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
locData = pd.read_csv('../locationData.csv',header=0)
matrix = pd.read_csv('..\costMatrix.csv',index_col=0)
bcCounts = pd.read_csv('../bcCounts.csv')
bcListDF = pd.read_csv('../useableLocations.csv')

# declare the googleOR objective
objective=solver.Objective()

# toList takes in a list as a string object
# returns python list object
def toList(strList):
	return ast.literal_eval(strList)

# get radius takes in location data and a basecode
# returns distance from reference point
def getRadius(loc,locData):

    # data is a list containing [radius,aircraft loc, base code]
	for i in range(len(locData)):

		# if the check if it is in the first or second column of the
		# location data
		if(str(locData.iloc[i,1])==str(loc)):
			return int(locData.iloc[i,0])
		elif(str(locData.iloc[i,2])==str(loc)):
			return int(locData.iloc[i,0])
		
# radialDict takes in a list of basecodes and the locationdata dataframe
# this returns a ditionary {basecode: radial distance}
def radialDict(baseCodes, locData):

	radDict={}
	for item in baseCodes:
		rad = getRadius(item,locData)
		# nan means the basecode isnt in basecodes.csv
		if(item=='nan'):
			continue
		# this means basecode is not in the locationdata
		if(rad==None):
			continue
		# assign radius to a basecode
		else:
			radDict[str(item)]=rad
	return radDict

# takes in the radialDict then returns list of list.
# [[start rad, end rad], ... ,[...]]
def genRadZones(radDict):

		
	radList = list(radDict.values())
	minRadList = min(radList)
	# find the total distance
	totDist = max(radList)-min(radList)

	# create a width of the radial zone
	# totDist/6 is aprox 3 hrs flying time
	width=math.ceil(totDist/6)
	
	# zList is the outer list which will contain lists start and end radii
	zList=[]
	for i in range(totDist//width+1):
		# find start and end points
		zList.append([min(radList)+(width*i), min(radList)+(width*(i+1))-1])

	# assign basecode for each zone
	bcZone = [[] for i in range(len(zList))]
	for bc,r in radDict.items():
		for i in range(len(zList)):
			if (r>= zList[i][0] and r<=zList[i][1]):
				bcZone[i].append(bc)

	return bcZone

# takes in the bcCounts dataframe and the list of basecodes
# returns a list of decision variables
def genDecisionVars(bcCounts,bcList):

	# generate the decision variables
	varList=[[0 for i in range(len(bcList))] for j in range(len(bcList))]
	for to in range(len(bcList)):
		for fro in range(len(bcList)):
			varList[to][fro]=solver.IntVar(0,solver.infinity(), str(bcList[fro])+' - '+str(bcList[to]))
	
	# generate the p-median variables
	yList=[]
	for bc in bcList:
		yList.append(solver.IntVar(0,1,str(bc)))

	return [varList, yList]

# takes in a decision variable object and returns a list of the to and from locations
def toFrom(decVar):
	# returns list [to, from]
	return str(decVar).split(' - ')

# takes in the costMatrix, decicion variables and p-median variables
# returns nothing. simply sets objective
def defObjective(costMat, decVars, yVars):

	# see mathematical formulation objective function
	for to in range(len(decVars)):
		for fro in range(len(decVars)):
			tofr = toFrom(decVars[to][fro])
			# find the cost and weigh the decVar with the cost
			cost=int(costMat.loc[tofr[1],tofr[0]])
			objective.SetCoefficient(decVars[to][fro],cost)
		
	objective.SetMinimization()

# takes decVars, p-medianVars, basecode list, and basecode count mx data
# returns nothing useful.  simply defines constraints
def defConstraints(decVars,yVars,bcList):
	
	# intitalize list of contraints
	constraints=[]
	count = 0
	# fix i and take the sum
	# go through the base codes 
	for to in range(len(decVars)):
		# get the number of mx activities
		mxCount=int(bcCounts.loc[bcCounts.BaseCode==bcList[to], ['BaseCode', 'CountMX']].iloc[0,1])
		count+=mxCount
		constraints.append(solver.Constraint(mxCount,mxCount))
		
		# for every location, set the constraint of what goes into the base
		for fro in range(len(decVars)):
			constraints[to].SetCoefficient(decVars[fro][to],1)

	# p-median variables 
	ySum=solver.Constraint(1,1)
	for i in range(0,len(yVars)):
		# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
		# CHANGE HERE TO CHANGE NUMBER OF MX LOCATIONS IN A ZONE
		# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
		ySum.SetCoefficient(yVars[i],1)

	# logical constraints
	# the sum of number of mx activites can't be greater than total number of mx activiteis
	# in the network
	logConstraints = []
	for y in range(len(yVars)):
		logConstraints.append(solver.Constraint(-solver.infinity(),0))
		logConstraints[y].SetCoefficient(yVars[y],-count)
	
		for j in range(0,len(bcList)):
			logConstraints[y].SetCoefficient(decVars[y][j],1)

	return constraints

# just generate the plots and give data Visualization
def genFigure(solList, radDict):


	fig, ax= plt.subplots()
	x=[]
	xtick=()
	y=[]
	group = ("selected", "not selected")
	col=[]
	for item in solList:
		x.append(radDict[item[0]])
		xtick = xtick + (item[0],)
		y.append(bcCounts.loc[bcCounts.BaseCode==item[0], ['BaseCode','CountMX']].iloc[0,1])
		col.append(item[1])

	ax.scatter(x,y, c=col, label=group)
	fig.suptitle('Zone #', fontsize=18)
	ax.set_xlabel('Radius (mi)', fontsize=12)
	ax.set_ylabel('Number MX Activities', fontsize=12)
	plt.show()

def main():

	locList=bcListDF.UseableBasecodes.unique().tolist()
	radDict=radialDict(locList,locData)
	# now we have the dictionary of {basecode:radius}

	bcZone = genRadZones(radDict)	
	# we now have our radial zones

	# Change this to see a new zone (indexing starts at 0)
	zone=1


	# first we need to set our decision variables
	decVarList = genDecisionVars(bcCounts,bcZone[zone])
	xList = decVarList[0]
	yList = decVarList[1]
	# so now we can reference our decision variables...
	# str(decVarList) prints the basecode that the xij is in reference to

	# Now lets try to define the objective
	defObjective(matrix,xList,yList)

	# define the constraints
	a = defConstraints(xList,yList,bcZone[zone])

	result = solver.Solve()

	# The objective value of the solution.
	print('Optimal objective value = %d' % solver.Objective().Value())

	solList=[]
	for y in yList:
		solList.append([y.name(), y.solution_value()])
		print('%s has value %d' %(y.name(), y.solution_value()))

	# if the basecode has value of 1, then it has been chosen as
	# the optimal base in the zone
	genFigure(solList, radDict)
	
if __name__ == "__main__":
	main()