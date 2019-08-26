import pandas as pd

def main():

    aliftTbl=pd.read_csv('../abbrev.csv')

    # find plane by tail # SN384
    plane = aliftTbl[aliftTbl['TAIL']=='SN384']

    # get all WUC_RD first 2 digits are  >= 11
    

    # get a df of where they were serviced and how long it took



    print(plane.head())
    print(plane.size)


if __name__ == "__main__":
    main()