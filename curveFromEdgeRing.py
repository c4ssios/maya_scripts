import maya.cmds as cmds
import numpy

def curveFromEdgeRing():

    sel = cmds.ls(sl=True, fl=True)
      
    avgPositionList = []
    
    for s in sel:
        cmds.select(s, r=True)
        edgeNum = int(s.split('[')[1].replace(']',''))
        cmds.polySelect(elb=edgeNum)
        edgeLoopVtxList = cmds.ls(cmds.polyListComponentConversion(cmds.ls(sl=True, fl=True),tv=True), fl=True)
        
        posXlist = []
        posYlist = []
        posZlist = []
        
        for v in edgeLoopVtxList:
             posXlist.append(cmds.pointPosition(v)[0])
             posYlist.append(cmds.pointPosition(v)[1])
             posZlist.append(cmds.pointPosition(v)[2])
             
        avgPos = [numpy.mean(posXlist), numpy.mean(posYlist), numpy.mean(posZlist)]
        
        avgPositionList.append(avgPos)
        
    
    if len(avgPositionList)<=1:
        pass
    else:
        cmds.curve(d=3,p=avgPositionList)
