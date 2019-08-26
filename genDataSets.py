from ortools.linear_solver import pywraplp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

lt4Data = pd.read_csv(r'..\long4_25.csv', low_memory=False)

def genMDC(typeMX):

	typeMXDF = lt4Data.loc[lt4Data['TYPE_MAINT'] == typeMX]
	fn='../'+typeMX+'data.csv'
	print(typeMXDF.shape, '  ', typeMX)
	# typeMXDF.to_csv(fn)

def main():
	mxTypes=lt4Data.TYPE_MAINT.unique().tolist()


	for item in mxTypes:
		genMDC(item)


if __name__ == "__main__":
	main()