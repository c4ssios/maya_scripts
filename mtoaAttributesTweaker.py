import maya.cmds as cmds
import maya.mel as mel


__title__ = "MTOA Attributes Tweaker"
__version__ = '0.1'
__author__ = "Nicolas Leblanc"
__company__ = "Dwarf Animation"
__maintainer__ = "Nicolas Leblanc"
__email__ = "nicolas.leblanc@dwarfanimation.com"



def applyColorToSelection(*args):
	colorFromUI = cmds.colorInputWidgetGrp("mtoa_color_widget", rgb=True, q=True)

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
			
			if cmds.attributeQuery("mtoa_constant_color", n=shape, exists=True)==0:
				cmds.addAttr(shape, ln="mtoa_constant_color", at="double3")
				cmds.addAttr(shape, ln="mtoa_constant_colorX", at="double", p="mtoa_constant_color")
				cmds.addAttr(shape, ln="mtoa_constant_colorY", at="double", p="mtoa_constant_color")
				cmds.addAttr(shape, ln="mtoa_constant_colorZ", at="double", p="mtoa_constant_color")


			cmds.setAttr(shape+".mtoa_constant_color", colorFromUI[0],colorFromUI[1],colorFromUI[2], type="double3")



def getFromSelection():
	pass


def mtoaAttributesTweakerUI():

	'''
	Create UI Window
	'''
	# Size Parameters

	windowWidth = 300
	windowHeight = 300
	frameLayoutMargin = 10

	#Color
	frame_bgc = [0.18, 0.18, 0.18]


	# Window Creation

	if (cmds.window("mtoaAttributesTweaker_window", exists=True)):
		cmds.deleteUI("mtoaAttributesTweaker_window")

	window = cmds.window("mtoaAttributesTweaker_window", title= __title__+ ' ' +__version__, iconName='MTOA Attributes Tweaker', width=windowWidth, height=windowHeight)

	cmds.columnLayout( adjustableColumn=True )

	cmds.frameLayout(label="MTOA Constant Color", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.colorInputWidgetGrp("mtoa_color_widget", label='Color', rgb=(0.18, 0.18, 0.18) )
	cmds.button(label='Get From Selection')
	cmds.button(label='Apply To Selection', height=50, command=applyColorToSelection)

	cmds.setParent(upLevel=True)
	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
