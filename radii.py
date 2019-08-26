import pandas as pd
import math

# takes in a location and location data then returns the radius
def getRadius(loc,locData):


    # data is a list containing [radius,aircraft loc, base code]
    for i in range(len(locData)):
        if(str(locData.iloc[i,1])==str(loc) or str(locData.iloc[i,2])==str(loc)):
            data=[locData.iloc[i,0],locData.iloc[i,1],locData.iloc[i,2]]
            return int(data[0])
        # else:
        #     print("NONE")
        #     return False


# this one is dated... salvage it if you want
def getRadZone(radDict):
# returns a list of lists. list[i] is of form [startRad, endRad] for zone i
    radList=list(radDict.values())
    # print(max(radList)," ",min(radList))
    totDist=max(radList)-min(radList)
    # have to use the ceiling function otherwise will end up with a 6 which is index out of range
    width=math.ceil(totDist/6)

    zList=[]
    for i in range(6):
        zList.append([min(radList)+(width*i), min(radList)+(width*(i+1))-1])
    return zList

    # print(len(radList))
    # zones=[[] for i in range(6)]
    # # print(type(zones[2]))
    # # print(zones)
    # # zones[0].append("test1")
    # # print(zones)
    # # zones[1].append("test2")
    # # print(zones)
    # # zones[5].append("final")
    # # print(zones)
    # for rad in radList:
    #     truDist=rad-min(radList)
    #     # print(int(truDist//width))
    #     zones[int(truDist//width)].append(rad)
    # return zones

    # now we have 6 zones. zones[i] is a list that contains the radii in zone[i]
    # z

    # tot=0
    # for item in zones:
    #     print(len(item))
    #     tot+=len(item)


# this function takes in list of locations and the location dataframe
def genRadMatrix(locList,locData):

    # initialize a list of lists which will become the COST MATRIX
    matrix=[[] for i in range(len(locList))]
    
    # google how to store pandas dataframe as a csv and you'll see why
    columns = locList
    index = locList

    # go iterate the length of the location lists
    for i in range(len(locList)):
        count=0
        # now go back through the each location in the list
        for loc2 in locList:
            # print("inner - %f outer - %f" %(count,i))
            count+=1
            # get the radius for each base
            rad1=getRadius(locList[i],locData)
            rad2=getRadius(loc2,locData)

            # used to debug
            # print(type(rad1))
            # print(type(rad2))

            # if the radius is None that means the location does not exist
            if (rad1 is None or rad2 is None):
                matrix[i].append(-1)
            elif (rad1 is None):
                matrix[i].append(abs(rad1-rad2))

    newDF = pd.DataFrame(matrix, columns=columns, index=index)
    newDF.to_csv("../costMatrix.csv")
    return matrix

def main():
    # goal: determine radial zones
    # aliftTblPath = '../abbrev.csv'
    # locDataPath='../locationData.csv'
    # # read in the data files
    # aliftTbl=pd.read_csv(aliftTblPath)
    # locData=pd.read_csv(locDataPath)
    # locsDF = aliftTbl[['AIRCRAFT_LOCATION','BASE_CODE']]



#     Radius count is of form {radius: #activities at that radius}
#     radiusCount={1028: 36717, 6152: 209, 910: 4334, 6958: 7462, 633: 3410, 1165: 7670, 1094: 8925, 1167: 8426, 4241: 935, 5764: 17, 734: 1404, 1068: 84, 963: 32, 4158: 1159, 900: 24, 3260: 216, 1140: 16, 620: 2, 1020: 23, 889: 43, 4194: 246, 471: 31, 6007: 41, 394: 30, 790: 6, 567: 72, 4171: 20, 659: 18, 473: 35, 893: 9, 738: 6, 1487: 28, 6408: 3, 1049: 13, 132: 33, 3226: 6, 6039: 50, 862: 12, 998: 35, 6386: 26, 5966: 23, 594: 21, 576: 6, 2379: 6, 1952: 31, 444: 12, 2394: 20, 355: 21, 6566: 6, 999: 50, 4387: 4, 856: 12, 745: 11, 191: 7, 4319: 4, 941: 1, 6344: 29, 5616: 25, 1001: 33, 1162: 4, 1013: 8, 1138: 22, 3921: 18, 6208: 15, 6644: 17, 495: 7, 188: 4, 1786: 2, 1009: 22, 1279: 10, 1956: 13, 543: 9, 1347: 8, 1251: 5, 990: 4, 761: 5, 1078: 7, 6584: 2, 8903: 3, 4944: 13, 680: 13, 4915: 2, 6551: 8, 681: 5, 5397: 3, 1177: 2, 170: 1, 3221: 1, 1248: 7, 898: 2, 648: 3, 6757: 1, 996: 2, 5693: 9, 812: 3, 803: 8, 516: 1, 5029: 2, 5058: 1, 291: 2, 202: 1, 345: 3, 7110: 1, 1038: 3, 3249: 4, 6767: 1, 2356: 2, 746: 1, 953: 1, 684: 1}
#     sum=0
#     radiusList=list(radiusCount.keys())
#     print(radiusCount)
#     print(getRadZone(radiusList))

    wcDF = pd.read_csv('..\longerThan4_25HRS.csv', low_memory=False)
    locData = pd.read_csv('..\locationData.csv')
    acLocList = wcDF.AIRCRAFT_LOCATION.unique().tolist()
    bcList = wcDF.BASE_CODE.unique().tolist()
    locList = acLocList
    bcRadius={}


    for item in bcList:
        rad=getRadius(item,locData)

        if not(item in acLocList):
            if rad == None:
                # print(type(rad))
                continue
            else:
                locList.append(item)
                # rad=getRadius(item,locData)
            
                # bcRadius[item]=getRadius(item,locData)
                bcRadius[item]=rad
        else:
            if rad == None:
                # print(type(rad))
                continue
            else:
                # bcRadius[item]=getRadius(item,locData)
                bcRadius[item]=rad


    print(bcRadius)
    # print(bcRadius['0820']==None)
    print(getRadZone(bcRadius))
    # for index,wc in wcDF.iterrows():

    #     acLoc=wc[17]
    #     bc=wc[18]


    # print('get Radius  -  ',type(getRadius(8450,locData)))
    # print(len(bcList))
    # print(len(acLocList))
    # print('Rad Matrix')
    # print(genRadMatrix(locList,locData))


if __name__ == "__main__":
    main()




# this bit takes a while to run but all it does is
# count the number of times a maint activity occurs
# at a particular radial distacne

    # print(locsDF.iloc[77,0])
    # radiusCount={}
    # for i in range(len(aliftTbl)):
    #     locs=getRadius(locsDF.iloc[i,0],locsDF.iloc[i,1],locData)
    #     if(type(locs) == type([])):
    #         if(locs[0] in radiusCount):
    #             radiusCount[locs[0]]+=1
    #         else:
    #             radiusCount[locs[0]]=1
    # print(radiusCount)