from ortools.linear_solver import pywraplp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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
matrix = pd.read_csv('..\costMatrix.csv')
bcCounts = pd.read_csv('../bcCounts.csv')
bcListDF = pd.read_csv('../useableLocations.csv')


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
			print(item)
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
	z1=[]
	z2=[]
	z3=[]
	z4=[]
	z5=[]
	z6=[]
	for bc,r in radDict.items():
		if(r>=0 and r<= 1216):
			z1.append(bc)
		elif(r>=1217 and r<=2433):
			z2.append(bc)
		elif(r>=2434 and r<= 3650):
			z3.append(bc)
		elif(r>3651 and r<= 4867):
			z4.append(bc)
		elif(r>=4868 and r<=6084):
			z5.append(bc)
		elif(r>=6085 and r<=7301):
			z6.append(bc)

	return [z1,z2,z3,z4,z5,z6]

# takes in the bcCounts dataframe and the list of basecodes
# returns a list of decision variables
def genDecisionVars(bcCounts,bcList):

	# generate the decision variables
	varList=[]
	# item is basecode and numMXAct is the number of MX at that basecode
	for item in bcList:
		numMXAct= bcCounts.loc[bcCounts.BaseCode==str(item), ['BaseCode', 'CountMX']].iloc[0,1]
		varList.append(solver.IntVar(0,int(numMXAct), str(item)))

	return varList

def toFrom(decVar):
	# returns list [to, from]
	return str(decVar).split(' - ')

def defObjective(costMat, decVars):

	for x in decVars:
		tofr = toFrom(x)
		cost=costMat.loc[tofr[0],tofr[1]]

		objective.SetCoefficient(x,int(cost))
		
	objective.SetMinimization()


def defConstraints(decVars,bcList):

	constraints=[]
	# fix i and take the sum
	# go through the base codes 
	for bc in bcList:
		# accumulator for how much goes into the base
		into = 0

		# go through the decVars
		for x in decVars:
			to = toFrom(x)[0]
			fro = toFrom(x)[1]
			# if we go to this base, then add the amt in
			if(to==str(bc)):
				into += int(bcCounts.loc[bcCounts.BaseCode==fro, ['BaseCode', 'CountMX']].iloc[0,1])
		# equality constraint
		constraints.append(solver.Constraint(into,into))
		# now set the right coeffs
		for x in decVars:
			to = toFrom(x)[0]
			fro = toFrom(x)[1]
			if(fro==str(bc)):
				constraints[-1].SetCoefficient(x,1)
	return constraints

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

	# first we need to set our decision variables
	# print(type(bcCounts.loc[bcCounts.BaseCode=='8450', ['BaseCode', 'CountMX']].iloc[0,1]))
	decVarList = genDecisionVars(bcCounts,bcZone[5])
	print(str(decVarList[0]))
	# so now we can reference our decision variables...
	# str(decVarList) prints the basecode that the xij is in reference to
	defObjective(matrix,decVarList)

	a=defConstraints(decVarList,bcZone[5])

	
	



if __name__ == "__main__":
	main()