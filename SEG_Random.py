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

#DEFINED CLASSES

class emanatedEdge:
	def __init__(self,_s,_j):
		self.source = _s
		self.junction = _j


class point:
	def __init__(self,_x,_y,_color):
		self.x = _x
		self.y = _y
		self.color = _color
	def __str__(self):
		return str(round(self.x,0)) + " _ " + str(round(self.y,0))


#DEFINED FUNCTIONS
def validPointXY(x,y,currentPoints):
	global minPointDistance
	global width
	global height
	for i in currentPoints:
		dist = math.sqrt((i.y-y)**2+(i.x-x)**2)
		if dist < minPointDistance or x < minPointDistance/2 or x > width-minPointDistance/2 or y < minPointDistance/2 or y > height-minPointDistance/2:
			return False
	return True

def validColorToDraw(color):
	if color == (150,150,150,255):
		return True
	if color[3]==0:
		return True
	return False

def rotatePoint(p, angle, pivot):
	px = p.x - pivot.x
	py = p.y - pivot.y

	qx = math.cos(angle) * px - math.sin(angle) * py
	qy = math.sin(angle) * px + math.cos(angle) * py

	qx += pivot.x
	qy += pivot.y
	return point(qx,qy,p.color)

def rotateJunctionBack(p, angle):
	global minPointDistance
	px = p.x
	py = p.y
	qx = math.cos(angle) * px - math.sin(angle) * py
	qy = math.sin(angle) * px + math.cos(angle) * py
	qx = round(qx)
	qy = round(qy)
	return point(qx,qy,p.color)
	
def rotatePointBack(p, pivot, angle, currentPoints):
	global minPointDistance
	px = p.x - pivot.x
	py = p.y - pivot.y
	qx = math.cos(angle) * px - math.sin(angle) * py
	qy = math.sin(angle) * px + math.cos(angle) * py
	qx += pivot.x
	qy += pivot.y
	for pp in currentPoints:
		dist = math.sqrt((pp.y-qy)**2+(pp.x-qx)**2)
		if dist < minPointDistance:
			return pp

def rotatePlane(pointSet, angle):
	newPoints = []
	for p in pointSet:

		qx = math.cos(angle) * p.x - math.sin(angle) * p.y
		qy = math.sin(angle) * p.x + math.cos(angle) * p.y
		newPoints.append(point((qx),(qy),p.color))
	return newPoints


def sortByY(item):
	return item.y
def drawPoint(dr,p,size,color):
	dr.ellipse((p.x-size, p.y-size, p.x+size, p.y+size), fill=color)
def drawSquare(dr,p,size,color):
	dr.polygon([(p.x-size,p.y-size),(p.x-size,p.y+size),(p.x+size,p.y+size),(p.x+size,p.y-size)],color)


#VARIABLES
imageOutput = True
csvOutput = False
emanationGrade = 2

# with open('em_results/emanationGraph.csv','a+') as csvh:
# 	csvh.write("Input Nodes,Graph Size,Construction Time,Spanning Ratio")

