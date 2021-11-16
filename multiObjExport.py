import maya.cmds as cmds
import maya.mel as mel
import os
import shutil



def exportToObj(path, objName):
	exportFileName = path+"/"+objName+".obj"
	tempFolderPath = mel.eval("getenv TEMP")
	exportFileNameTemp = tempFolderPath+"/"+objName+".obj"

	cmds.file(exportFileNameTemp, force=True, es=True, type='OBJexport', pr=True,  options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1")

	shutil.move(exportFileNameTemp, exportFileName)

	print "Export " + exportFileName


def exportSelectedToOBJ():
	objToExport = cmds.ls(sl=True, l=True)

	if objToExport:
		exportPath = cmds.fileDialog2( okCaption='Select', fm=3,  dialogStyle=2)

		for obj in objToExport:
			cmds.select(obj, r=True)
			shortName = obj.split("|")[-1]
			exportToObj(exportPath[0], shortName)

		cmds.select(objToExport, r=True)


	else:
		cmds.warning("Nothing is Selected. Select at least one object.")