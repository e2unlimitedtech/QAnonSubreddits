import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import random
import math

numClustersBegin=2
numClustersEnd=6
numClusters=2
edgeThreshold=4000
produceNodeList=False
fileRoot='QAnon_Reddit_Explicit_Clusters'
co_occurrence_file = "explicit_cooccurrence_matrix_11_12_2023.csv" #format:  term1, term2, freq

#clusterInputFile='TweetsContainingPatriotClustersMinDF50MaxDF30Pct4.csv' #'node.csv'  # clusters3.csv
#clusterInputFile='node.csv'
#co_occurrence_file = "edgeOnly.csv" #format:  term1, term2, freq
#co_occurrence_file = "TweetsContainingPatriotCooccurrenceMatrixMinDF50MaxDF30Pct.csv" #format:  term1, term2, freq

coordinates=[(-400,-200,200,400),(-100,100,200,400),(200,400,200,400),(-400,-200,-200,-400),(-100,100,-200,-400),(200,400,-200,-400) ]
colors=['red','blue','purple','pink','green','orange']
labels=['0','1','2','3','4','5']
interclusterEdgeColor='#999999'
intraclusterEdgeColor='#ffccff'

def getNewSpot(coords,listOfCurrent):
	(xStart,xStop,yStart,yStop) = coords
	count=0
	while True:
		if count==3 and xStop<0:
			xStop-=100
			yStop+=100
			count=0
		elif count==3 and xStop>0:
			xStop+=100
			yStop+=100
			count=0
		count+=1

		xdim=random.random()*xStop+xStart
		ydim=random.random()*yStop+yStart
		if len(listOfCurrent)==0:
			listOfCurrent.append((xdim,ydim))
			return xdim,ydim
		mindist=100000
		for (x,y) in listOfCurrent:
			dist=math.sqrt((xdim-x)**2 + (ydim-y)**2)
			if dist<mindist:
				mindist=dist
		if mindist>50:
			#print("distance is",dist)
			listOfCurrent.append((xdim,ydim))
			return xdim,ydim

def makeGraph(termLabels,outputFile):
	G=Network()
	G.set_options("""
		 var options = {
		 			"physics":{
		 				"enabled": false
		 			},
		 			"edges": {
	    				"color": {
	      					"inherit": true
	    							},
	   				 	"smooth": {
	   				 		"enabled": false
	   				 		}
	  				}
	  }
	  """)

	edgeList=[]
	nodeWeight={}

	for index,row in smallSet.iterrows():
		if row['TERM1'] in nodeWeight:
			nodeWeight[row['TERM1']]+=row['Freq']
		else:
			nodeWeight[row['TERM1']]=row['Freq']
		if row['TERM2'] in nodeWeight:
			nodeWeight[row['TERM2']]+=row['Freq']
		else:
			nodeWeight[row['TERM2']]=row['Freq']
		edgeList.append((row['TERM1'],row['TERM2'],row['Freq']))

	nodeSizes=[(4*edgeThreshold,10),(3*edgeThreshold,8),(2*edgeThreshold,6),(0,3)]

	nodePlacementList=[]

	print("graphing nodes")
	for node in nodeWeight:
		nw=15
		totalWeight=nodeWeight[node]
		for t in nodeSizes:
			if totalWeight<t[0]:
				nw=t[1]
		label=termLabels[node]
		labelInd=labels.index(label)
		xdim,ydim=getNewSpot(coordinates[labelInd],nodePlacementList)
		G.add_node(node,color=colors[labelInd],x=xdim,y=ydim,label=node,size=nw,font='15px arial black')		

	edgeWeights=[(4*edgeThreshold,2.5),(3*edgeThreshold,1.5),(2*edgeThreshold,1),(0,.5)]
	for (x,y,w) in edgeList:
		ew=5
		for t in edgeWeights:
			if w<t[0]:
				ew=t[1]
	#	if ew>=5:
	#		print (x,y,w)

		if termLabels[x]==termLabels[y]:
			G.add_edge(x,y,color=intraclusterEdgeColor,width=ew)
		else:		
			G.add_edge(x,y,color=interclusterEdgeColor,width=ew)

	G.save_graph(outputFile)

if __name__=='__main__':


	df= pd.read_csv(co_occurrence_file,names=['TERM1','TERM2','Freq'],skiprows=[0])
	#df=df.drop(0)

	df['TERM1']=df['TERM1'].astype('str')
	df['TERM2']=df['TERM2'].astype('str')
	df['Freq']=df['Freq'].astype('int')

	if produceNodeList:
		nodeList=set()
		with open ("potential_nodes_with_edges.csv",'w') as f:
			edgeThreshold=100
			smallSet=df[(df.TERM1 !=df.TERM2) & (df.Freq>=edgeThreshold) ]
			for index,row in smallSet.iterrows():
				f.write(f"{row['TERM1']},{row['TERM2']},{row['Freq']}\n") 
				nodeList.add(row['TERM1'])
				nodeList.add(row['TERM2'])
			
		with open ("potential_nodes_only.csv",'w') as f:
			for word in nodeList:
				f.write(f"{word}\n")

		exit()


	smallSet=df[(df.TERM1 !=df.TERM2) & (df.Freq>=edgeThreshold) ]

	for numClusters in range(numClustersBegin,numClustersEnd+1):
		clusterInputFile=fileRoot+str(numClusters)+'.csv' #'node.csv'  # clusters3.csv
		outputFile=fileRoot+str(numClusters)+".html"
		termLabels={}
		with open(clusterInputFile) as f:
			L=f.readlines()
			for line in L:
				row=line.split(',')
				termLabels[row[0].strip()]=row[1].strip()	
		makeGraph(termLabels,outputFile)
