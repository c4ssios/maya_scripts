import maya.cmds as cmds
import sys
import os


def multiOBJimporter():
   
    objFilter = "*.obj"
    result = cmds.fileDialog2(fileFilter=objFilter, okCaption='Load', fm=4, rf=1, dialogStyle=2)
   
    del result[len(result)-1]
   
    for elem in result:
        longFileName = elem.split("/")
        fileName = longFileName[len(longFileName)-1]
        objName = fileName.split('.')
      
        cmds.file(elem, i=True, typ='OBJ', ra=True, mergeNamespacesOnClash=False, namespace=objName[0], options="mo=0")
