import maya.cmds as cmds
import maya.mel as mel
from functools import partial


__title__ = "PRman Lights Tweaker"
__version__ = '0.1'
__author__ = "Nicolas Leblanc"
__company__ = "Nicolas Leblanc"
__maintainer__ = "Nicolas Leblanc"
__email__ = "nicolas.leblanc@dwarfanimation.com"


attributeList = [
['floatSliderGrp', 'intensity'],
['floatSliderGrp', 'exposure'],
['colorSliderGrp', 'lightColor'],
['checkBox', 'enableTemperature'],
['floatSliderGrp', 'temperature'],
['checkBox', 'primaryVisibility'],
['floatSliderGrp', 'specular'],
['floatSliderGrp', 'diffuse'],
['floatSliderGrp', 'intensityNearDist'],
['checkBox', 'areaNormalize'],
['checkBox', 'visibleInRefractionPath'],
['intSliderGrp', 'fixedSampleCount']
]

pxrLightType = [
'PxrMeshLight',
'PxrRectLight',
'PxrDiskLight',
'PxrDistantLight',
'PxrSphereLight',
'PxrCylinderLight',
'PxrDomeLight',
]


def applyToSelection(*args):
	sel = cmds.ls(sl=True, l=True)
	if len(sel)<1:
		cmds.warning('Nothing is selected.')
	else:
		children = cmds.listRelatives(sel, c=True, fullPath=True)

		offenders = []

		for c in children:
			if cmds.objectType(c) not in pxrLightType:
				offenders.append(cmds.listRelatives(c, p=True)[0])

		if len(offenders)>0:
			for o in offenders:
				cmds.warning(o + ' is not a Pixar Light.')

		else:
			for c in children:
				for attr in attributeList:
					checkEnableCommand = 'cmds.' + attr[0] + '(' +"'" +attr[0] + '_' + attr[1] +"'"+ ', q=True, en=True)'

					if eval(checkEnableCommand)==1:

						if attr[1]=='lightColor':
							getValueCommand = 'cmds.' + attr[0] + '(' +"'" +attr[0] + '_' + attr[1] +"'"+ ', q=True, rgb=True)'
							cmds.setAttr(c+'.'+attr[1], eval(getValueCommand)[0], eval(getValueCommand)[1], eval(getValueCommand)[2], type="double3")

						else:
							getValueCommand = 'cmds.' + attr[0] + '(' +"'" +attr[0] + '_' + attr[1] +"'"+ ', q=True, v=True)'

							if cmds.attributeQuery(attr[1], node=c, exists=True):
								cmds.setAttr(c+'.'+attr[1], eval(getValueCommand))
								#print eval(getValueCommand)




def getFromSelection(*args):

	sel = cmds.ls(sl=True, l=True)

	attrValuesList = []

	if len(sel)==0:
		cmds.warning('Nothing is selected.')
	if len(sel)>1:
		cmds.warning('Select only One Pixar Light.')

	if len(sel)==1:

		child = cmds.listRelatives(sel[0], c=True, fullPath=True)[0]

		if cmds.objectType(child) not in pxrLightType:
			cmds.warning("No Pixar Light Selected.")

		else:

			for attr in attributeList:

				if cmds.attributeQuery(attr[1], node=child, exists=True):

					param = [attr[0], attr[1], cmds.getAttr(child+'.'+attr[1])]

					command = ''

					if param[1]=='lightColor':
						command ='cmds.' + param[0] + '(' +"'" +param[0] + '_' + param[1] +"'"+ ', edit=True, rgb=' + str(param[2][0])+')'

					else:
						command ='cmds.' + param[0] + '(' +"'" +param[0] + '_' + param[1] +"'"+ ', edit=True, v=' + str(param[2])+')'

					exec(command)




def toggleTemperatureColorUI(value, *args):
	cmds.floatSliderGrp('floatSliderGrp_temperature', e=True, m=value)
	cmds.checkBox('checkBox_toggle_temperature', e=True, m=value)
	cmds.rowColumnLayout('rowColumnLayout_temperature', edit=True, m=value)



def toggleUIelement(UItype, name, value, *args):
	command ='cmds.' + UItype + '(' +"'" + name +"'"+ ', edit=True, en=' + str(value)+')'
	exec(command)


def prmanLightsTweakerUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowWidth = 450
	windowHeight = 500
	frameLayoutMargin = 10
	firstColumnWidth = 100

	#Color
	frame_bgc = [0.18, 0.18, 0.18]


	# Window Creation

	if (cmds.window("prmanLightsTweaker_window", exists=True)):
		cmds.deleteUI("prmanLightsTweaker_window")

	window = cmds.window("prmanLightsTweaker_window", title= __title__+ ' ' +__version__, iconName='PRMAN Lights Tweaker', width=windowWidth, height=windowHeight, sizeable=False)

	cmds.columnLayout( adjustableColumn=True )

	#basic
	cmds.frameLayout(label="Basic", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)

	cmds.separator( height=5, style='none' )


	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])

	cmds.checkBox('checkBox_toggle_intensity', v=1, l="", onc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_intensity", 1), ofc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_intensity", 0))
	cmds.floatSliderGrp('floatSliderGrp_intensity', label='Intensity', field=True, minValue=0, maxValue=10, fieldMinValue=0, fieldMaxValue=100, value=1, step=0.001, cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.checkBox('checkBox_toggle_exposure', v=1, l="", onc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_exposure", 1), ofc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_exposure", 0))
	cmds.floatSliderGrp('floatSliderGrp_exposure', label='Exposure', field=True, minValue=-10, maxValue=10, fieldMinValue=-100, fieldMaxValue=100, value=0, step=0.001, cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.checkBox('checkBox_toggle_lightColor', v=1, l="", onc=partial(toggleUIelement, 'colorSliderGrp', "colorSliderGrp_lightColor", 1), ofc=partial(toggleUIelement, 'colorSliderGrp', "colorSliderGrp_lightColor", 0))
	cmds.colorSliderGrp('colorSliderGrp_lightColor', label='Color', rgb=(1, 1, 1), cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.setParent(upLevel=True)


	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])

	cmds.checkBox('checkBox_toggle_enableTemperature', v=1, l="", onc=partial(toggleUIelement, 'checkBox', "checkBox_enableTemperature", 1), ofc=partial(toggleUIelement, 'checkBox', "checkBox_enableTemperature", 0))
	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[1, firstColumnWidth])
	cmds.text('')
	cmds.checkBox('checkBox_enableTemperature', l="Enable Temperature", v=0, onc=partial(toggleTemperatureColorUI, 1), ofc=partial(toggleTemperatureColorUI, 0))

	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)


	cmds.rowColumnLayout('rowColumnLayout_temperature', numberOfColumns=2, columnWidth=[(1,20), (2, 430)], m=0)
	cmds.checkBox('checkBox_toggle_temperature', v=1, l="", onc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_temperature", 1), ofc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_temperature", 0), m=0)
	cmds.floatSliderGrp('floatSliderGrp_temperature', label='Temperature', field=True, minValue=1000, maxValue=50000, fieldMinValue=1000, fieldMaxValue=50000, value=6500, step=0.1, cal=[1, "right"], cw=[1, firstColumnWidth], m=False )
	cmds.setParent(upLevel=True)

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])
	cmds.checkBox('checkBox_toggle_primaryVisibility', v=1, l="", onc=partial(toggleUIelement, 'checkBox', "checkBox_primaryVisibility", 1), ofc=partial(toggleUIelement, 'checkBox', "checkBox_primaryVisibility", 0))
	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[1, firstColumnWidth])
	cmds.text('')
	cmds.checkBox('checkBox_primaryVisibility', l="Primary Visibility", v=0)

	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)

	cmds.setParent(upLevel=True)


	#refine
	cmds.frameLayout(label="Refine", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])
	cmds.checkBox('checkBox_toggle_specular', v=1, l="", onc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_specular", 1), ofc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_specular", 0))
	cmds.floatSliderGrp('floatSliderGrp_specular', label='Specular Amount', field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=1, step=0.001, cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.checkBox('checkBox_toggle_diffuse', v=1, l="", onc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_diffuse", 1), ofc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_diffuse", 0))
	cmds.floatSliderGrp('floatSliderGrp_diffuse', label='Diffuse Amount', field=True, minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=1, value=1, step=0.001, cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.checkBox('checkBox_toggle_intensityNearDist', v=1, l="", onc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_intensityNearDist", 1), ofc=partial(toggleUIelement, 'floatSliderGrp', "floatSliderGrp_intensityNearDist", 0))
	cmds.floatSliderGrp('floatSliderGrp_intensityNearDist', label='Intensity Near Dist', field=True, minValue=0, maxValue=0, fieldMinValue=0, fieldMaxValue=1, value=0, step=0.001, cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)

	#advanced
	cmds.frameLayout(label="Advanced", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])
	cmds.checkBox('checkBox_toggle_areaNormalize', v=1, l="", onc=partial(toggleUIelement, 'checkBox', "checkBox_areaNormalize", 1), ofc=partial(toggleUIelement, 'checkBox', "checkBox_areaNormalize", 0))

	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[1, firstColumnWidth])
	cmds.text('')
	cmds.checkBox('checkBox_areaNormalize', l="Normalize", v=0)

	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])
	cmds.checkBox('checkBox_toggle_visibleInRefractionPath', v=1, l="", onc=partial(toggleUIelement, 'checkBox', "checkBox_visibleInRefractionPath", 1), ofc=partial(toggleUIelement, 'checkBox', "checkBox_visibleInRefractionPath", 0))
	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[1, firstColumnWidth])
	cmds.text('')
	cmds.checkBox('checkBox_visibleInRefractionPath', l="Visible In Refraction", v=1)

	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)

	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,20), (2, 430)])
	cmds.checkBox('checkBox_toggle_fixedSampleCount', v=1, l="", onc=partial(toggleUIelement, 'intSliderGrp', "intSliderGrp_fixedSampleCount", 1), ofc=partial(toggleUIelement, 'intSliderGrp', "intSliderGrp_fixedSampleCount", 0))
	cmds.intSliderGrp('intSliderGrp_fixedSampleCount', label='Light Samples', field=True, minValue=0, maxValue=64, fieldMinValue=0, fieldMaxValue=64, value=0,  cal=[1, "right"], cw=[1, firstColumnWidth] )

	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)


	cmds.separator( height=20, style='double' )

	cmds.button(label='Get From Selection', command=getFromSelection)
	cmds.separator( height=5, style='none' )
	cmds.button(label='Apply To Selection', height=50, command=applyToSelection)


	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
