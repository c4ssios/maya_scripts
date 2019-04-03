import maya.cmds as cmds

def addArnoldSubdivAttr(subdLvl, pixelError):
	
	subDivMesh = cmds.ls('*_GES*', typ='mesh')
	
	for mesh in subDivMesh:
		cmds.setAttr(mesh+'.aiSubdivType', 1)
		cmds.setAttr(mesh+'.aiSubdivIterations', subdLvl)
		cmds.setAttr(mesh+'.aiSubdivAdaptiveMetric', 1)
		cmds.setAttr(mesh+'.aiSubdivPixelError', pixelError)
		print mesh + ' attributes set succesfully.'
