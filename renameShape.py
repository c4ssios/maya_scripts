import maya.cmds as cmds

def renameShapeNode():
    
    meshes = cmds.ls(typ='mesh', l=True)
    if len(meshes)>0:
        for m in meshes:
            transform = cmds.listRelatives(m, p=True)[0]
            
            cmds.rename(m, transform + 'Shape')