for iter in range(1):
	testInput = 0
	pointCount = 10
	steinerPointCount = 0
	width = 1000
	height = 1000
	minPointDistance = width/pointCount
	edgeWeight = 3
	dotSize = 5
	blockedRays = set()
	usedRGBs = []
	printMargin = 1
	hadChange = True
	points = []
	emanatedEdges = []
	connectedPoints = []
	sfnt = ImageFont.truetype("arial",22)
	mfnt = ImageFont.truetype("arial",42)
	img = Image.new('RGB',(width+printMargin,height),color=(255,255,255))
	drawer = ImageDraw.Draw(img)
	boundingBoxColor = (150,150,150)
	fileName = str(random.randint(1000000,2000000))

	if csvOutput:
		pointCount = random.randrange(10,pointCount)

	if testInput ==0:
		file = open("em_results/"+fileName+".txt","a+")
		for i in range(pointCount):
			h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
			r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
			while (r,g,b) in usedRGBs:
				h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
				r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
			usedRGBs.append((r,g,b))
			color=(r,g,b)
			x = round(random.random() * width)
			y = round(random.random() * width)
			while not validPointXY(x,y,points):
				x = round(random.random() * width)
				y = round(random.random() * width)
			points.append(point(x,y,color))
			file.write(str(int(x))+".000"+" "+str(int(y))+".000\n")
		file.close()

	else:
		inputFileName = str(testInput)
		file = open("em_results/"+inputFileName+".txt","r")
		for i in range(pointCount):
			h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
			r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
			while (r,g,b) in usedRGBs:
				h,s,l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
				r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
			usedRGBs.append((r,g,b))
			color=(r,g,b)
			line = str(file.readline())
			if line != "":
				lineitems = line.split(" ")
				x = int(lineitems[0].split(".")[0])
				y = int(lineitems[1].split(".")[0])
				points.append(point(x,y,color))
		file.close()

	#BOUNDING BOX SETTING
	topLeftCorner = point(0,0,(0,0,0))
	bottomRightCorner = point(0,0,(0,0,0))
	topLeftCorner.x = min(point.x for point in points)
	topLeftCorner.y = min(point.y for point in points)
	bottomRightCorner.x = max(point.x for point in points)
	bottomRightCorner.y = max(point.y for point in points)

	startTime = time.time()
	print("Emanation Start")
	#EMANATION GRAPH OBJECT CONSTRUCTION
	emGraph = nx.Graph()
	emGraph.add_nodes_from([(p.x,p.y) for p in points])


	if emanationGrade == 2:
		coneDegree = math.pi/2**2
		for rot in range(8):
			rotatedPoints = []
			if rot == 0:
				rotatedPoints = points
			else:    
				rotatedPoints = rotatePlane(points,rot*coneDegree)
			ySortedPoints = sorted(rotatedPoints,key=sortByY)
			for p in rotatedPoints:

				p_s = p
				p_csr = p
				p_csl = p
				pcList = []
				p_sFound = False
				p_csrFound = False
				p_cslFound = False
				disconnect = False

				#FINDING P_S
				for ps in ySortedPoints:
					if  ps == p:
						continue
					angle_p_s_p = math.atan2((ps.y-p.y),(ps.x-p.x))

					if angle_p_s_p >= 1.5*coneDegree and angle_p_s_p <= 2.5*coneDegree:
						p_s = ps
						p_sFound = True
						break
				if not p_sFound:			
					continue
				# if(points.index(rotatePointBack(p,point(0,0,p.color),-1*rot*coneDegree,points))==0 and points.index(rotatePointBack(p_s,point(0,0,p.color),-1*rot*coneDegree,points))==2):
				# 	1==1

				#FINDING P_CS
				for pcs in ySortedPoints:
					if pcs.x == p.x or pcs == p_s or pcs.y < p.y:
						continue
					angle_p_cs_p = math.atan2((pcs.y-p.y),(pcs.x-p.x))
					if angle_p_cs_p >= 1.5*coneDegree and angle_p_cs_p <= 2*coneDegree and angle_p_s_p >= 1.5*coneDegree and angle_p_s_p <= 2*coneDegree:
						p_csr = pcs
						p_csrFound = True
						break
					elif angle_p_cs_p >= 2*coneDegree and angle_p_cs_p <= 2.5*coneDegree and angle_p_s_p >= 2*coneDegree and angle_p_s_p <= 2.5*coneDegree:
						p_csl = pcs
						p_cslFound = True
						break

				#FINDING all P_C s
				if p_s.x > p.x:
					for pc in ySortedPoints:
						if pc.y >= p_s.y or pc.x == p.x:
							continue
						angle_p_c_p = math.atan2((pc.y-p.y),(pc.x-p.x))
						if angle_p_c_p >= 0.5*coneDegree and angle_p_c_p <= 1*coneDegree: #case 1-1
							pcList.append((pc,1))
						elif angle_p_c_p >= 1*coneDegree and angle_p_c_p <= 1.5*coneDegree: #case 2-1
							pcList.append((pc,2))
						elif angle_p_c_p >= 2.5*coneDegree and angle_p_c_p <= 3*coneDegree: #case 4-2
							pcList.append((pc,8))
						elif angle_p_c_p >= 3*coneDegree and angle_p_c_p <= 3.5*coneDegree: #case 3-2
							pcList.append((pc,7))
				else:				
					for pc in ySortedPoints:
						if pc.y >= p_s.y or pc.x == p.x:
							continue
						angle_p_c_p = math.atan2((pc.y-p.y),(pc.x-p.x))
						if angle_p_c_p >= 0.5*coneDegree and angle_p_c_p <= 1*coneDegree: #case 3-1
							pcList.append((pc,3))
						elif angle_p_c_p >= 1*coneDegree and angle_p_c_p <= 1.5*coneDegree: #case 4-1
							pcList.append((pc,4))
						elif angle_p_c_p >= 2.5*coneDegree and angle_p_c_p <= 3*coneDegree: #case 2-2
							pcList.append((pc,6))
						elif angle_p_c_p >= 3*coneDegree and angle_p_c_p <= 3.5*coneDegree: #case 1-2
							pcList.append((pc,5))

				#CHECK IF P_C INTERFERES

				if p_csrFound:
					sleft_p_s = rotatePoint(p_s,coneDegree/2,p)
					sleft_p_cs = rotatePoint(p_csr,coneDegree/2,p)
					if sleft_p_s.y > sleft_p_cs.y:
						continue
				elif p_cslFound:
					sright_p_s = rotatePoint(p_s,-1*coneDegree/2,p)
					sright_p_cs = rotatePoint(p_csl,-1*coneDegree/2,p)
					if sright_p_s.y > sright_p_cs.y:
						continue


				for item in pcList:
					p_c = item[0]
					case = item[1]

					left_p_s = rotatePoint(p_s,coneDegree,p)
					left_p_c = rotatePoint(p_c,coneDegree,p)
					farLeft_p_s = rotatePoint(p_s,1.5*coneDegree,p)
					farLeft_p_c = rotatePoint(p_c,1.5*coneDegree,p)
					right_p_s = rotatePoint(p_s,-1*coneDegree,p)
					right_p_c = rotatePoint(p_c,-1*coneDegree,p)
					farRight_p_s = rotatePoint(p_s,-1.5*coneDegree,p)
					farRight_p_c = rotatePoint(p_c,-1.5*coneDegree,p)
					if case == 1:
						if p_s.x > p_c.x:
							disconnect = True
						elif p_s.y > p_s.x + p_c.x-2*p.x + p_c.y:
							disconnect = True
					elif case == 2:
						if farLeft_p_s.y > farLeft_p_c.y or p_s.y-p_c.y > 0.5 * (p_c.x-p.x):
							disconnect = True
					elif case == 3:
						if left_p_s.y > left_p_c.y:
							disconnect = True
					elif case == 4:
						if (p_s.y - p_c.y) > (p.x - p_s.x):
							disconnect = True
					elif case == 5:
						if p_s.x < p_c.x:
							disconnect = True
						elif p_s.y > -1*p_s.x + p_c.y - p_c.x + 2*p.x:
							disconnect = True				
					elif case == 6:
						if farRight_p_s.y > farRight_p_c.y  or p_s.y-p_c.y > 0.5 * (p.x-p_c.x):
							disconnect = True
					elif case == 7:
						if right_p_s.y > right_p_c.y:
							disconnect = True
					elif case == 8:
						if (p_s.y - p_c.y) > (p_s.x - p.x):
							disconnect = True
				if disconnect:
					continue

				#CALCULATE JUNCTION POSITION
				j = point(p.x,p_s.y - abs(p_s.x-p.x),p.color)
				isSteiner = False
				if p.x != p_s.x and p.y != p_s.y:
					isSteiner = True				
				if rot != 0:
					p = rotatePointBack(p,point(0,0,p.color),-1*rot*coneDegree,points)
					p_s = rotatePointBack(p_s,point(0,0,p.color),-1*rot*coneDegree,points)
					j = rotateJunctionBack(j,-1*rot*coneDegree)
				else:
					p_s = rotatePointBack(p_s,point(0,0,p.color),0,points)
				if (str(p),str(p_s)) in connectedPoints or (str(p_s),str(p)) in connectedPoints:
					continue
				else:
					if isSteiner:
						steinerPointCount += 1					
					connectedPoints.append((str(p),str(p_s)))
					emanatedEdges.append(emanatedEdge(p,j))
					emanatedEdges.append(emanatedEdge(p_s,j))					
					emGraph.add_node((j.x,j.y))
					dist1 = math.sqrt((p.y-j.y)**2+(p.x-j.x)**2)
					dist2 = math.sqrt((p_s.y-j.y)**2+(p_s.x-j.x)**2)
					emGraph.add_edge((p.x,p.y),(j.x,j.y), weight=dist1)
					emGraph.add_edge((p_s.x,p_s.y),(j.x,j.y), weight=dist2)


	elif emanationGrade == 1:
		coneDegree = math.pi/2
		for rot in range(0,4):
			rotatedPoints = []
			if rot == 0:
				rotatedPoints = points
			else:    
				rotatedPoints = rotatePlane(points,rot*coneDegree)
			ySortedPoints = sorted(rotatedPoints,key=sortByY)
			for p in rotatedPoints:
				rp_sFound = False
				lp_sFound = False
				p_s = p
				rp_s = p
				lp_s = p
				if points.index(rotatePointBack(p,point(0,0,p.color),-1*rot*coneDegree,points)) == 4:
					1==1
				#FINDING P_S
				for ps in ySortedPoints:					
					if  ps.y <= p.y or ps == p:
						continue
					angle_p_s_p = math.atan2((ps.y-p.y),(ps.x-p.x))

					if not rp_sFound and not lp_sFound  and angle_p_s_p >= 0.5*coneDegree and angle_p_s_p <= 1*coneDegree:
						rp_s = ps
						rp_sFound = True
						continue
					if not rp_sFound and not lp_sFound  and angle_p_s_p >= 1*coneDegree and angle_p_s_p <= 1.5*coneDegree:
						lp_s = ps
						lp_sFound = True
						continue

					if rp_sFound and ps.y > rp_s.y and angle_p_s_p >= 0.5*coneDegree and angle_p_s_p <= 1*coneDegree:
						rotated_p_s = rotatePoint(rp_s,0.5*coneDegree,p)
						rotated_ps = rotatePoint(ps,0.5*coneDegree,p)
						if rotated_ps.y < rotated_p_s.y:
							c_lp_s = False
							for clps in ySortedPoints:
								angle_clps_p = math.atan2((clps.y-p.y),(clps.x-p.x))
								if clps.y <= rp_s.y or angle_clps_p <= coneDegree or angle_clps_p >= 1.5*coneDegree:
									continue
								elif clps.y > rp_s.y and clps.y < ps.y:
									c_lp_s = clps
								break
							if c_lp_s != False:
								rp_sFound = False
								lp_sFound = True
								lp_s = c_lp_s

							else:
								rp_s = ps

					if lp_sFound and ps.y > lp_s.y and angle_p_s_p >= 1*coneDegree and angle_p_s_p <= 1.5*coneDegree:
						rotated_p_s = rotatePoint(lp_s,-0.5*coneDegree,p)
						rotated_ps = rotatePoint(ps,-0.5*coneDegree,p)
						if rotated_ps.y < rotated_p_s.y:
							c_rp_s = False
							for crps in ySortedPoints:
								angle_crps_p = math.atan2((crps.y-p.y),(crps.x-p.x))
								if crps.y <= lp_s.y or angle_crps_p >= coneDegree or angle_crps_p <= 0.5*coneDegree:
									continue
								elif crps.y > lp_s.y and crps.y < ps.y:
									c_rp_s = crps
								break
							if c_rp_s != False:
								lp_sFound = False
								rp_sFound = True
								rp_s = c_rp_s
							else:
								lp_s = ps
				if not rp_sFound and not lp_sFound:
					continue
				if lp_sFound:
					p_s = lp_s
				else:
					p_s = rp_s

				#CALCULATE JUNCTION POSITION
				j = point(p.x,p_s.y,p.color)
				isSteiner = False
				if p.x != p_s.x and p.y != p_s.y:
					isSteiner = True				
				if rot != 0:
					p = rotatePointBack(p,point(0,0,p.color),-1*rot*coneDegree,points)
					p_s = rotatePointBack(p_s,point(0,0,p.color),-1*rot*coneDegree,points)
					j = rotateJunctionBack(j,-1*rot*coneDegree)
				else:
					p_s = rotatePointBack(p_s,point(0,0,p.color),0,points)
				if (str(p),str(p_s)) in connectedPoints or (str(p_s),str(p)) in connectedPoints:
					continue
				else:
					if isSteiner:
						steinerPointCount += 1					
					connectedPoints.append((str(p),str(p_s)))
					emanatedEdges.append(emanatedEdge(p,j))
					emanatedEdges.append(emanatedEdge(p_s,j))					
					emGraph.add_node((j.x,j.y))
					dist1 = math.sqrt((p.y-j.y)**2+(p.x-j.x)**2)
					dist2 = math.sqrt((p_s.y-j.y)**2+(p_s.x-j.x)**2)
					emGraph.add_edge((p.x,p.y),(j.x,j.y), weight=dist1)
					emGraph.add_edge((p_s.x,p_s.y),(j.x,j.y), weight=dist2)


	#CALCULATE SPANNING RATIO
	endTime = time.time()
	print("Emanation Ended in:",endTime-startTime)

	emSpanningRatio = (0,0,0)
	delSpanningRatio = (0,0,0)
	# shortestPaths = dict(nx.all_pairs_bellman_ford_path_length(emGraph))
	# for p1 in points:
	# 	for p2 in points:
	# 		if p1 != p2:
	# 			dist = math.sqrt((p1.y-p2.y)**2+(p1.x-p2.x)**2)
	# 			dilation = shortestPaths[(p1.x,p1.y)][(p2.x,p2.y)] / dist
	# 			if emSpanningRatio[0] < dilation:
	# 				emSpanningRatio = (dilation,points.index(p1),points.index(p2))
	print(emSpanningRatio)
	print(steinerPointCount)

	if imageOutput:
		for e in emanatedEdges:
			drawer.line(((e.source.x,e.source.y),(e.junction.x,e.junction.y)),'black',width=2)
		for e in emanatedEdges:
			drawSquare(drawer,e.junction,dotSize/2,'black')
		for x in points:
			drawer.text((x.x+dotSize,x.y-dotSize),str(points.index(x)),'red',font=mfnt)
			drawPoint(drawer,x,dotSize,x.color)
		img.load()
		res = img.resize((int(width+printMargin),int(height)),resample=Image.ANTIALIAS)
		res.show()
		res.save("em_results/"+fileName+".png")
	if csvOutput:
		row = [str(fileName),str(pointCount),str(endTime-startTime),str(emSpanningRatio[0])]
		with open('em_results/emanationGraph.csv','a',newline='') as csvFile:
			writer = csv.writer(csvFile)
			writer.writerow(row)
	else:
		break