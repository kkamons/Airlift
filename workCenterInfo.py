import pandas as pd
import matplotlib.pyplot as plt



def locInfo(df):
    wcDict = {}
    for index,row in df.iterrows():
        wc = row['WORK_CENTER']
        manHrs = float(row['HOURS'])
        if wc in wcDict:
            currHrs = wcDict[wc]
            wcDict[wc] = manHrs+currHrs
        else:
            wcDict[wc]= manHrs

    return wcDict

def main():

    aliftTblPath = '../abbrev.csv'

    # read the file
    aliftTbl=pd.read_csv(aliftTblPath)
    # sort by the time columns
    greaterThan = aliftTbl[aliftTbl.iloc[:,12]>=4.25]
    lessThan = aliftTbl[aliftTbl.iloc[:,12]<4.25]

    # print(greaterThan[greaterThan['WORK_CENTER']])
    # print(greaterThan['WORK_CENTER'].size)
    gtData=locInfo(greaterThan)
    # ltData=locInfo(lessThan)
    print("length of gt data: ",len(gtData))
    # print("length of lt data: ", len(ltData))

    xvals=[]
    yvals=[]
    for key in gtData:
        xvals.append(key)
        yvals.append(gtData[key])
    
    plt.plot(xvals,yvals,label='Greater Than 4+15 Hrs')
    plt.xlabel('Locations')
    plt.ylabel('manHrs')
    plt.show()
    
if __name__ == "__main__":
    main()