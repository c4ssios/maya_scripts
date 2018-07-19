import maya.cmds as cmds


def unfreezePosition():
    
    sel = cmds.ls(sl=True, l=True)
    
    for s in sel:
        if cmds.objectType(s, isType='transform')==0:
            cmds.warning(s+' is not a transformNode, skipped.')
        else:
            localRotPivPos = cmds.xform(s, rotatePivot=True,  q=True)
            worldPos = cmds.xform(s, translation=True, worldSpace=True, q=True)

            x = localRotPivPos[0]+worldPos[0]
            y = localRotPivPos[1]+worldPos[1]
            z = localRotPivPos[2]+worldPos[2]
            
            cmds.xform(s, translation=[-x,-y,-z], relative=True )
            cmds.makeIdentity(s, apply=True, translate=True)
            cmds.xform(s, translation=[x,y,z], relative=True)
