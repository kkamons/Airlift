import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#######################################################
# explore.py was just used for testing purposes...
# 
#######################################################




def readTheBigFile(path):
    # This method can read the big file

    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # The fix for unicode error is ****encoding='ISO-8859-1'***
    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


    # just read in the first 100k to speed up run time
    data=pd.read_csv(path, encoding='ISO-8859-1',low_memory=False)
    return data

def exploreWC(maindf,wc):
    
    # go through all the wc then get determine which type maint, action and when disc

    wcData=[]
    for i in range(len(wc)):
        # get truncated df with only the specified wc
        workCenter=wc[i]
        # print(workCenter)
        # for abbrev
        # df=maindf[maindf.iloc[:,5]==workCenter]
        # for bigFile
        df=maindf[maindf.iloc[:,4]==workCenter]
        # print(df.head())


        typemx=df.TYPE_MAINT.unique().tolist()
        acts=df.ACTION.unique().tolist()
        whenDisc=df.WHEN_DISC.unique().tolist()
        wcData.append([workCenter,typemx,acts,whenDisc])
    return wcData



    # preforms sorts by type, action and when disc
    # typemxSort=df.sort_values(by=['TYPE_MAINT'])
    # typemxSort.to_csv('../sortByMx.csv')

    # actionSort=df.sort_values(by=['ACTION'])
    # actionSort.to_csv('../sortByAction.csv')

    # wdSort=df.sort_values(by=['WHEN_DISC'])
    # wdSort.to_csv('../sortByWhenDisc.csv')

    # get type maint per 
def wcData(wcData):
    # just used for exploring the wc data
    for item in wcData:
        print("%s : metrics" % item[0])
        print("# types of maintence : %d   # actions taken : %d" % (len(item[1]),len(item[2])))


def showWC(maindf):
    # this list contains all of the wc in the main table
    # QE240 is the most popular
    wcList=maindf.WORK_CENTER.unique()
    countList=[]
    for i in range(len(wcList)):
        countList.append(maindf.WORK_CENTER.value_counts()[wcList[i]])

    temp=[]
    for i in range(len(wcList)):
        temp.append([countList[i],wcList[i]])
    temp=sorted(temp,reverse=True)

    wcListTrunc=[]
    countListTrunc=[]
    for i in range(20):
        countListTrunc.append(temp[i][0])
        wcListTrunc.append(temp[i][1])

    # this just shows the first 15
    # plt.plot(wcListTrunc,countListTrunc)
    # plt.show()

    return wcListTrunc

def main():



# DONT USE THIS PATH
    # airliftTblPath = 'C:/Users/keith/Desktop/WashU/Spring19/ESE404/Project/washUAirlift/.csv'


# use this path
    # ../FILE.csv 
    # the ../ represents the file above the current file
    cmdCodePath = '../Command_Code_Lookup.txt'
    # hMalPath = '../AirliftHMALCode.txt'
    locDataPath = '../locationData.txt'
    WUCPath = '../AirliftWUCLookupFiles.txt'
    MDCPath = '../WashUAirliftMDC.csv'
    aliftTblPath = '../abbrev.csv'
    lt4P = '..\longerThan4_25HRS.csv'

    # DONT NEED THE BIG TABLE
    # aliftTbl = readTheBigFile(MDCPath)
    aliftTbl=pd.read_csv(aliftTblPath)
    # bigFile=readTheBigFile(MDCPath)
    cmdCodes = pd.read_csv(cmdCodePath)
    hMal=pd.read_csv(hMalPath)
    locData = pd.read_csv(locDataPath)
    WUC=pd.read_csv(WUCPath)
    lt4=pd.read_csv(lt4P)
    wcDF = pd.read_csv('../wcData.csv')




if __name__ == "__main__":
    main()