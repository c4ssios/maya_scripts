import maya.cmds as cmds
import maya.mel as mel
from functools import partial


__title__ = "PRman Attributes Tweaker"
__version__ = '0.2'
__author__ = "Nicolas Leblanc"
__company__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"



def applyToSelection(value, *args):
	sel = cmds.ls(sl=True, l=True)
	if len(sel)<1:
		cmds.warning('Nothing is selected.')
	else:
		for s in sel:
			
			if value=='diffuse_color':

				colorFromUI = cmds.colorInputWidgetGrp("prman_color_widget", rgb=True, q=True)

				if cmds.attributeQuery("rmanCdiffuse_color", n=s, exists=True)==0:
					cmds.addAttr(s, ln="rmanCdiffuse_color", at="float3")
					cmds.addAttr(s, ln="rmanCdiffuse_colorR", at="float", p="rmanCdiffuse_color")
					cmds.addAttr(s, ln="rmanCdiffuse_colorG", at="float", p="rmanCdiffuse_color")
					cmds.addAttr(s, ln="rmanCdiffuse_colorB", at="float", p="rmanCdiffuse_color")


				cmds.setAttr(s+".rmanCdiffuse_color", colorFromUI[0],  colorFromUI[1], colorFromUI[2], type="double3")

				if cmds.checkBox("applyVertexColor_checkbox", v=True, q=True)==1:
					cmds.polyColorPerVertex(s, r=colorFromUI[0], g=colorFromUI[1], b=colorFromUI[2], a=1, cdo=True)
					cmds.polyOptions(s, colorMaterialChannel='diffuse')

			else:

				valueFromUI = cmds.floatSliderGrp('floatSliderGrp_' + value, value=True, q=True)

				if cmds.attributeQuery("rmanF" + value, n=s, exists=True)==0:
					cmds.addAttr(s, ln="rmanF" + value, at="float", dv=0)

				cmds.setAttr(s+".rmanF" + value, valueFromUI)


def removeFromSelection(value, *args):
	sel = cmds.ls(sl=True, l=True)
	if len(sel)<1:
		cmds.warning('Nothing is selected.')
	else:
		for s in sel:
			
			if value=='diffuse_color':
				if cmds.attributeQuery("rmanCdiffuse_color", n=s, exists=True)==1:
					cmds.deleteAttr(s, at='rmanCdiffuse_color')

				if cmds.polyColorSet(s, allColorSets=True, q=True):
					cmds.polyColorSet(s,delete=True)

			else:
				if cmds.attributeQuery("rmanF" + value, n=s, exists=True)==1:
					cmds.deleteAttr(s, at="rmanF" + value)


def getFromSelection(value, *args):
	sel = cmds.ls(sl=True, l=True)
	if len(sel)==0:
		cmds.warning('Nothing is selected.')
	if len(sel)>1:
		cmds.warning('Select only One object.')

	else:
		for s in sel:

			if value=='diffuse_color':
				if cmds.attributeQuery("rmanC" + value, n=s, exists=True)==0:
					cmds.warning('There is no RMAN ' + value + ' attribute on selection.')
				else:
					currentColor = cmds.getAttr(s+'.rmanCdiffuse_color')[0]
					cmds.colorInputWidgetGrp("prman_color_widget", rgb=currentColor, edit=True)
			else:
				if cmds.attributeQuery("rmanF" + value, n=s, exists=True)==0:
					cmds.warning('There is no RMAN ' + value + ' attribute on selection.')
				else:
					currentValue = cmds.getAttr(s+'.rmanF' + value)
					cmds.floatSliderGrp('floatSliderGrp_' + value, v=currentValue, edit=True)


def prmanAttributesTweakerUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowWidth = 300
	windowHeight = 650
	frameLayoutMargin = 10

	#Color
	frame_bgc = [0.18, 0.18, 0.18]


	# Window Creation

	if (cmds.window("prmanAttributesTweaker_window", exists=True)):
		cmds.deleteUI("prmanAttributesTweaker_window")

	window = cmds.window("prmanAttributesTweaker_window", title= __title__+ ' ' +__version__, iconName='PRMAN Attributes Tweaker', width=windowWidth, height=windowHeight, sizeable=False)

	cmds.columnLayout( adjustableColumn=True )

	#color
	cmds.frameLayout(label="Diffuse Color", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.colorInputWidgetGrp("prman_color_widget", label='Color', rgb=(0.18, 0.18, 0.18) )
	cmds.button('button_getFromSelection_color', label='Get From Selection', command=partial(getFromSelection, 'diffuse_color'))
	cmds.button('button_applyToSelection_color', label='Apply To Selection', height=50, command=partial(applyToSelection, 'diffuse_color'))
	cmds.button('button_removeOverrides_color', label='Remove Color Overrides', command=partial(removeFromSelection, 'diffuse_color'))
	cmds.separator( height=5, style='none' )

	cmds.checkBox('applyVertexColor_checkbox', l='Apply Vertex Color', v=1)
	cmds.separator( height=5, style='none' )

	cmds.setParent(upLevel=True)

	#roughness
	cmds.frameLayout(label="Specular Roughness", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )
	cmds.floatSliderGrp('floatSliderGrp_specRoughness', label='Roughness', field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=0.2, step=0.001 )
	cmds.button('button_getFromSelection_specRoughness', label='Get From Selection', command=partial(getFromSelection, 'specRoughness'))
	cmds.button('button_applyToSelection_specRoughness', label='Apply To Selection', height=50, command=partial(applyToSelection, 'specRoughness'))
	cmds.button('button_removeOverrides_specRoughness', label='Remove Spec Roughness Overrides', command=partial(removeFromSelection, 'specRoughness'))
	cmds.separator( height=5, style='none' )

	cmds.setParent(upLevel=True)

	cmds.separator( height=20, style='double' )

	cmds.button('button_close', label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
