import maya.cmds as cmds
import maya.mel as mel
from time import gmtime, strftime
from datetime import datetime
from math import *


__title__ = "Even Distribute"
__version__ = '0.8'
__author__ = "Nicolas Leblanc"
__company__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"



def uniqueNameGenerator(*args):
    uniqueName = 'tmpObject'+str(datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
    return uniqueName

def edgeLoopSorting(*args):
    sel = cmds.ls(sl=True, fl=True)
    edgeLoop = []
    for s in sel:
        loop = []
        cmds.select(s, r=True)
        entireEdgeLoop = cmds.ls(s, cmds.polySelectSp(q=True, loop=True), fl=True)
        tmpFlatList = sum(edgeLoop, [])
        for e in entireEdgeLoop:
            if e in sel and e not in loop and e not in tmpFlatList: 
                loop.append(e)
            else:
                pass
        if len(loop)>0:
            edgeLoop.append(loop)
    return edgeLoop

def distributeTrigger(*args):
    edgeLoopList = edgeLoopSorting()

    for edgeLoop in edgeLoopList:
        cmds.select(edgeLoop, r=True)
        distribute(edgeLoop)
    cmds.select(sum(edgeLoopList, []), r=True)



def distribute(edgeLoop):
    
    edgeSel = cmds.ls(edgeLoop, fl=True)
    vertList = cmds.ls(cmds.polyListComponentConversion(edgeSel, toVertex=True), fl=True)
    
    tempCurveName = uniqueNameGenerator()
    

    if cmds.radioCollection('interpolation_radioCollection2', select=True, q=True) == 'curved_radioButton':
        cmds.polyToCurve(n=tempCurveName, form=2, degree=3, ch=False)      

    else:
        cmds.polyToCurve(n=tempCurveName, form=2, degree=1, ch=False)
        CVtoDelete = []
        for i in range(1, len(vertList)-1):
            CVtoDelete.append(tempCurveName + '.cv[' + str(i) + ']')   
        cmds.delete(CVtoDelete)

    cmds.rebuildCurve(tempCurveName, ch=False, replaceOriginal=True, rt=0, end=1, kr=0, kep=1, kt=0, s=len(vertList)-1, d=3, tol=0.01)

    
    accuracy = 4
    
    firstEPPos = [round(elem, accuracy) for elem in cmds.pointPosition( tempCurveName+'.ep[0]' )]
    vertListOrdered = []
    for edge in edgeSel:
        
        edgeVert = cmds.ls(cmds.polyListComponentConversion(edge, toVertex=True), fl=True)
        
        for v in edgeVert:
            
            vPos = [round (elem, accuracy) for elem in cmds.pointPosition(v)]

            if vPos==firstEPPos:
                vertListOrdered.append(v)

    while len(vertListOrdered)<len(vertList):
        for edge in edgeSel:
            vertEdge = cmds.ls(cmds.polyListComponentConversion(edge, toVertex=True), fl=True)
            
            counter = []
            
            for v in vertEdge:
                if v not in vertListOrdered:
                    counter.append(v)
                else:
                    pass
                    
            if len(counter)==1:
                vertListOrdered.append(counter[0])
            else:
                pass
                
    for v in vertListOrdered:
        epPos = cmds.pointPosition(tempCurveName+'.ep[' + str(vertListOrdered.index(v)) +']')
        cmds.move(epPos[0], epPos[1], epPos[2], v, absolute=True)

    cmds.delete(tempCurveName)

    #cmds.hilite(cmds.listRelatives(edgeSel,parent=True), r=True)
    #cmds.select(edgeSel, r=True)


def evenDistributeUI():

    windowSize = 300

    if (cmds.window("evenDistribute_window", exists=True)):
        cmds.deleteUI("evenDistribute_window")

    window = cmds.window("evenDistribute_window", title= __title__+ ' ' +__version__, iconName='evenDistribute', width=windowSize )

    cmds.columnLayout( adjustableColumn=True )
    cmds.separator( height=5, style='none')
    cmds.text('Vertex Spacing')
    cmds.separator( height=5, style='none')
    cmds.button(label='Even Distribute', height=30, command=distributeTrigger)

    cmds.rowLayout(numberOfColumns=2)
    cmds.radioCollection('interpolation_radioCollection2')
    cmds.radioButton('staight_radioButton', label='Straight', sl=True)
    cmds.radioButton('curved_radioButton', label='Curved')
    cmds.setParent(upLevel=True)

    cmds.separator( height=20, style='double' )

    cmds.button( label='Close', height=50, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

    cmds.setParent(upLevel=True)

    cmds.showWindow( window )


