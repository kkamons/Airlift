import pandas as pd
import multiprocessing as mp
import psutil
import numpy as np
import sys

def dfSubset(path,size):

    # just read in the first 100k to speed up run time
    data=pd.read_csv(path, encoding='ISO-8859-1',low_memory=False)
    subset = data.sample(size)
    return subset


def main():

    inFile = str(sys.argv[1])
    subsetSize = int(sys.argv[2])
    
    # generate the subset
    smallDF = dfSubset(inFile,subsetSize)

    # store this dataframe in a csv file
    smallDF.to_csv('../abbrev.csv')


if __name__ == "__main__":
    main()