import pandas as pd
import multiprocessing as mp
import psutil
import numpy as np

def readTheBigFile(path):
    # This method can read the big file

    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    # The fix for unicode error is ****encoding='ISO-8859-1'***
    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


    # just read in the first 100k to speed up run time
    data=pd.read_csv(path, encoding='ISO-8859-1',nrows=100000,low_memory=False)
    return data


def process_bigData(chunk):

    # gain speed by not sorting results
    grouped_obj = chunk.groupby(chunk.index,sort=False)
    func={''}

def main():

    # airliftTblPath = 'C:/Users/keith/Desktop/WashU/Spring19/ESE404/Project/washUAirlift/.csv'
    cmdCodePath = '../Command_Code_Lookup.txt'
    hMalPath = '../AirliftHMALCode.txt'
    locDataPath = '../locationData.txt'
    WUCPath = '../AirliftWUCLookupFiles.txt'
    MDCPath = '../WashUAirliftMDC.csv'
    aliftTblPath = '../abbrev.csv'

    # DONT NEED THE BIG TABLE
    # aliftTbl = readTheBigFile(MDCPath)
    aliftTbl=pd.read_csv(aliftTblPath)
    cmdCodes = pd.read_csv(cmdCodePath)
    hMal=pd.read_csv(hMalPath)
    locData = pd.read_csv(locDataPath)
    WUC=pd.read_csv(WUCPath)

    print(aliftTbl.shape)
    print(list(aliftTbl.columns.values))
    print('\n\n')
    print(aliftTbl.head())
    print(aliftTbl[["DATE","START_TIME","STOP_TIME","HOURS"]].head())



if __name__ == "__main__":
    main()