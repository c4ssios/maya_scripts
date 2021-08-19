import maya.cmds as cmds

def locatorAtPivot():
    sel = cmds.ls(sl=True, l=True)
    if len(sel)==0:
        cmds.warning('Select at least on object.')
    else:
        for s in sel:


            targetPos = cmds.xform(s, q=True, rp=True, worldSpace=True)
            targetRot = cmds.xform(s, q=True, ro=True, worldSpace=True)
            targetScl = cmds.xform(s, q=True, s=True, relative=True)
            
            locName = s.split('|')[-1] +'_LOC'
                   
            cmds.spaceLocator(n=locName)
            cmds.setAttr('|'+locName+'.translateX', targetPos[0])
            cmds.setAttr('|'+locName+'.translateY', targetPos[1])
            cmds.setAttr('|'+locName+'.translateZ', targetPos[2])

            cmds.setAttr('|'+locName+'.rotateX', targetRot[0])
            cmds.setAttr('|'+locName+'.rotateY', targetRot[1])
            cmds.setAttr('|'+locName+'.rotateZ', targetRot[2])

            cmds.setAttr('|'+locName+'.scaleX', targetScl[0])
            cmds.setAttr('|'+locName+'.scaleY', targetScl[1])
            cmds.setAttr('|'+locName+'.scaleZ', targetScl[2])


            sourceParent = cmds.listRelatives(s, p=True, fullPath=True)[0]
            if sourceParent:
                cmds.parent(locName, sourceParent)

