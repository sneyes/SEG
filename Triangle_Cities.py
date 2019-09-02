import random
import colorsys
from PIL import Image, ImageDraw, ImageFont
import threading
import networkx as nx
import threading
import math
import time
import array
import numpy
import copy
import sys
import time
import csv
import glob
import os


#DEFINED CLASSES

class emanatedEdge:
	def __init__(self,_a,_b):
		self.A = _a
		self.B = _b


class point:
	def __init__(self,_x,_y,_color):
		self.x = _x
		self.y = _y
		self.color = _color
		self.degree = 0
		self.label = ""
	def __str__(self):
		return str(round(self.x,0)) + " _ " + str(round(self.y,0))
def drawPoint(dr,p,size,color):
	dr.ellipse((p.x-size/2, p.y-size/2, p.x+size/2, p.y+size/2), fill=color)

imageOutput = True
csvOutput = True
labeledImage = True

if csvOutput:
	headerRow = ["File Name","Configuration","Point Count","Steiner Point Count","Minimum Degree","Maximum Degree","Average Degree","Edge Count","Minimum Edge Len","Maximum Edge Len","Average Edge Len","Total Edge Length","Minimum Angle","Maximum Angle","Spanning Ratio"]
	with open('gml/triangle_results.csv','a',newline='') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(headerRow)

