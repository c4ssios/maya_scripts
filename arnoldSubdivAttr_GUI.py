#!/usr/bin/env python
#title           :arnoldSubdiv.py
#description     :GUI to apply Arnold subdiv Attributes on shapes.
#date            :20200920
#==============================================================================

import maya.cmds as cmds

__title__ = "Arnold Subdivision Attributes"
__version__ = "0.1"
__author__ = "Nicolas Leblanc"
__company__ = "Home"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"


def applyAttributes(*args):
	print collectingAttributesValues()

def collectingAttributesValues():
	typeInput = cmds.optionMenu('subdivType_menu', q=True, v=True)
	iterationsInput = cmds.intSliderGrp('iterations_slider', q=True, v=True)
	adaptativeMetricInput = cmds.optionMenu('adaptativeMetric_menu', q=True, v=True)
	adaptativeErrorInput = cmds.floatSliderGrp('adaptativeError_slider', q=True, v=True)
	adaptativeSpaceInput = cmds.optionMenu('adaptativeSpace_menu', q=True, v=True)
	uvSmoothingInput = cmds.optionMenu('uvSmoothing_menu', q=True, v=True)
	smoothTangentInput = cmds.checkBox('smoothTangent_checkbox', q=True, v=True)
	ignoreFrustumInput = cmds.checkBox('ignoreFrustum_checkbox', q=True, v=True)
	heightInput = cmds.floatField("height_floatField", q=True, v=True)
	boundsPaddingInput = cmds.floatField("boundsPadding_floatField", q=True, v=True)
	scalarZeroValueInput = cmds.floatField("scalarZeroValue_floatField", q=True, v=True)
	enableAutobumpInput = cmds.checkBox('enableAutobump_checkbox', q=True, v=True)

	attributesList = [typeInput, iterationsInput, adaptativeMetricInput, adaptativeErrorInput, adaptativeSpaceInput, uvSmoothingInput, smoothTangentInput, ignoreFrustumInput, heightInput, boundsPaddingInput, scalarZeroValueInput, enableAutobumpInput]
	return attributesList

def arnoldSubdivUI():
	'''
	Create UI Window
	'''

	# Size Parameters

	windowWidth = 350
	windowHeight = 300
	labelSize = 150

	#Parameters List

	subdivTypeList = ["none", "catclark", "linear"]
	adaptativeMetricList = ["auto", "edge_length", "flatness"]
	adaptativeSpaceList = ["raster", "object"]
	uvSmoothingList = ["pin_corners", "pin_borders", "linear", "smooth"]
	applyToList = ["Current Selection", "*_GES", "*_GED", "*_GEV"]


	# Window Creation

	if (cmds.window("arnoldSubdiv_window", exists=True)):
		cmds.deleteUI("arnoldSubdiv_window")

	window = cmds.window("arnoldSubdiv_window", title= __title__+ ' ' +__version__, iconName='arnoldSubdiv', width=windowWidth, height=windowHeight)

	cmds.columnLayout( adjustableColumn=True )

	cmds.frameLayout(label="Subdivision", collapsable=True)
	cmds.separator( height=5, style='none' )


	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Type', w=labelSize, align="right")
	cmds.optionMenu('subdivType_menu')
	for subType in subdivTypeList:
		cmds.menuItem( label=subType )
	cmds.setParent(upLevel=True)


	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Iterations', w=labelSize, align="right")
	cmds.intSliderGrp("iterations_slider" ,min=0, max=10, value=1, step=1, field=True, cw=(2,150) )
	cmds.setParent(upLevel=True)


	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Adaptavive Metric', w=labelSize, align="right")
	cmds.optionMenu('adaptativeMetric_menu')
	for am in adaptativeMetricList:
		cmds.menuItem( label=am )
	cmds.setParent(upLevel=True)


	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Adaptavive Error', w=labelSize, align="right")
	cmds.floatSliderGrp("adaptativeError_slider" ,min=0, max=10, value=0, step=0.001, field=True, cw=(2,150) )
	cmds.setParent(upLevel=True)


	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Adaptavive Space', w=labelSize, align="right")
	cmds.optionMenu('adaptativeSpace_menu')
	for a in adaptativeSpaceList:
		cmds.menuItem( label=a )
	cmds.setParent(upLevel=True)


	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='UV Smoothing', w=labelSize, align="right")
	cmds.optionMenu('uvSmoothing_menu')
	for uv in uvSmoothingList:
		cmds.menuItem( label=uv )
	cmds.setParent(upLevel=True)

	cmds.columnLayout(co=("left", 152))
	cmds.checkBox("smoothTangent_checkbox", label="Smooth Tangents")
	cmds.setParent(upLevel=True)

	cmds.columnLayout(co=("left", 152))
	cmds.checkBox("ignoreFrustum_checkbox", label="Ignore Frustum Culling")
	cmds.setParent(upLevel=True)

	cmds.frameLayout(label="Displacement Attributes", collapsable=True, collapse=True,)

	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Height', w=labelSize, align="right")
	cmds.floatField("height_floatField", value=1.0)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Bounds Padding', w=labelSize, align="right")
	cmds.floatField("boundsPadding_floatField", value=0)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Scalar Zero Value', w=labelSize, align="right")
	cmds.floatField("scalarZeroValue_floatField", value=0)
	cmds.setParent(upLevel=True)

	cmds.columnLayout(co=("left", 152))
	cmds.checkBox("enableAutobump_checkbox", label="Enable Autobump")
	cmds.setParent(upLevel=True)

	cmds.setParent(upLevel=True)

	cmds.separator( height=20, style='double')

	cmds.rowLayout(numberOfColumns=2)
	cmds.button(label="Apply To", height=50, width=250, command=applyAttributes)
	cmds.optionMenu('applyTo_menu')
	for a in applyToList:
		cmds.menuItem(label=a)

	cmds.setParent(upLevel=True)

	cmds.separator( height=20, style='double')

	cmds.button(label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )