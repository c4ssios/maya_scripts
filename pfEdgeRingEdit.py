from pymel.all import *
import pymel.core.datatypes as dt
from random import *

def edgeDistMove(mode):
	scaleFactor = floatSliderGrp ("fsl",q=True,value=True)
	percFactor = floatSliderGrp ("fsp",q=True,value=True)
	randCatch = radioCollection("rces1",q=True,select=True)
	edgeList = ls(sl=True,fl=True)
	distMode = radioCollection("rces0",q=True,select=True)
	for edge in edgeList:
		vertSel = ls(polyListComponentConversion(edge,tv=True),fl=True)
		leadPos = dt.Vector(xform(vertSel[0],q=True,ws=True,t=True))
		followPos = dt.Vector(xform(vertSel[1],q=True,ws=True,t=True))
		diffVec = followPos - leadPos
		mag = dt.length (diffVec)
		unit = dt.normal(diffVec)
		midPoint = leadPos + (unit * (mag/2))
		if distMode == "rp2":
			scaleFactor = scaleFactor
		elif distMode == "rp1":
			scaleFactor = ((mag / 100) * (percFactor/2))
		if mode==0:
			if randCatch=='rb1':
				randMoveA = uniform((-1*scaleFactor),scaleFactor)
				randMoveB = uniform((-1*scaleFactor),scaleFactor)
			else:
				randMoveA = scaleFactor
				randMoveB = scaleFactor
			finalPosA = leadPos + (unit * randMoveA)
			finalPosB = followPos + ((-1 * unit) * randMoveB)
		elif mode ==1 :
			if randCatch=='rb1':
				randMoveA = uniform(0,scaleFactor)
				randMoveB = uniform(0,(-1*scaleFactor))
			else:
				randMoveA = scaleFactor
				randMoveB = (-1 * scaleFactor)	
			finalPosA = leadPos + (unit * randMoveA)
			finalPosB = followPos + (unit * randMoveB)
		else :
			if randCatch=='rb1':
				randMoveA = uniform(0,(-1*scaleFactor))
				randMoveB = uniform(0,scaleFactor)
			else:
				randMoveA = (-1 * scaleFactor)
				randMoveB = scaleFactor	
			finalPosA = leadPos + (unit * randMoveA)
			finalPosB = followPos + (unit * randMoveB)			
		xform(vertSel[0],ws=True,t=finalPosA)
		xform(vertSel[1],ws=True,t=finalPosB)
		
def edgeDistSet(mode):
	scaleFactor = floatSliderGrp ("fsl",q=True,value=True)
	edgeList = ls(sl=True,fl=True)
	numEdges = len(edgeList)
	avmag = 0.0
	for edge in edgeList:
		vertSel = ls(polyListComponentConversion(edge,tv=True),fl=True)
		leadPos = dt.Vector(xform(vertSel[0],q=True,ws=True,t=True))
		followPos = dt.Vector(xform(vertSel[1],q=True,ws=True,t=True))
		diffVec = followPos - leadPos
		mag = dt.length (diffVec)
		avmag = avmag + mag
		unit = dt.normal(diffVec)
	averageLength = avmag / numEdges

	
	for edgeb in edgeList:
		vertSelB = ls(polyListComponentConversion(edgeb,tv=True),fl=True)
		leadPos = dt.Vector(xform(vertSelB[0],q=True,ws=True,t=True))
		followPos = dt.Vector(xform(vertSelB[1],q=True,ws=True,t=True))
		diffVec = followPos - leadPos
		unit = dt.normal(diffVec)
		mag = dt.length (diffVec)
		midPoint = leadPos + (unit * (mag/2))
		lengthDiff = averageLength / mag
		lengthDistDiff = scaleFactor / mag
		targetmag = mag * lengthDiff
		targetmagdist = mag * lengthDistDiff
		if mode ==1 :
			finalPosA = midPoint - (unit * (targetmag/2))
			finalPosB = midPoint +  (unit * (targetmag/2))
			xform(vertSelB[0],ws=True,t=finalPosA)
			xform(vertSelB[1],ws=True,t=finalPosB)
		elif mode ==0 :
			finalPosA = midPoint - (unit * (targetmagdist/2))
			finalPosB = midPoint +  (unit * (targetmagdist/2))
			xform(vertSelB[0],ws=True,t=finalPosA)
			xform(vertSelB[1],ws=True,t=finalPosB)
						


def buildUI():
	winName = 'edgeScaler'
	if (window (winName,exists=True)):
		deleteUI (winName)
	window (winName,w=400,h=150,title="edgeScaler UI")
	columnLayout(bgc=((0.184*1.5),(0.134*1.5),(0.11*1.5)))
	text (font = "boldLabelFont" ,label = "distance options")
	floatSliderGrp ('fsl',field=True,pre = 4,s = 0.001,label='distance',minValue = 0.001,maxValue = 2.0,value= 0.12,fieldMinValue = 0.001,fieldMaxValue = 2.0)
	floatSliderGrp ('fsp',field=True,pre = 4,s = 0.1,label='percentage',minValue = 0.1,maxValue = 99.9,value= 50,fieldMinValue = 0.001,fieldMaxValue = 99.9)
	text (label="")
	text (font = "boldLabelFont" ,label = "distance mode")
	radioCollection ('rces0')
	radioButton ('rp1',label='percentage')
	radioButton ('rp2',label='distance')
	radioCollection ('rces0',e=True,select = 'rp2')
	text (label="")
	text (font = "boldLabelFont" ,label = "randomisation")
	radioCollection ('rces1')
	radioButton ('rb1',label='on')
	radioButton ('rb2',label='off')
	text (label="")
	radioCollection ('rces1',e=True,select = 'rb2')
	button ('bt1',w=400,label='contract',c=Callback(edgeDistMove,1),bgc=((0.218*2.2),(0.165*2.2),(0.032*2.2)))
	button ('bt2',w=400,label='expand',c=Callback(edgeDistMove,2),bgc=((0.218*2.2),(0.165*2.2),(0.032*2.2)))
	button ('bt3',w=400,label='both',c=Callback(edgeDistMove,0),bgc=((0.218*2.2),(0.165*2.2),(0.032*2.2)))
	button ('bt4',w=400,label='set width to distance',c=Callback(edgeDistSet,0),bgc=((0.218*2.2),(0.165*2.2),(0.032*2.2)))
	button ('bt5',w=400,label='set width to average',c=Callback(edgeDistSet,1),bgc=((0.218*2.2),(0.165*2.2),(0.032*2.2)))
	showWindow (winName)





