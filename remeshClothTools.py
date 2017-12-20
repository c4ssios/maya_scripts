import maya.cmds as cmds
import maya.mel
from math import *


__title__ = "Remesh Cloth Tools"
__version__ = '0.1'
__author__ = "Nicolas Leblanc"
__company__ = "Framestore"
__maintainer__ = "Nicolas Leblanc"
__email__ = "nicolas.leblanc@framestore.com"


def flattenToUVs(obj):

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

	
def matchScale(sourceObj, targetObj):
    
    sourceArea = cmds.polyEvaluate(sourceObj, wa=True)
    targetArea = cmds.polyEvaluate(targetObj, wa=True)
    scaleFactor = sqrt(sourceArea/targetArea)
    cmds.scale(scaleFactor, scaleFactor, scaleFactor, targetObj )
    cmds.makeIdentity(targetObj, apply=True, t=True , r=True, s=True)


def flattenSelectedObjects(*args):
    
    sel = cmds.ls(sl=True)
    for s in sel:
        flatName = s+'_flat'
        cmds.duplicate(s, n=flatName)
        flattenToUVs(flatName)
        matchScale(s,flatName)


        
def transfertRemeshed(*args):
    
    
    remeshList = cmds.listRelatives('remesh_GRP', c=True, ad=True,  typ='mesh')
    
    if len(remeshList)==0:
        cmds.warning('No remesh GRP')
    else:
        for mesh in remeshList :
            meshTR = cmds.listRelatives('*'+mesh, p=True)[0]
            flatObj = cmds.ls(meshTR, l=True)
            
            origFlat = ''
            remeshFlat = ''
            
            for f in flatObj:
                if 'remesh' in f:
                    remeshFlat = f
                else:
                    origFlat = f
            
            cmds.transferAttributes(origFlat, remeshFlat, transferUVs=2, spa=0, suv='map1', tuv= 'map1', sm=3)
            cmds.delete(remeshFlat, ch=True)
            
            costumePiece = meshTR.replace('_flat', '')
            
            cmds.transferAttributes( costumePiece, remeshFlat, pos=1, spa=3, sus= 'map1', tus= 'map1', sm=3 )
            cmds.delete(remeshFlat, ch=True)


def remeshClothUI():

    '''
    Create UI Window
    '''
    # Size Parameters

    windowSize = 250

    # Window Creation

    if (cmds.window("remeshCloth_window", exists=True)):
        cmds.deleteUI("remeshCloth_window")

    window = cmds.window("remeshCloth_window", title= __title__+ ' ' +__version__, iconName='remeshCloth', width=windowSize )

    cmds.columnLayout( adjustableColumn=True )


    '''
    Buttons
    '''

    cmds.separator( height=10, style='none' )
    cmds.button('flattenSelectedObjects_button', label = 'Flatten Selected Object(s)', height=50, command=flattenSelectedObjects)
    cmds.button('transfertRemeshedObj_button', label = 'Transfert Remeshed Objects', height=50, command=transfertRemeshed)
    cmds.separator( height=5, style='none' )

    cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

    cmds.setParent(upLevel=True)

    cmds.showWindow( window )

