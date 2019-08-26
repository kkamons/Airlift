import pandas as pd
import ast

#################################################################
# expWCdata.py was used to generate the work center data
# then was adapted to do the same analysis on BASECODES
#################################################################

# This method takes in a string version of a list then returns
# a python list object
def toList(strList):
	return ast.literal_eval(strList)


# this method takes the count of mx per work center and writes it
# to a csv
def wcCountsToDF(wcData):

	# data is in form: [[wc,[mx],[act],[whenDisc]],...]
	wcMxCounts=[]
	wcActCounts=[]
	countsDict={}
	for index,wc in wcData.iterrows():
		# print("Work Center:  %s \nMx : %d, Action: %d, WhenDisc: %d" % (wc[0],len(toList(wc[1])),len(toList(wc[2])),len(toList(wc[3]))))
		countsDict[wc[0]]=[len(toList(wc[1])), len(toList(wc[2])),len(toList(wc[3]))]

	# turn the dictionary into a dataframe and write to csv
	countsDf=pd.DataFrame.from_dict(data=countsDict, orient='index', columns=['TypeMx','ACTION','WHEN_DISC'])
	countsDf.to_csv('../wcCounts.csv')

# this counts the number of MX activites at each work center.
# returns dictionary object
# argument data is a pandas dataframe
def countMX(data):	
	# get the work centers and initialize a dictionary
	wcList = data.WORK_CENTER.unique().tolist()
	countDict = dict.fromkeys(wcList)

	# iterate through a dataframe
	for index, wc in data.iterrows():
		# if the work center has not been encountered, initialize
		if(countDict[wc[5]]==None):
			countDict[wc[5]]=1
		# increment
		else:
			countDict[wc[5]]= countDict[wc[5]]+1

	return countDict

# count MX activities per base
# takes in pandas dataframe
#  returns the count dictionary {basecode: mxCount}
# also writes the dictionary to a csv
# comment this out to not override the existing csv file
def countMXbc(data, mx):
	
	# get the locations that are used
	locList=[]
	for index,wc in data.iterrows():
		# wc is a row in the dataframe
		# print(wc[18])
		# print(type(wc[17]))
		# print(wc[11])
		# print(mx)
		if (wc[11]==mx):
			# if the aircraft location is known
			if not(str(wc[18]) =='nan'):
				locList.append(str(wc[18]))
			# there is no aircraft location so we use the basecode
			else:
				locList.append(str(wc[19]))
		
	# initialize a dictionary
	countDict = dict.fromkeys(locList)
	# go through the dataframe and count the number of occurances
	for index, wc in data.iterrows():
		if wc[11]==mx:
			# if the aircraft has aircraft location
			if not(str(wc[18])=='nan'):
				# initialize
				if(countDict[wc[18]]==None):
					countDict[wc[18]]=1
				# increment
				else:
					countDict[str(wc[18])]= countDict[str(wc[18])] +1
			# otherwise use the basecode
			else:
				# initialize
				if(countDict[str(wc[19])]==None):
					countDict[str(wc[19])]=1
				# increment
				else:
					countDict[str(wc[19])]= countDict[str(wc[19])]+1
	# turn this dictionary into a dataframe and write it to a csv
	# countsDf=pd.DataFrame.from_dict(data=countDict) #columns=['BaseCode','CountMX']  , orient='index'
	countsDf=pd.DataFrame(list(countDict.items()),columns=['BaseCode','CountMX'])
	# print(countsDf.head())
	print(mx)
	countsDf.to_csv('../'+mx+'MXCounts.csv', index=False)

	return countDict



def main():
	# wcData=pd.read_csv('../wcData.csv')
	wcDF = pd.read_csv('..\longerThan4_25HRS.csv', low_memory=False)
	mxDF = pd.read_csv(r'..\long4_25.csv', low_memory=False)

	typesMX = mxDF.TYPE_MAINT.unique().tolist()
	typesMX.remove('G')
	typesMX.remove('W')
	typesMX.remove('F')
	
	# print(countMXbc(mxDF,typesMX[0]))
	
	# print((countMXbc(wcDF)))
	for item in typesMX:
		countMXbc(mxDF,item)

if __name__ == "__main__":
	main()