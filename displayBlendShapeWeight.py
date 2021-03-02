import maya.cmds as cmds


__title__ = "BS Weight Annotations"
__version__ = '0.2'
__author__ = "Nicolas Leblanc"
__company__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"


def createAnnotationForBS():

	sel = cmds.ls(sl=True, l=True)

	if len(sel)<1:
		cmds.warning('Nothing is selected.')

	if len(sel)>1:
		cmds.warning("Select Only 1 object with a blendShape deformer.")

	if len(sel)==1:

		bbox = cmds.exactWorldBoundingBox(sel[0])

		history = cmds.listHistory(sel[0])
		blendShapeNode = cmds.ls(history, type="blendShape", l=True)[0]

		blendAttrSize = cmds.getAttr(blendShapeNode+".weight")

		groupName = sel[0].split('|')[-1]+"_annotations_GRP"

		if not cmds.objExists(groupName):
			cmds.group(em=True, name=groupName)

		for i in range(len(blendAttrSize[0])):

			attrName = blendShapeNode + ".weight[" + str(i) + "]"
			attrValue = float(int(cmds.getAttr(attrName)*1000))/1000

			targetName = str(cmds.aliasAttr(attrName, q=True))

			annotationName = targetName+"_annotation"
    		
			if not cmds.objExists(annotationName):

				annotation = cmds.annotate(sel[0], tx=targetName + " : " + str(attrValue), p=(bbox[0]*2, bbox[4]-i, (bbox[2]+bbox[5])/2))
				tempAnnotationName = cmds.listRelatives(annotation, p=True)[0]

				cmds.rename(tempAnnotationName, annotationName)
				cmds.setAttr(annotationName + ".displayArrow", 0)
				cmds.setAttr(annotationName + "Shape.overrideEnabled", 1)
				cmds.setAttr(annotationName + "Shape.overrideRGBColors", 1)
				cmds.setAttr(annotationName + "Shape.overrideColorR", 1)
				cmds.setAttr(annotationName + "Shape.overrideColorG", 1)
				cmds.setAttr(annotationName + "Shape.overrideColorB", 0)

				cmds.parent(annotationName, groupName)


			cmds.setAttr(annotationName + ".text", targetName + " : " + str(attrValue), type="string")

			'''
			Create Expression to refresh value
			'''
		expressionNodeName = blendShapeNode+"_expression"
		expressionSTR = 'string $cmd = "displayBlendShapeWeight.updateBSAnnotations();";\npython($cmd);'

		if cmds.objExists(expressionNodeName):
			pass
		else:
			cmds.expression(n=expressionNodeName, s=expressionSTR)
			


def updateBSAnnotations():

	blendShapeNodeList = cmds.ls(type="blendShape")

	if len(blendShapeNodeList)>1 or len(blendShapeNodeList)==0:
		pass

	else:

		annotationList = cmds.ls(type="annotationShape")

		for a in annotationList:
			shapeName = "_".join(a.split('_')[:-1])

			shapeValue = float(int(cmds.getAttr(blendShapeNodeList[0]+'.'+shapeName)*1000))/1000
			cmds.setAttr(a + '.text', shapeName + ' : ' + str(shapeValue), type="string")

			'''
			Hack to force Maya annotations to refresh
			'''
			cmds.select(a, r=True)
			cmds.select(cl=True)

