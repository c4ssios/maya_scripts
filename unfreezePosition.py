import maya.cmds as cmds


def unfreezePosition():
    
    sel = cmds.ls(sl=True, l=True)
    
    for s in sel:
        if cmds.objectType(s, isType='transform')==0:
            cmds.warning(s+' is not a transformNode, skipped.')
        else:
            worldPos = cmds.xform(s, rotatePivot=True,  q=True)
            cmds.xform(s, translation=[-worldPos[0], -worldPos[1], -worldPos[2]])
            cmds.makeIdentity(s, apply=True, translate=True)
            cmds.xform(s, translation=worldPos)
    
