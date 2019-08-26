import pandas as pd

###################################################
# sortByTime.py is used to generate the lessThan4Hrs.csv
# and greaterThan4Hrs.csv
###################################################

def readTheBigFile(path):
    data=pd.read_csv(path, encoding='ISO-8859-1',low_memory=False)
    return data

def main():

    aliftTbl = readTheBigFile('../WashUAirliftMDC.csv')


    # read the file
    # aliftTbl=pd.read_csv(aliftTblPath)

    # sort by the time columns
    greaterThan = aliftTbl[aliftTbl.iloc[:,11]>=4.25]
    # lessThan = aliftTbl[aliftTbl.iloc[:,12]<4.25]

    # write to csv for easy access
    greaterThan.to_csv("../longerThan4_25HRS.csv")
    # lessThan.to_csv("../lessThan4_25HRS.csv")
    # print(aliftTbl.iloc[0:5,11])

if __name__ == "__main__":
    main()