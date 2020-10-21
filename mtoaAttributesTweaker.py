import maya.cmds as cmds
import maya.mel as mel
from functools import partial


__title__ = "MTOA Attributes Tweaker"
__version__ = '0.3'
__author__ = "Nicolas Leblanc"
__company__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "nicolas.leblanc@dwarfanimation.com"



def applyToSelection(value, *args):
	sel = cmds.ls(sl=True, l=True)
	if len(sel)<1:
		cmds.warning('Nothing is selected.')
	else:
		for s in sel:
			shape = ''
			if cmds.objectType(s, isType='mesh')==1:
				shape = s
			else:
				shape = cmds.listRelatives(s, type='mesh', fullPath=True)[0]
			
			if value=='color':

				colorFromUI = cmds.colorInputWidgetGrp("mtoa_color_widget", rgb=True, q=True)

				if cmds.attributeQuery("mtoa_constant_color", n=shape, exists=True)==0:
					cmds.addAttr(shape, ln="mtoa_constant_color", at="double3")
					cmds.addAttr(shape, ln="mtoa_constant_colorX", at="double", p="mtoa_constant_color")
					cmds.addAttr(shape, ln="mtoa_constant_colorY", at="double", p="mtoa_constant_color")
					cmds.addAttr(shape, ln="mtoa_constant_colorZ", at="double", p="mtoa_constant_color")


				cmds.setAttr(shape+".mtoa_constant_color", colorFromUI[0],  colorFromUI[1], colorFromUI[2], type="double3")

			else:

				valueFromUI = cmds.floatSliderGrp('floatSliderGrp_' + value, value=True, q=True)

				if cmds.attributeQuery("mtoa_constant_" + value, n=shape, exists=True)==0:
					cmds.addAttr(mesh, ln="mtoa_constant_" + value, attributeType="double", dv=0)

				cmds.setAttr(shape+".mtoa_constant_" + value, valueFromUI)


def getFromSelection(value, *args):
	sel = cmds.ls(sl=True, l=True)
	if len(sel)==0:
		cmds.warning('Nothing is selected.')
	if len(sel)>1:
		cmds.warning('Select only One object.')

	else:
		for s in sel:
			shape = ''
			if cmds.objectType(s, isType='mesh')==1:
				shape = s
			else:
				shape = cmds.listRelatives(s, type='mesh', fullPath=True)[0]


			if cmds.attributeQuery("mtoa_constant_" + value, n=shape, exists=True)==0:
				cmds.warning('There is no MTOA constant ' + value + ' attribute on selection.')

			else:
				if value=='color':
					currentColor = cmds.getAttr(shape+'.mtoa_constant_color')[0]
					cmds.colorInputWidgetGrp("mtoa_color_widget", rgb=currentColor, edit=True)
				else:
					currentValue = cmds.getAttr(shape+'.mtoa_constant_' + value)
					cmds.floatSliderGrp('floatSliderGrp_' + value, v=currentValue, edit=True)


def mtoaAttributesTweakerUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowWidth = 300
	windowHeight = 500
	frameLayoutMargin = 10

	#Color
	frame_bgc = [0.18, 0.18, 0.18]


	# Window Creation

	if (cmds.window("mtoaAttributesTweaker_window", exists=True)):
		cmds.deleteUI("mtoaAttributesTweaker_window")

	window = cmds.window("mtoaAttributesTweaker_window", title= __title__+ ' ' +__version__, iconName='MTOA Attributes Tweaker', width=windowWidth, height=windowHeight)

	cmds.columnLayout( adjustableColumn=True )

	#color
	cmds.frameLayout(label="MTOA Constant Color", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.colorInputWidgetGrp("mtoa_color_widget", label='Color', rgb=(0.18, 0.18, 0.18) )
	cmds.button(label='Get From Selection', command=partial(getFromSelection, 'color'))
	cmds.button(label='Apply To Selection', height=50, command=partial(applyToSelection, 'color'))
	cmds.separator( height=5, style='none' )

	cmds.setParent(upLevel=True)

	#color jitter
	cmds.frameLayout(label="MTOA Constant Jitter", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.floatSliderGrp('floatSliderGrp_jitter', label='Object Color Jitter', field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=0.03, step=0.001 )
	cmds.button(label='Get From Selection', command=partial(getFromSelection, 'jitter'))
	cmds.button(label='Apply To Selection', height=50, command=partial(applyToSelection, 'jitter'))
	cmds.separator( height=5, style='none' )

	cmds.setParent(upLevel=True)

	#transmission
	cmds.frameLayout(label="MTOA Constant Transmission", collapsable=True, collapse=True, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.floatSliderGrp('floatSliderGrp_trans', label='Object Color Jitter', field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=0, step=0.001 )
	cmds.button(label='Get From Selection', command=partial(getFromSelection, 'trans'))
	cmds.button(label='Apply To Selection', height=50, command=partial(applyToSelection, 'trans'))
	cmds.separator( height=5, style='none' )

	cmds.setParent(upLevel=True)

	#IOR
	cmds.frameLayout(label="MTOA Constant IOR", collapsable=True, collapse=True, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.floatSliderGrp('floatSliderGrp_IOR', label='Object Color Jitter', field=True, minValue=0, maxValue=2, fieldMinValue=0, fieldMaxValue=2, value=1.52, step=0.001 )
	cmds.button(label='Get From Selection', command=partial(getFromSelection, 'IOR'))
	cmds.button(label='Apply To Selection', height=50, command=partial(applyToSelection, 'IOR'))
	cmds.separator( height=5, style='none' )

	cmds.setParent(upLevel=True)


	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
