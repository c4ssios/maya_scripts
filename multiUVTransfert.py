import maya.cmds as cmds

__title__ = "Multi UVs Transfert"
__version__ = '1.0'
__author__ = "Nicolas Leblanc"
__company__ = "Home"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"



windowWidth = 300
windowHeight = 300

def pickSourceObject(*args):

	sourceObject = cmds.ls(sl=True, l=True)

	if len(sourceObject)==0:
		cmds.warning('Nothing is selected.')

	elif len(sourceObject)>1:
		cmds.warning('Select only ONE object as a source.')

	else:

		sourceMesh = cmds.listRelatives(sourceObject[0], path=True, fullPath=True, type='mesh')

		if sourceMesh is None:
			cmds.warning('Source Object must be a Polygonal Object.')

		else:
			cmds.textField('sourceObject_textField', edit=True, text=sourceObject[0])

	

def UVsTransfert(*args):

	sourceObject = str(cmds.textField('sourceObject_textField', q=True, text=True))

	targetObjects = cmds.ls(sl=True, l=True)

	if len(sourceObject)==0:
		cmds.warning('Nothing is defined as a source.')

	elif len(targetObjects)==0:
		cmds.warning('Nothing is selected.')

	elif sourceObject in targetObjects:

		cmds.warning('The source object cant be in the target objects list.')

	else:

		if len(cmds.listRelatives(targetObjects, path=True, fullPath=True, type='mesh'))==0:
			cmds.warning('Select only Polygonal objects as target.')

		else:

			transfertMode = int()
			UVsets = int()

			if cmds.radioCollection('transfertMode_radioCollection', q=True, sl=True)=='componentMode_radioButton':
				transfertMode = 4
			else:
				transfertMode = 5

			if cmds.radioCollection('transfertUV_radioCollection', q=True, sl=True)=='currentUVset_radioButton':
				UVsets = 1
			else:
				UVsets = 2

			for t in targetObjects:

				cmds.transferAttributes(sourceObject, t, transferUVs=UVsets, sampleSpace=transfertMode, searchMethod=3)
				cmds.delete(t, ch=True)

			print ('UVs transfered on ' + str(len(targetObjects)) +  ' object(s) succesfully.')




def multiUVTransfertUI():

	if (cmds.window("multiUVsTransfert_window", exists=True)):
		cmds.deleteUI("multiUVsTransfert_window")

	window = cmds.window("multiUVsTransfert_window", title= __title__+ ' ' +__version__, iconName='multiUVsTransfert', width=windowWidth, height=windowHeight)

	cmds.columnLayout( adjustableColumn=True )
	cmds.separator( height=5, style='none')
	cmds.text(label='Choose one source object and hit Pick Source button.\n Choose target object(s) and hit\nTransfert UVs button.\n')

	cmds.frameLayout('sourceObject_framelayout', borderVisible=False, lv=0)
	cmds.rowLayout(numberOfColumns=2, columnWidth=[(1, 40), (2, 250)])
	cmds.button('sourceObject_button', width=70, height=25, label='Pick Source', command=pickSourceObject)
	cmds.textField('sourceObject_textField', width=250, ed=False)
	cmds.setParent(upLevel=True)

	cmds.frameLayout('transfertUV_frameLayout', borderVisible=False, lv=0)
	cmds.separator( height=2, style='none')
	cmds.text(label='UV Sets', align='left')
	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 120), (2, 120)])
	cmds.radioCollection('transfertUV_radioCollection')
	cmds.radioButton('currentUVset_radioButton', label='Current')
	cmds.radioButton('allUVsets_radioButton', label='All')
	cmds.setParent(upLevel=True)

	cmds.separator( height=5, style='double')

	cmds.frameLayout('transfertMode_frameLayout', borderVisible=False, lv=0)
	cmds.text(label='Sample Space', align='left')
	cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 120), (2, 120)])
	cmds.radioCollection('transfertMode_radioCollection')
	cmds.radioButton('componentMode_radioButton', label='Components')
	cmds.radioButton('topologyMode_radioButton', label='Topology')
	cmds.separator( height=5, style='none')
	cmds.setParent(upLevel=True)

	cmds.radioCollection('transfertUV_radioCollection', edit=True, sl='currentUVset_radioButton')
	cmds.radioCollection('transfertMode_radioCollection', edit=True, sl='componentMode_radioButton')

	cmds.separator( height=5, style='double')

	cmds.frameLayout('execute_frameLayout', borderVisible=False, lv=0)
	cmds.button('execute_button', height=40, label='Transferts UVs', command=UVsTransfert)
	cmds.setParent(upLevel=True)

	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
