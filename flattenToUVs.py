import maya.cmds as cmds
import maya.mel
from math import *


def flattenToUVs():

	sel = cmds.ls (sl=True, o=True)

	for obj in sel:
		numUVs = cmds.polyEvaluate(obj, uv=True)

		for i in range (0, numUVs):
			uvPos = cmds.polyEditUV(obj +  '.map[' + str(i) + ']', q=True)
			geoVert = cmds.polyListComponentConversion(obj +  '.map[' + str(i) + ']', fuv=True, tv=True)
			cmds.xform(geoVert, a=True, ws=True, t=(uvPos[0], uvPos[1], 0 ))

	cmds.makeIdentity(obj, apply=True, t=True , r=True, s=True)
	cmds.makeIdentity(obj, apply=False, t=True , r=True, s=True)
	cmds.move(-0.5, -0.5, 0 , obj)
	cmds.makeIdentity(obj, apply=True, t=True , r=True, s=True)
	cmds.makeIdentity(obj, apply=False, t=True , r=True, s=True)
	



def matchScale():

	sel = cmds.ls(sl=True)

	masterObj = sel[0]
	masterV1 = cmds.pointPosition(masterObj +'.vtx[0]')
	masterV2 = cmds.pointPosition(masterObj +'.vtx[1]')
	distanceMaster = sqrt( pow((masterV1[0]-masterV2[0]),2) + pow((masterV1[1]-masterV2[1]),2) + pow((masterV1[2]-masterV2[2]),2))

	sel.remove(sel[0])

	for s in sel:

		v1 = []
		v2 = []

		firstVertPos = cmds.pointPosition(s+'.vtx[0]')
		for i in firstVertPos:
			v1.append(i)

		secondVertPos = cmds.pointPosition(s+'.vtx[1]')
		for i in secondVertPos:
			v2.append(i)    

		distance = sqrt( pow((v1[0]-v2[0]),2) + pow((v1[1]-v2[1]),2) + pow((v1[2]-v2[2]),2))

		scaleFactor = distanceMaster/distance

		cmds.scale(scaleFactor, scaleFactor, scaleFactor, s )
