import maya.cmds as cmds
import maya.mel as mel
from time import gmtime, strftime
from datetime import datetime
from math import *

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
    
    

    if cmds.radioCollection('interpolation_radioCollection', select=True, q=True) == 'curved_radioButton':
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


def transfertUVs(*args):

    sel = cmds.ls(sl=True)

    if len(sel)==2:
        sourceCurrentUV = cmds.polyUVSet(sel[0],cuv=True, q=True)
        targetCurrentUV = cmds.polyUVSet(sel[1],cuv=True, q=True)

        cmds.transferAttributes( sel[0], sel[1], transferUVs=2, spa=0, suv= sourceCurrentUV[0], tuv= targetCurrentUV[0], sm=3 )

        if cmds.checkBox('deleteHistory_checkBox', value=True, q=True)==1:
            cmds.delete( sel[1], ch=True)
        else:
            pass

    else:
        cmds.warning('Select only 2 objects')


def transfertShape(*args):

    sel = cmds.ls(sl=True)

    if len(sel)==2:
        sourceCurrentUV = cmds.polyUVSet(sel[0],cuv=True, q=True)
        targetCurrentUV = cmds.polyUVSet(sel[1],cuv=True, q=True)

        cmds.transferAttributes( sel[0], sel[1], pos=1, spa=3, sus= sourceCurrentUV[0], tus= targetCurrentUV[0], sm=3 )

        if cmds.checkBox('deleteHistory_checkBox', value=True, q=True)==1:
            cmds.delete( sel[1], ch=True)
        else:
            pass

    else:
        cmds.warning('Select only 2 objects')


def quadDrawTrigger(*args):
    mel.eval('dR_quadDrawTool;')

def shrinkwrapTrigger(*args):
    mel.eval('dR_shrinkWrap;')

def nameSpaceRemover(*args):
    cmds.namespace(setNamespace=':')
    namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True)
    while len(namespaces)>2:
        namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True)
        for d in ('UI', 'shared'):
            if d in namespaces:
                namespaces.remove(d)
        for n in namespaces:
            cmds.namespace(mergeNamespaceWithRoot=True, removeNamespace=n)
            print 'Namespace ' + n + 'removed.'


def MD_retopoToolsUI():

    windowSize = 300

    if (cmds.window("MD_retopoTools_window", exists=True)):
        cmds.deleteUI("MD_retopoTools_window")

    window = cmds.window("MD_retopoTools_window", title="MD Retopo Tools v0.17", iconName='MD_retopoTools', width=windowSize )

    cmds.columnLayout( adjustableColumn=True )
    cmds.separator( height=5, style='none')
    cmds.text('Vertex Spacing')
    cmds.separator( height=5, style='none')
    cmds.button(label='Even Distribute', height=30, command=distributeTrigger)

    cmds.rowLayout(numberOfColumns=2)
    cmds.radioCollection('interpolation_radioCollection')
    cmds.radioButton('staight_radioButton', label='Straight', sl=True)
    cmds.radioButton('curved_radioButton', label='Curved')
    cmds.setParent(upLevel=True)

    cmds.separator( height=10, style='double' )
    cmds.separator( height=5, style='none')
    cmds.text('Transfer Attributes')
    cmds.separator( height=5, style='none')
    cmds.button(label='Transfer UVs', height=30, command=transfertUVs)
    cmds.button(label='Transfer Shape', height=30, command=transfertShape)
    cmds.separator( height=5, style='none')
    cmds.checkBox('deleteHistory_checkBox', label='Delete History', value=1)

    cmds.separator( height=20, style='double' )
    cmds.text('Modelling Tools')
    cmds.separator( height=5, style='none')
    cmds.button(label='Quaddraw', height=30, command=quadDrawTrigger)
    cmds.button(label='Shrinkwrap Selection', height=30, command=shrinkwrapTrigger)

    cmds.separator( height=20, style='double' )
    cmds.text('Namespace Management')
    cmds.button(label='Namespace Remover', height=30, command=nameSpaceRemover)


    cmds.separator( height=20, style='double' )

    cmds.button( label='Close', height=50, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

    cmds.setParent(upLevel=True)

    cmds.showWindow( window )


