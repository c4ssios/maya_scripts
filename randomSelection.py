import maya.cmds as cmds
import random


__title__ = "Random Choice From Selection"
__version__ = '0.1'
__author__ = "Nicolas Leblanc"
__company__ = ""
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"


def randomChoiceSelection(*args):

	sel = cmds.ls(sl=True, fl=True, l=True)
	percentage = cmds.floatField('percentage_floatField', q=True, value=True)

	if len(sel)==0:
		cmds.warning('Nothing is selected.')

	if len(sel)==1:
		cmds.warning('You must select more than one thing.')

	if len(sel)>1:

		newSel = random.sample(sel, int(len(sel)*percentage/100))
		cmds.select(newSel, r=True)



def randomSelectionUI():

	windowWidth = 250
	windowHeight = 100

	# Window Creation

	if (cmds.window("randomSelection_window", exists=True)):
		cmds.deleteUI("randomSelection_window")

	window = cmds.window("randomSelection_window", title= __title__+ ' ' +__version__, iconName='randomSelection', width=windowWidth, height=windowHeight)

	cmds.columnLayout( adjustableColumn=True )


	cmds.separator( height=5, style='none')
	cmds.text(label='Set Percentage ')
	cmds.separator( height=5, style='double')
	cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 50), (2, 150)] )
	cmds.floatField('percentage_floatField', minValue=0, maxValue=100, value=50, width=50)
	cmds.text(label="% of current selection.")
	cmds.setParent(upLevel=True)


	cmds.separator( height=5, style='none' )
	cmds.button(label='Select', height=50, command=randomChoiceSelection)

	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
