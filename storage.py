from ortools.linear_solver import pywraplp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

# First we read in the files
# MDC = pd.read_csv('../WashUAirliftMDC.csv')
# aliftTbl = pd.read_csv('../abbrev.csv')
solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
wcData=pd.read_csv('../wcData.csv')
cmdCode = pd.read_csv('../Command_Code_Lookup.txt')
hMal = pd.read_csv('../AirliftHMALCode.txt')
locData = pd.read_csv('../locationData.csv',header=0)
WUC = pd.read_csv('../AirliftWUCLookupFiles.txt')
lt4Data = pd.read_csv('..\longerThan4_25HRS.csv', low_memory=False)
matrix = pd.read_csv('..\costMatrix.csv',index_col=0)
bcCounts = pd.read_csv('../bcCounts.csv')
bcListDF = pd.read_csv('../useableLocations.csv')
sortedData = pd.read_csv(r'../long4_25.csv', low_memory=False)

objective=solver.Objective()

def toList(strList):
	return ast.literal_eval(strList)

def getRadius(loc,locData):


    # data is a list containing [radius,aircraft loc, base code]
	for i in range(len(locData)):

		# if the check if it is in the first or second column of the
		# location data
		if(str(locData.iloc[i,1])==str(loc)):
			return int(locData.iloc[i,0])
		elif(str(locData.iloc[i,2])==str(loc)):
			return int(locData.iloc[i,0])
		
		# this is the previous code that didnt handle this well
		# if(str(locData.iloc[i,1])==str(loc) or str(locData.iloc[i,2])==str(loc)):
		# 	data=[locData.iloc[i,0],locData.iloc[i,1],locData.iloc[i,2]]
		# 	return int(data[0])

# radialDict takes in a list of basecodes and the locationdata dataframe
# this returns a ditionary {basecode: radial distance}
def radialDict(baseCodes, locData):


	radDict={}
	for item in baseCodes:
		rad = getRadius(item,locData)
		# this was for debugging.
		# nan means the basecode isnt in basecodes.csv
		if(item=='nan'):
			# print(item)
			continue
		# this means basecode is not in the locationdata
		if(rad==None):
			continue
		# assign radius
		else:
			radDict[str(item)]=rad
	return radDict

# This is hardcoding using the radii generated through radii.py
# takes in the radialDict then returns list of list.
# [[start rad, end rad], ... ,[...]]
def genRadZones(radDict):
	# hard coded for prototyping
			
	radList = list(radDict.values())
	minRadList = min(radList)
	totDist = max(radList)-min(radList)

	width=math.ceil(totDist/6)

	zList=[]
	for i in range(totDist//width):
		zList.append([min(radList)+(width*i), min(radList)+(width*(i+1))-1])	

	bcZone = [[] for i in range(len(zList))]
	for bc,r in radDict.items():
		
		for i in range(len(zList)):
			if (r>= zList[i][0] and r<=zList[i][1]):
				bcZone[i].append(bc)

	return bcZone



# so this function wasnt really used...
# im just leaving it for reference
def cleanBC(bcList):

	cleanBC=[]
	for bc in bcList:
		print(matrix.loc[str(bc),str(8450)])
		if matrix.loc[str(bc),str(8450)]!=-1:
			cleanBC.append(bc)
	
	print(len(bcList))
	print(len(cleanBC))

# takes in the bcCounts dataframe and the list of basecodes
# returns a list of decision variables
def genDecisionVars(bcCounts,bcList):

	# generate the decision variables
	varList=[[0 for i in range(len(bcList))] for j in range(len(bcList))]
	# item is basecode and numMXAct is the number of MX at that basecode
	for to in range(len(bcList)):
		# numMXAct= bcCounts.loc[bcCounts.BaseCode==str(to), ['BaseCode', 'CountMX']].iloc[0,1]
		for fro in range(len(bcList)):
			# varList.append(solver.IntVar(0,int(numMXAct), str(fro)+' - '+str(to)))
			varList[to][fro]=solver.IntVar(0,solver.infinity(), str(bcList[fro])+' - '+str(bcList[to]))
	
	yList=[]
	for bc in bcList:
		yList.append(solver.IntVar(0,1,str(bc)))

	return [varList, yList]

def toFrom(decVar):
	# returns list [to, from]
	return str(decVar).split(' - ')

def defObjective(costMat, decVars, yVars):

	for to in range(len(decVars)):
		for fro in range(len(decVars)):
			tofr = toFrom(decVars[to][fro])
			cost=int(costMat.loc[tofr[1],tofr[0]])
			objective.SetCoefficient(decVars[to][fro],cost)
		
	objective.SetMinimization()

def defConstraints(decVars,yVars,bcList,bcCountData):
	constraints=[]

	# fix i and take the sum
	# go through the base codes 
	count = 0

	for to in range(len(decVars)):
		# print(to)
		mxCount=int(bcCountData.loc[bcCountData.BaseCode==bcList[to], ['BaseCode', 'CountMX']].iloc[0,1])
		count+=mxCount
		constraints.append(solver.Constraint(mxCount,mxCount))
		for fro in range(len(decVars)):
			constraints[to].SetCoefficient(decVars[fro][to],1)

	ySum=solver.Constraint(1,1)
	for i in range(0,len(yVars)):
		ySum.SetCoefficient(yVars[i],1)

	logConstraints = []
	for y in range(len(yVars)):
		logConstraints.append(solver.Constraint(-solver.infinity(),0))
		logConstraints[y].SetCoefficient(yVars[y],-count)
	
		for j in range(0,len(bcList)):
			logConstraints[y].SetCoefficient(decVars[y][j],1)

	return constraints
# just generate the plots
def sanityCheck(solList, radDict, bcCountData):


	fig, ax= plt.subplots()
	x=[]
	xtick=()
	y=[]
	col=[]
	for item in solList:
		x.append(radDict[item[0]])
		xtick = xtick + (item[0],)
		y.append(bcCountData.loc[bcCountData.BaseCode==item[0], ['BaseCode','CountMX']].iloc[0,1])
		col.append(item[1])

	ax.scatter(x,y, c=col)
	# plt.xticks(x,xtick)
	fig.suptitle('Zone 3 Type R', fontsize=18)
	ax.set_xlabel('Radius (mi)', fontsize=12)
	ax.set_ylabel('Number MX Activities', fontsize=12)
	plt.show()

def main():


	

	locList=bcListDF.UseableBasecodes.unique().tolist()
	# Change this to whatever type mx you want
	sDf = pd.read_csv('../RMXCounts.csv')
	locList = sDf.BaseCode.unique().tolist()
	# generate a radDict for every type of mx

	radDict=radialDict(locList,locData)
	# now we have the dictionary of {basecode:radius}

	bcZone = genRadZones(radDict)	
	# we now have our radial zones

	# change this for the zone
	print(bcZone)
	zone=2

	# now we should sort by mx activity

	decVarList = genDecisionVars(bcCounts,bcZone[zone])
	xList = decVarList[0]
	yList = decVarList[1]

	# 5%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
	# MX TYPES G, W F ARE SMALL SO WE DO NOT CONSIDER THEM
	# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	# so now we can reference our decision variables...
	# str(decVarList) prints the basecode that the xij is in reference to

	# Now lets try to define the objective
	defObjective(matrix,xList,yList)

	# define the constraints
	defConstraints(xList,yList,bcZone[zone],sDf)

	result = solver.Solve()
	
	print('Number of variables =', solver.NumVariables())
	print('Number of constraints =', solver.NumConstraints())

	# The objective value of the solution.
	print('Optimal objective value = %d' % solver.Objective().Value())

	solList=[]
	for y in yList:
		solList.append([y.name(), y.solution_value()])
		print('%s has value %d' %(y.name(), y.solution_value()))

	sanityCheck(solList, radDict, sDf)
	
if __name__ == "__main__":
	main()




from ortools.linear_solver import pywraplp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

# First we read in the files
# MDC = pd.read_csv('../WashUAirliftMDC.csv')
# aliftTbl = pd.read_csv('../abbrev.csv')
solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
wcData=pd.read_csv('../wcData.csv')
cmdCode = pd.read_csv('../Command_Code_Lookup.txt')
hMal = pd.read_csv('../AirliftHMALCode.txt')
locData = pd.read_csv('../locationData.csv',header=0)
WUC = pd.read_csv('../AirliftWUCLookupFiles.txt')
lt4Data = pd.read_csv('..\longerThan4_25HRS.csv', low_memory=False)
matrix = pd.read_csv('..\costMatrix.csv',index_col=0)
bcCounts = pd.read_csv('../bcCounts.csv')
bcListDF = pd.read_csv('../useableLocations.csv')

objective=solver.Objective()

def toList(strList):
	return ast.literal_eval(strList)

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
		# this was for debugging.
		# nan means the basecode isnt in basecodes.csv
		if(item=='nan'):
			# print(item)
			continue
		# this means basecode is not in the locationdata
		if(rad==None):
			continue
		# assign radius
		else:
			radDict[str(item)]=rad
	return radDict

# This is hardcoding using the radii generated through radii.py
# takes in the radialDict then returns list of list.
# [[start rad, end rad], ... ,[...]]
def genRadZones(radDict):

		
	radList = list(radDict.values())
	minRadList = min(radList)
	totDist = max(radList)-min(radList)

	print('genRadZone:  ' , totDist//(450*3))

	width=math.ceil(totDist/6)

	zList=[]
	for i in range(totDist//width+1):
		zList.append([min(radList)+(width*i), min(radList)+(width*(i+1))-1])
	print('zlist comparison')
	print(zList)
	print(totDist)
	print('this is the len of zList:  ', len(zList))
	

	bcZone = [[] for i in range(len(zList))]
	for bc,r in radDict.items():
		
		for i in range(len(zList)):
			if (r>= zList[i][0] and r<=zList[i][1]):
				bcZone[i].append(bc)

	print(bcZone)


	# hard coded for prototyping
	z1=[]
	z2=[]
	z3=[]
	z4=[]
	z5=[]
	z6=[]
	for bc,r in radDict.items():
		if(r>=1300 and r <= 2433):
			z2.append(bc)
		# if(r>=0 and r<= 1216):
			z1.append(bc)
		# elif(r>=1217 and r<=2433):
			# z2.append(bc)
		elif(r>=2434 and r<= 3650):
			z3.append(bc)
		elif(r>3651 and r<= 4867):
			z4.append(bc)
		elif(r>=4868 and r<=6084):
			z5.append(bc)
		elif(r>=6085 and r<=7301):
			z6.append(bc)

	return [z1,z2,z3,z4,z5,z6]
	# return bcZone


def cleanBC(bcList):

	cleanBC=[]
	for bc in bcList:
		if matrix.loc[str(bc),str(8450)]!=-1:
			cleanBC.append(bc)
# takes in the bcCounts dataframe and the list of basecodes
# returns a list of decision variables
def genDecisionVars(bcCounts,bcList):

	# generate the decision variables
	varList=[[0 for i in range(len(bcList))] for j in range(len(bcList))]
	# item is basecode and numMXAct is the number of MX at that basecode
	for to in range(len(bcList)):
		# numMXAct= bcCounts.loc[bcCounts.BaseCode==str(to), ['BaseCode', 'CountMX']].iloc[0,1]
		for fro in range(len(bcList)):
			# varList.append(solver.IntVar(0,int(numMXAct), str(fro)+' - '+str(to)))
			varList[to][fro]=solver.IntVar(0,solver.infinity(), str(bcList[fro])+' - '+str(bcList[to]))
	
	yList=[]
	for bc in bcList:
		yList.append(solver.IntVar(0,1,str(bc)))

	return [varList, yList]

def toFrom(decVar):
	# returns list [to, from]
	return str(decVar).split(' - ')

def defObjective(costMat, decVars, yVars):

	for to in range(len(decVars)):
		for fro in range(len(decVars)):
			tofr = toFrom(decVars[to][fro])
			cost=int(costMat.loc[tofr[1],tofr[0]])
			objective.SetCoefficient(decVars[to][fro],cost)

	# for x in decVars:
	# 	tofr = toFrom(x)
	# 	cost=costMat.loc[tofr[1],tofr[0]]

	# 	objective.SetCoefficient(x,int(cost))

	# for y in yVars:
	# 	objective.SetCoefficient(y,1)
		
	objective.SetMinimization()

	# print(costMat.loc[str(decVars[1]),str(decVars[0])])

def defConstraints(decVars,yVars,bcList):

	constraints=[]
	# fix i and take the sum
	# go through the base codes 
	count = 0



	# print(len(decVars),'  ', len(bcList))
	for to in range(len(decVars)):
		mxCount=int(bcCounts.loc[bcCounts.BaseCode==bcList[to], ['BaseCode', 'CountMX']].iloc[0,1])
		count+=mxCount
		constraints.append(solver.Constraint(mxCount,mxCount))
		for fro in range(len(decVars)):
			constraints[to].SetCoefficient(decVars[fro][to],1)


	# for bc in bcList:
	# 	# accumulator for how much goes into the base
	# 	lydWay=int(bcCounts.loc[bcCounts.BaseCode==bc, ['BaseCode', 'CountMX']].iloc[0,1])
	# 	# constraints.append(solver.Constraint(lydWay,lydWay))
	# 	into += lydWay
		# go through the decVars
		# for x in decVars:
		# 	to = toFrom(x)[0]
		# 	fro = toFrom(x)[1]
			# if we go to this base, then add the amt in
			# if(fro==str(bc)):
				# into += int(bcCounts.loc[bcCounts.BaseCode==fro, ['BaseCode', 'CountMX']].iloc[0,1])
				# constraints[-1].SetCoefficient(x,1)
		# equality constraint
		# constraints.append(solver.Constraint(lydWay,lydWay))
		# now set the right coeffs
		# for x in decVars:
		# 	to = toFrom(x)[0]
		# 	fro = toFrom(x)[1]
		# 	if(fro==str(bc)):
		# 		constraints[-1].SetCoefficient(x,1)
	ySum=solver.Constraint(1,1)
	for i in range(0,len(yVars)):
		ySum.SetCoefficient(yVars[i],1)

	logConstraints = []
	for y in range(len(yVars)):
		logConstraints.append(solver.Constraint(-solver.infinity(),0))
		logConstraints[y].SetCoefficient(yVars[y],-count)
	
		for j in range(0,len(bcList)):
			logConstraints[y].SetCoefficient(decVars[y][j],1)

	return constraints

def sanityCheck(solList, radDict):


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
		# if item[0]=='3244':
		# 	col.append(1)
		# else:
		# 	col.append(0)
		col.append(item[1])

	ax.scatter(x,y, c=col, label=group)
	fig.suptitle('Zone 2', fontsize=18)
	ax.set_xlabel('Radius (mi)', fontsize=12)
	ax.set_ylabel('Number MX Activities', fontsize=12)
	# ax.legend()
	# plt.xticks(x,xtick)
	plt.show()

def main():
	
	# this snippet takes a while to run.  maybe save this data
	# to a df then load it in.  This is to handle the location not found error
	# FIX if aircraft location isnt nan then it is at home base

	# this is the FIXED VERSON UNCOMMENT THIS SECTION TO WRITE TO CSV
	# locList = [[] for i in range(lt4Data.shape[0])]
	# # currentLocs = []
	# for index,wc in lt4Data.iterrows():
	# 	if not(str(wc[17])=='nan'):
	# 		locList[index].append(str(wc[17]))
	# 	else:
	# 		locList[index].append(str(wc[18]))

	# columns=['UseableBasecodes']

	# locDF=pd.DataFrame(locList,columns = columns)
	# locDF.to_csv('../useableLocations.csv')

	locList=bcListDF.UseableBasecodes.unique().tolist()
	radDict=radialDict(locList,locData)
	# now we have the dictionary of {basecode:radius}


	bcZone = genRadZones(radDict)	
	# we now have our radial zones
	# print(bcZone)
	# print(radDict)
	
	# for dont need to filter the basecodes...
	# cleanBC(bcZone[1])
	# print(bcZone[1])


	# Change this
	zone=1


	# first we need to set our decision variables
	# print(type(bcCounts.loc[bcCounts.BaseCode=='8450', ['BaseCode', 'CountMX']].iloc[0,1]))
	decVarList = genDecisionVars(bcCounts,bcZone[zone])
	xList = decVarList[0]
	yList = decVarList[1]
	# toFrom(decVarList[2])
	# print(len(decVarList))
	# print(decVarList[0])
	# print(len(decVarList))
	# so now we can reference our decision variables...
	# str(decVarList) prints the basecode that the xij is in reference to

	# Now lets try to define the objective
	# defObjective(matrix,decVarList)
	defObjective(matrix,xList,yList)

	# define the constraints
	# a=defConstraints(decVarList,bcZone[5])
	a = defConstraints(xList,yList,bcZone[zone])

	result = solver.Solve()
	
	print('Number of variables =', solver.NumVariables())
	print('Number of constraints =', solver.NumConstraints())

	# The objective value of the solution.
	print('Optimal objective value = %d' % solver.Objective().Value())

	solList=[]
	for y in yList:
		solList.append([y.name(), y.solution_value()])
		print('%s has value %d' %(y.name(), y.solution_value()))

	sanityCheck(solList, radDict)
	
if __name__ == "__main__":
	main()

