import maya.cmds as cmds
import random
import re
import yaml


materialList = ['stone','paint','metal','wood','plastic','rubber','cloth','glass','ceramic','skin','hair','nail','bone','liquid','polysterene','leather','default','paper','felt','light', 'concrete', 'plant']
colorList = ['Grey','Black','White','Yellow','Red','Green','Blue','Orange','Purple','Brown','Pink','Colour','Clear','Mixed']

colorPresetFile = '/servers/Home/nleblanc/pythonScripts/maya/colorPreset.yaml'
arnoldMaterialPresetFile = '/servers/Home/nleblanc/pythonScripts/maya/arnoldMaterialPreset.yaml'


def randomRename():
	sel = cmds.ls(sl=True)
	for s in sel:
	    name = random.choice(materialList)+random.choice(colorList)+'_C_sphere' + ('%04d') % (sel.index(s)+1) + '_GEP'
	    cmds.rename(s, name)


def camelCaseSplit(string):
	splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split()
	return splitted


def filterSelection(selection):
	offenders = []
	for obj in selection:
		objShortName=obj.split('|')[-1]
		if '_' not in objShortName:
			offenders.append(obj)
		elif len(objShortName.split('_'))!=4:
			offenders.append(obj)
		elif len(camelCaseSplit(objShortName.split('_')[0]))!=2:
			offenders.append(obj)
		elif camelCaseSplit(objShortName.split('_')[0])[0] not in materialList:
			offenders.append(obj)
		elif camelCaseSplit(objShortName.split('_')[0])[1] not in colorList:
			offenders.append(obj)

	return offenders


def preSurfaceObjects():

	objects = cmds.ls('*:',typ='mesh', l=True)
	offenders = filterSelection(objects)

	if offenders:
		for o in offenders:
			objects.remove(o)
	
	if len(objects)==0:
		cmds.warning('Cant find any object name with material information.')

	else:

		uniqueMat=[]

		for obj in objects:
			objShortName=obj.split('|')[-1]
			objectMaterialName = objShortName.split('_')[0]

			materialName = objectMaterialName + '_MAT'
			materialSGName = materialName + '_SG'

			if objectMaterialName not in uniqueMat:
				uniqueMat.append(objectMaterialName)
				createMaterial(objectMaterialName, materialName, materialSGName)
			
 
			cmds.sets(obj, e=True, forceElement=materialSGName)



def createMaterial(material, materialName, shadingGroupName):


	color = camelCaseSplit(material)[1].lower()
	materialType = camelCaseSplit(material)[0]


	if cmds.objExists(materialName):
		cmds.delete(materialName)
	if cmds.objExists(shadingGroupName):
		cmds.delete(shadingGroupName)


	material = cmds.shadingNode('aiStandardSurface', asShader=True, n=materialName)
	materialSG = cmds.sets(name=shadingGroupName, empty=True, renderable=True, noSurfaceShader=True)
	cmds.connectAttr(material+'.outColor', shadingGroupName + '.surfaceShader')


	colorPreset = open(colorPresetFile, 'r')
	colorPresetParsed = yaml.load(colorPreset)

	arnoldMaterialPreset = open(arnoldMaterialPresetFile, 'r')
	arnoldMaterialParsed = yaml.load(arnoldMaterialPreset)

	for attribute in arnoldMaterialParsed[materialType]:
		attrValue = arnoldMaterialParsed[materialType][attribute]


		if type(attrValue)==str:
			colorValues =  [colorPresetParsed[color]['r'], colorPresetParsed[color]['g'], colorPresetParsed[color]['b']]

			if attrValue.split('color')[1]:
				operation = attrValue.split('color')[1][:1]
				factor = attrValue.split(operation)[-1]

				for v in colorValues:
					colorValues[colorValues.index(v)] = eval(str(v) + str(operation) + str(factor) )

			cmds.setAttr(materialName + '.' +attribute, colorValues[0], colorValues[1], colorValues[2], type='double3')


		if type(attrValue)==list:
			cmds.setAttr(materialName+'.'+ attribute ,attrValue[0], attrValue[1], attrValue[2], type='double3')

		if type(attrValue)==float:
			cmds.setAttr(materialName+'.'+ attribute, attrValue)


