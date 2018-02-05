#!/usr/bin/env python
#title           :randomColor.py
#description     :Apply a Zbrush style random color of every selected objects using vertex color.
#date            :20161010
#==============================================================================

import maya.cmds as cmds
from functools import partial
import random


__title__ = "Object Random Color"
__version__ = '0.21'
__author__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"




def triggerRandomColor(objects, *args):
	'''
	Listing objects and triggering definition
	'''

	objectList=[]

	if objects=='selected':
		objectList = cmds.listRelatives(cmds.ls(sl=True, l=True), typ='mesh', f=True)

	if objects=='all':
		objectList = cmds.ls(typ='mesh', l=True)

	if objectList is None or len(objectList)==0:

		if objects=='selected':
			cmds.warning('Nothing is Selected. Select a least one object.')

		if objects=='all':
			cmds.warning('There is no mesh in the scene.')

	else:
		if cmds.checkBox('useGeoId_checkbox', value=1, q=True):

			geoIdList = []
			geoIdObjList = []
			noGeoIdObjList = []

			for o in objectList:

				if cmds.attributeQuery('geoId', n=o, ex=True):

					geoIdObjList.append(o)
					geoId = cmds.getAttr(o+'.geoId')

					if geoId not in geoIdList:

						geoIdList.append(geoId)

				else:

					noGeoIdObjList.append(o)


			if len(geoIdList)>0:
				for geoId in geoIdList:
					matchingObjList = []
					for obj in geoIdObjList:
						if cmds.getAttr(obj+'.geoId')==geoId:

							matchingObjList.append(obj)

					applyRandomColor(matchingObjList)


			if len(noGeoIdObjList)>0:

				applyRandomColor(noGeoIdObjList)



		else:

			for o in objectList:

				applyRandomColor(o)



def applyRandomColor(obj):
	'''
	Apply Random Color definition
	'''

	red = random.uniform(0, 1)
	green = random.uniform(0, 1)
	blue = random.uniform(0, 1)
	cmds.polyColorPerVertex(obj, r=red, g=green, b=blue, a=1, cdo=True)
	cmds.polyOptions(obj, colorMaterialChannel='diffuse')


def removeRandomColor(*args):
	'''
	Apply Random definition
	'''

	for shape in cmds.ls(typ='mesh', l=True):
		if cmds.polyColorSet(shape, allColorSets=True, q=True):
			cmds.polyColorSet(shape,delete=True)
		else:
			pass


def randomColorUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowSize = 250

	# Window Creation

	if (cmds.window("randomColor_window", exists=True)):
		cmds.deleteUI("randomColor_window")

	window = cmds.window("randomColor_window", title= __title__+ ' ' +__version__, iconName='randomColor', width=windowSize )

	cmds.columnLayout( adjustableColumn=True )


	'''
	Buttons
	'''

	cmds.separator( height=10, style='none' )
	cmds.button('applyRandomColorSelected_button', label = 'Apply Random Color on Selected Object(s)', height=50, command=partial(triggerRandomColor, 'selected'))
	cmds.button('applyRandomColorAll_button', label = 'Apply Random Color on All Object(s)', height=50, command=partial(triggerRandomColor, 'all'))
	cmds.separator( height=5, style='none' )
	cmds.checkBox('useGeoId_checkbox', l='Apply per geoID')
	cmds.separator( height=20, style='double' )
	cmds.button('remove_button', label = 'Remove Random Color', height=30, command=removeRandomColor)

	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)

	cmds.showWindow( window )
