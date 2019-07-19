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
	
	uniqueMat=[]

	for obj in objects:
		objShortName=obj.split('|')[-1]
		objectMaterialName = objShortName.split('_')[0]
		if objectMaterialName not in uniqueMat:
			uniqueMat.append(objectMaterialName)


	#Arnold Material Creation

	for m in uniqueMat:

		color = camelCaseSplit(m)[1].lower()
		materialType = camelCaseSplit(m)[0]

		materialName = m + '_MAT'

		if cmds.objExists(materialName):
			cmds.delete(materialName)
		if cmds.objExists(materialName+'_SG'):
			cmds.delete(materialName+'_SG')


		material = cmds.shadingNode('aiStandardSurface', asShader=True, n=materialName)
		materialSG = cmds.sets(name=materialName+'_SG', empty=True, renderable=True, noSurfaceShader=True)
		cmds.connectAttr(material+'.outColor', materialSG+'.surfaceShader')


		colorPreset = open(colorPresetFile, 'r')
		colorPresetParsed = yaml.load(colorPreset)

		arnoldMaterialPreset = open(arnoldMaterialPresetFile, 'r')
		arnoldMaterialParsed = yaml.load(arnoldMaterialPreset)

		for attribute in arnoldMaterialParsed[materialType]:
			#print arnoldMaterialParsed[materialType][attribute]
			cmds.setAttr(materialName+'.'+)
			#cmds.setAttr(materialName+'.baseColor', colorPresetParsed[color]['r'], colorPresetParsed[color]['g'], colorPresetParsed[color]['b'],type='double3')


