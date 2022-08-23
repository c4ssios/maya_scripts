import maya.cmds as cmds

def fixNormals(object):
    cmds.polyNormalPerVertex(object, ufn=True)
    cmds.polySoftEdge(object, angle=30, ch=False)
    

def fixNormalsOnSelection():
    sel = cmds.ls(sl=True, l=True)

    if len(sel)==0:
        cmds.warning("Nothing is Selected")
    
        
    else:
        for s in sel:
            fixNormals(s)