citiesFile = "gml/files/worldcities.csv"
degreeConstraints = [0,22.5,33]
for degreeConstraint in degreeConstraints:
	emGraph = nx.Graph()    
	pointCount = 0
	steinerPointCount = 0
	edgeCount = 0
	totalEdgeLength = 0
	printMargin = 100000000
	edgeSet = set()
	graphEdges = []
	width = 0
	height = 0
	dotSize = 3
	minimumAngle = 180
	maximumAngle = 0
	minimumEdgeLen = 100000000
	maximumEdgeLen = 0
	averageEdgeLen = 0
	minimumDegree = 100000000
	mfnt = ImageFont.truetype("arial",dotSize*3)
	maximumDegree = 0
	averageDegree = 0
	usedRGBs = []
	points = []
	fileName = str(random.randint(1000000,2000000))

	with open(citiesFile) as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		for row in readCSV:
			x = int(float(row[2])*10) + 2000
			y = int(-float(row[1])*10) + 2000
			lab = row[0]
			if x > width:
				width = x
			if y > height:
				height = y
			if x < printMargin:
				printMargin = x
			if y < printMargin:
				printMargin = y
			h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
			r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
			while (r,g,b) in usedRGBs:
				h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
				r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
			usedRGBs.append((r,g,b))
			color=(r,g,b)
			p = point(x*dotSize,y*dotSize,color)
			p.label = lab
			points.append(p)
		
	width = int((width+printMargin) * dotSize)
	height = int((height+printMargin) * dotSize)
	pointCount = len(points)
	fileName = "worldcities"
	img = Image.new('RGB',(width,height),color=(255,255,255))
	drawer = ImageDraw.Draw(img)

	nodeFile = open("triangle/nodeFiles/"+fileName+".node","w+")
	nodeFile.write(str(pointCount)+"  2  0  0""\n")
	for p in points:
		nodeFile.write(str(points.index(p))+"  "+str(p.x)+"  "+str(p.y)+"\n")
	nodeFile.close() 
	if degreeConstraint == 0:
		os.system("triangle\\triangle.exe -Q triangle\\nodeFiles\\"+fileName+".node")
	else:
		os.system("triangle\\triangle.exe -Qq"+str(degreeConstraint)+" triangle\\nodeFiles\\"+fileName+".node")

	nodeLines = open("triangle/nodeFiles/"+fileName+".1.node","r").readlines()

	for line in nodeLines:
		if nodeLines.index(line) == 0 or nodeLines.index(line) == len(nodeLines) or nodeLines.index(line) == (len(nodeLines)-1):
			continue
		parts = line.split()
		if len(points) > int(parts[0]):
			continue
		steinerPointCount+=1
		px = float(parts[1])
		py = float(parts[2])
		h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
		r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
		while (r,g,b) in usedRGBs:
			h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
			r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
		usedRGBs.append((r,g,b))
		color=(r,g,b)
		points.append(point(px,py,color))

	emGraph.add_nodes_from([(p.x,p.y) for p in points])
	eleLines = open("triangle/nodeFiles/"+fileName+".1.ele","r").readlines()
	for line in eleLines:
		if eleLines.index(line) == 0 or eleLines.index(line) == len(eleLines) or eleLines.index(line) == (len(eleLines)-1):
			continue
		parts = line.split()

		p1 = points[int(parts[1])]
		p2 = points[int(parts[2])]
		p3 = points[int(parts[3])]
		
		p1Angle = (math.atan2(p3.y - p1.y, p3.x - p1.x) - math.atan2(p2.y - p1.y, p2.x - p1.x)) * 180 / math.pi
		p2Angle = (math.atan2(p1.y - p2.y, p1.x - p2.x) - math.atan2(p3.y - p2.y, p3.x - p2.x)) * 180 / math.pi
		p3Angle = (math.atan2(p2.y - p3.y, p2.x - p3.x) - math.atan2(p1.y - p3.y, p1.x - p3.x)) * 180 / math.pi
		if p1Angle < 0: p1Angle+=360
		if p2Angle < 0: p2Angle+=360
		if p3Angle < 0: p3Angle+=360
		if p1Angle < minimumAngle : minimumAngle = p1Angle
		if p2Angle < minimumAngle : minimumAngle = p2Angle
		if p3Angle < minimumAngle : minimumAngle = p3Angle
		if p1Angle > maximumAngle : maximumAngle = p1Angle
		if p2Angle > maximumAngle : maximumAngle = p2Angle
		if p3Angle > maximumAngle : maximumAngle = p3Angle

		dist12 = math.sqrt((p1.y-p2.y)**2+(p1.x-p2.x)**2)
		dist13 = math.sqrt((p1.y-p3.y)**2+(p1.x-p3.x)**2)
		dist23 = math.sqrt((p2.y-p3.y)**2+(p2.x-p3.x)**2)
		if (str(p1)+" "+str(p2)) not in edgeSet and (str(p2)+" "+str(p1)) not in edgeSet:
			emGraph.add_edge((p1.x,p1.y),(p2.x,p2.y), weight=dist12)
			graphEdges.append(emanatedEdge(p1,p2))
			p1.degree += 1
			p2.degree += 1
			edgeSet.add(str(p1)+" "+str(p2))
			edgeSet.add(str(p2)+" "+str(p1))
		if (str(p1)+" "+str(p3)) not in edgeSet and (str(p3)+" "+str(p1)) not in edgeSet:
			emGraph.add_edge((p1.x,p1.y),(p3.x,p3.y), weight=dist13)
			graphEdges.append(emanatedEdge(p1,p3))
			p1.degree += 1
			p3.degree += 1
			edgeSet.add(str(p1)+" "+str(p3))
			edgeSet.add(str(p3)+" "+str(p1))
		if (str(p2)+" "+str(p3)) not in edgeSet and (str(p3)+" "+str(p2)) not in edgeSet:
			emGraph.add_edge((p2.x,p2.y),(p3.x,p3.y), weight=dist23)
			graphEdges.append(emanatedEdge(p2,p3))
			p2.degree += 1
			p3.degree += 1
			edgeSet.add(str(p2)+" "+str(p3))
			edgeSet.add(str(p3)+" "+str(p2))

	for e in graphEdges:
		edgeLen = (math.sqrt((e.A.y-e.B.y)**2+(e.A.x-e.B.x)**2)/dotSize)
		if edgeLen > maximumEdgeLen:
			maximumEdgeLen = edgeLen
		if edgeLen < minimumEdgeLen:
			minimumEdgeLen = edgeLen
		totalEdgeLength += edgeLen
	edgeCount = len(graphEdges)
	averageEdgeLen = totalEdgeLength / edgeCount


	spanningRatio = 0
	# shortestPaths = dict(nx.all_pairs_bellman_ford_path_length(emGraph))
	for p1 in points:
		if p1.degree > maximumDegree:
			maximumDegree = p1.degree
		if p1.degree < minimumDegree:
			minimumDegree = p1.degree
		averageDegree += p1.degree
		# for p2 in points:
		# 	if p1 != p2:
		# 		dist = math.sqrt((p1.y-p2.y)**2+(p1.x-p2.x)**2)
		# 		if dist != 0:
		# 			try:
		# 				dilation = shortestPaths[(p1.x,p1.y)][(p2.x,p2.y)] / dist
		# 			except KeyError: pass
		# 		if spanningRatio < dilation:
		# 			spanningRatio = dilation						
	
	averageDegree /= pointCount
	if imageOutput:
		for e in graphEdges:
			drawer.line(((e.A.x,e.A.y),(e.B.x,e.B.y)),'black',width=4)
		for x in points:
			if labeledImage:
				if(x.label != ""):
					drawer.text((x.x+dotSize,x.y+dotSize),x.label,'red',font=mfnt)
					drawPoint(drawer,x,dotSize*3,x.color)
		img.load()
		res = img.resize((int(width),int(height)),resample=Image.ANTIALIAS)
		res.save("triangle/images/"+fileName+"_"+str(degreeConstraint)+" DegConst.png")
	print("Processing file "+fileName+"_"+str(degreeConstraint)+" DegConst finished.")
	if csvOutput:
		row = [str(fileName),"Triangle DegConst "+str(degreeConstraint),str(pointCount),str(steinerPointCount),str(minimumDegree),str(maximumDegree),str(averageDegree),str(edgeCount),str(minimumEdgeLen),str(maximumEdgeLen),str(averageEdgeLen),str(totalEdgeLength),str(minimumAngle),str(maximumAngle),str(spanningRatio)]
		with open('gml/triangle_results.csv','a',newline='') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(row)