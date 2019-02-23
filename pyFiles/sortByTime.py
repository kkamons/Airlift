import pandas as pd


def main():

    # read the file
    aliftTbl=pd.read_csv(aliftTblPath)

    # sort by the time columns
    greaterThan = aliftTbl[aliftTbl.iloc[:,12]>=4.25]
    lessThan = aliftTbl[aliftTbl.iloc[:,12]<4.25]

    # write to csv for easy access
    greaterThan.to_csv("../longerThan4_25HRS.csv")
    lessThan.to_csv("../lessThan4_25HRS.csv")

if __name__ == "__main__":
    main()