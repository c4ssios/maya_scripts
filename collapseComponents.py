#!/usr/bin/env python
#title           :collapseComponents.py
#description     :
#date            :20180204
#==============================================================================

import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import makePlanar


__title__ = "Collapse Components"
__version__ = '0.1'
__author__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"


def getVertCoordList(vertList, axis):

	coordList = []
	for vert in vertList:
		coordList.append(cmds.pointPosition(vert)[int(axis)])

	return coordList


def getVertFromSel():

	sel = cmds.ls(sl=True, l=True, fl=True)
	vertList = []
	if len(sel)<1:
		pass
	else:
		vertList = cmds.ls(cmds.polyListComponentConversion( sel , tv=True ), fl=True)

	return vertList


def collapseComponents(axis, *args):

	vertList = getVertFromSel()
	if len(vertList) == 0:
		cmds.warning('Nothing is Selected')
	else:
		coordlist = getVertCoordList(vertList, axis)

		alignValue = 0
		if cmds.radioCollection('align_radioCollection', sl=True, q=True)=='avg_radioButton':
			alignValue = sum(coordlist) / float(len(coordlist))
		if cmds.radioCollection('align_radioCollection', sl=True, q=True)=='min_radioButton':
			alignValue = min(coordlist)
		if cmds.radioCollection('align_radioCollection', sl=True, q=True)=='max_radioButton':
			alignValue = max(coordlist)

		for v in vertList:
			if int(axis) == 0:
				cmds.move(alignValue,v, x=True, absolute=True)
			if int(axis) == 1:
				cmds.move(alignValue,v, y=True, absolute=True)
			if int(axis) == 2:
				cmds.move(alignValue,v, z=True, absolute=True)


def collapseOnNormalsAVG(*args):

	makePlanar.IMakePlanar()


def collapseComponentsUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowSize = 240

	# Window Creation

	if (cmds.window("collapseComponents_window", exists=True)):
		cmds.deleteUI("collapseComponents_window")

	window = cmds.window("collapseComponents_window", title= __title__+ ' ' +__version__, iconName='collapseComponents', width=windowSize, sizeable=False )

	cmds.columnLayout( adjustableColumn=True )

	cmds.separator( height=10, style='none' )
	cmds.text( label='World Axis Align' )
	cmds.separator( height=10, style='none' )

	cmds.rowLayout(numberOfColumns=3)
	cmds.button('X_button', label='X', w=(windowSize/3), h=(windowSize/3), command=partial(collapseComponents, '0'))
	cmds.button('Y_button', label='Y', w=(windowSize/3), h=(windowSize/3), command=partial(collapseComponents, '1'))
	cmds.button('Z_button', label='Z', w=(windowSize/3), h=(windowSize/3), command=partial(collapseComponents, '2'))
	cmds.setParent(upLevel=True)
	cmds.separator( height=20, style='double' )

	cmds.rowLayout(numberOfColumns=3)
	cmds.radioCollection('align_radioCollection', nci=3)
	cmds.radioButton('min_radioButton', label='Min', cl='align_radioCollection', w=(windowSize/3) )
	cmds.radioButton('avg_radioButton', label='Average', cl='align_radioCollection', sl=True, w=(windowSize/3) )
	cmds.radioButton('max_radioButton', label='Max', cl='align_radioCollection', w=(windowSize/3) )
	cmds.setParent(upLevel=True )

	cmds.separator( height=20, style='double' )
	cmds.button('normals_button', label='Normals Average', command=collapseOnNormalsAVG)
	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.showWindow( window )
	#cmds.window("collapseComponents_window", e=True, width=windowSize,)
