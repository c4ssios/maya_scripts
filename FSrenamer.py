#!/usr/bin/env python
#title           :FSrenamer.py
#description     :Renamer tool for modelling department using Framestore naming convention.
#date            :20200819
#==============================================================================


import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import math
import time


__title__ = "FS Renamer"
__version__ = '1.0'
__author__ = "Nicolas Leblanc"
__company__ = "Framestore"
__maintainer__ = "Nicolas Leblanc"
__email__ = "nicolas.leblanc@framestore.com"



def renameSelection(*args):
	'''
	Renaming definition
	'''

	materialInput = cmds.optionMenu('materialMenu', query=True, value=True)
	colorInput = cmds.optionMenu('colorMenu', query=True, value=True)
	positionInput = cmds.optionMenu('positionMenu', query=True, value=True)
	nameInput = cmds.textField('nameField', query=True, text=True)
	paddingInput = cmds.intField('paddingField', query=True, value=True)
	extensionInput = cmds.optionMenu('extensionMenu', query=True, value=True)

	if len(nameInput)==0:

		cmds.warning('Name field cannot be empty.')

	else:

		sel = cmds.ls(selection=True, l=True)
		numInSel = len(sel)


		if numInSel==0:
			cmds.warning('Nothing is selected.')

		else:

			sel.reverse()

			digits = int(math.log10(numInSel))+1

			if digits > paddingInput:
				paddingInput = digits


			renameProgressBar(numInSel)

			startTime = time.time()

			for s in sel:

				splitName = s.split('|')
				objectName = splitName[len(splitName)-1]
				hierarchyName = s[:-(len(objectName))]
				nameSpace = ''

				if cmds.checkBox('keepNamespace_checkbox', query=True, value=1):
					if ':' in objectName:
						namespaceSplit = objectName.split(':') 
						nameSpace = objectName[:-(len(namespaceSplit[len(namespaceSplit)-1]))]
					else:
						pass


				startingNumber = cmds.intField('paddingStartField', value=True, query=True)
				numIndex = len(sel)-1-sel.index(s)+startingNumber
				paddingFinal = ('%0'+ str(paddingInput) +'d') % numIndex

				if cmds.radioCollection('numbersOrLetters_radioCollection', select=True, q=True)=='letters_radioButton':

					paddingFinal = convertToLetter(int(paddingFinal))

				if cmds.checkBox('groupNaming_checkbox', query=True, value=1):

					name = nameSpace + nameInput + paddingFinal + '_' + extensionInput

				else:

					name = nameSpace + materialInput + colorInput + '_' + positionInput + '_' + nameInput + paddingFinal + '_' + extensionInput

				cmds.rename(hierarchyName + '|' + objectName, name)

				cmds.progressBar('renameProgress_progressBar', edit=True, step=1)

			cmds.deleteUI('progressBar_window')

			endTime = time.time()


			displayResult(numInSel, startTime, endTime)


def listNamespaces():
	'''
	List All namespaces in the scene
	'''
	cmds.namespace(setNamespace=':')
	namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True, r=True)
	for d in ('UI', 'shared'):
	    if d in namespaces:
	        namespaces.remove(d)

	return namespaces


def removeSelectedNamespaces(*args):

	selectedNamespaces = cmds.textScrollList( "namespaces_list", query=True, selectItem=True)

	for n in selectedNamespaces:
		cmds.namespace(mergeNamespaceWithRoot=True, removeNamespace=n)
		print 'Namespace ' + n + ' removed.'

	cmds.textScrollList("namespaces_list",edit=True, removeAll=True)
	displayNamespacesList()


	if cmds.window( 'namespaceEditor' ,exists=True):
		mel.eval('updateNamespaceEditor;')



def removeAllNamespaces(*args):
	'''
	Remove All namespaces in the scene
	'''

	cmds.namespace(setNamespace=':')
	namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True, r=True)
	while len(namespaces)>2:
	    namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True, r=True)
	    for d in ('UI', 'shared'):
	        if d in namespaces:
	            namespaces.remove(d)
	    for n in namespaces:
	    	if cmds.namespace(exists=n):
	    		cmds.namespace(mergeNamespaceWithRoot=True, removeNamespace=n)
	    		print 'Namespace ' + n + ' removed.'
	    	else:
	    		namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True, r=True)

	cmds.textScrollList("namespaces_list",edit=True, removeAll=True)
	displayNamespacesList()

	if cmds.window( 'namespaceEditor' ,exists=True):
		mel.eval('updateNamespaceEditor;')



def convertToLetter(value):
	'''
	Convert a integer to string with letters
	'''
	bufferValue = value
	tmpList = []
	while bufferValue > 26:
		if bufferValue%26==0:
			tmpList.append('Z')
		else:
			tmpList.append(chr((bufferValue%26)+64))
		bufferValue = (bufferValue-1)//26

	tmpList.append(chr((bufferValue)+64))

	tmpList.reverse()

	letters = ''.join(tmpList)
	
	return letters

def addPrefixSuffix(value, *args):

	prefix = cmds.textField('addPrefix_textField', query=True, text=True)
	suffix = cmds.textField('addSuffix_textField', query=True, text=True)

	sel = cmds.ls(selection=True, l=True)

	if len(sel)==0:
		cmds.warning('Nothing is selected.')

	else:

		sel.sort()
		sel.reverse()

		startTime = time.time()

		for s in sel:
			splitName = s.split('|')
			objectName = splitName[len(splitName)-1]
			hierarchyName = s[:-(len(objectName))]
			nameSpace = ''
			name = 'name'

			if cmds.checkBox('keepNamespacePrefix_checkbox', query=True, value=1):
				if ':' in objectName:
					namespaceSplit = objectName.split(':') 
					nameSpace = objectName[:-(len(namespaceSplit[len(namespaceSplit)-1]))]
				else:
					pass

			if value == 'prefix':
				if len(prefix)==0:
					cmds.warning('Prefix field cannot be empty.')
				else:
					name = nameSpace + prefix + objectName

			if value == 'suffix':
				if len(suffix)==0:
					cmds.warning('Suffix field cannot be empty.')
				else:
					name = nameSpace + objectName + suffix

			cmds.rename(hierarchyName + '|' + objectName, name)

		endTime = time.time()

		displayResult(len(sel), startTime, endTime)

		
def searchAndReplace(*args):
	'''
	Triggering Maya's search and replace function
	'''

	searchFor = cmds.textField('searchFor_textField', query=True, text=True)
	replaceWith = cmds.textField('replaceWith_textField', query=True, text=True)
	searchMethod = cmds.radioCollection('searchAndReplaceOptions_radioCollection', query=True, select=True).replace('_radioButton','')


	if len(searchFor)==0:
		cmds.warning('Fields cannot be empty.')

	else:

		objectListToRename = ''

		if searchMethod=='selected':
			objectListToRename = cmds.ls(sl=True, l=True)

		elif searchMethod=='hierarchy':
			objectListToRename = cmds.ls(sl=True, l=True, dag=True)

		elif searchMethod=='all':
			objectListToRename = cmds.ls(l=True)

		if len(objectListToRename)>0:

			errorObjects = []

			objectListToRename.sort()
			objectListToRename.reverse()

			renamedObjects = 0

			startTime = time.time()

			for o in objectListToRename:

				splitName = o.split('|')
				objectName = splitName[len(splitName)-1]
				hierarchyName = o[:-(len(objectName))]

				if searchFor in objectName:
					newName = objectName.replace(searchFor, replaceWith)

					if len(newName)==0:
						errorObjects.append(hierarchyName+'|'+objectName)
					else:
						cmds.rename(hierarchyName+'|'+objectName, newName)
						renamedObjects+=1

			endTime = time.time()

			if len(errorObjects)>0:
				cmds.warning('Some objects could not be renamed, resulting of an empty name.')
			else:
				displayResult(renamedObjects, startTime, endTime)

		else:
			cmds.warning('Nothing to rename.')


def displayResult(num, start, end):

	outputMessage = str(num) + ' objects renamed in ' + str(end-start) + ' sec.'
	mel.eval('print `format ("%s")`' % outputMessage)



'''
UI functions definitions
'''

def enableGroupRename(*args):
	'''
	Enable group renaming layout in the UI
	'''

	cmds.optionMenu('materialMenu', edit=True, enable=False)
	cmds.optionMenu('colorMenu', edit=True, enable=False)
	cmds.optionMenu('positionMenu', edit=True, enable=False)
	cmds.optionMenu('extensionMenu', edit=True, value='GRP')
	

def disableGroupRename(*args):
	'''
	Disable group renaming layout in the UI
	'''
	
	cmds.optionMenu('materialMenu', edit=True, enable=True)
	cmds.optionMenu('colorMenu', edit=True, enable=True)
	cmds.optionMenu('positionMenu', edit=True, enable=True)
	cmds.optionMenu('extensionMenu', edit=True, value='GEP')


def toggleNumberOfDigits(*args):
	'''
	Toggle padding field
	'''

	paddingFieldStatus = cmds.intField('paddingField', query=True, enable=True)
	cmds.intField('paddingField', edit=True, en=not paddingFieldStatus)


def renameProgressBar(numberOfObj):

	progressBarWindow = cmds.window('progressBar_window', title='FS Renamer Progression')
	cmds.columnLayout()
	cmds.progressBar('renameProgress_progressBar',minValue=0, maxValue=numberOfObj, width=300, height=40)
	cmds.showWindow(progressBarWindow)


def displayNamespacesList():
	namespaces = listNamespaces()
	for name in namespaces:
		cmds.textScrollList('namespaces_list', edit=True, append=name)
	
	
def FSrenamerUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowWidth = 540
	windowHeight = 300
	paddingFrameSize = 116
	materialSize = 80
	colorSize = 80
	positionSize = 50
	nameSize = 200
	paddingSize = 50
	extensionSize =50
	spacingSize = 7
	searchSize = 80
	searchInputSize = 300
	prefixSize = 80
	prefixInputSize = 150
	frameLayoutMargin = 10
	namespaceButtonSize = 200

	#Color
	frame_bgc = [0.18, 0.18, 0.18]

	
	# Parameters Lists

	materialList = ['stone','paint','metal','wood','plastic','rubber','cloth','glass','ceramic','skin','hair','nail','bone','liquid','polysterene','leather','default','paper','hrsi','felt','lrsi','frsi','rcc','light','plant']
	materialList.sort()
	colorList = ['Grey','Black','White','Yellow','Red','Green','Blue','Orange','Purple','Brown','Pink','Colour','Light','Clear','Mixed']
	colorList.sort()
	positionList = ['C','R', 'L', 'F', 'B', 'FR','BR','FL','BL']
	extensionList = ['GEP','GES','GED','GEV','PLY','NRB','CRV','GRP','LOC']


	# Window Creation

	if (cmds.window("FSRenamer_window", exists=True)):
		cmds.deleteUI("FSRenamer_window")

	window = cmds.window("FSRenamer_window", title= __title__+ ' ' +__version__, iconName='FSRenamer', width=windowWidth, height=windowHeight)

	cmds.columnLayout( adjustableColumn=True )


	'''
	Search and Replace
	'''

	cmds.frameLayout(label="Search and Replace", collapsable=True, collapse=True, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Search For :', width=searchSize, align='right')
	cmds.textField('searchFor_textField', width=searchInputSize)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Replace with :', width=searchSize, align='right')
	cmds.textField('replaceWith_textField', width=searchInputSize)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=4)
	cmds.separator(width=searchSize, style=None)
	cmds.radioCollection('searchAndReplaceOptions_radioCollection')
	cmds.radioButton('hierarchy_radioButton' ,label='Hierarchy', sl=True)
	cmds.radioButton('selected_radioButton' ,label='Selected')
	cmds.radioButton('all_radioButton' ,label='All')
	cmds.setParent(upLevel=True)

	cmds.button('searchAndReplace_button', label='Replace', height=30, command=searchAndReplace)


	cmds.separator( height=10, style='none' )
	cmds.setParent(upLevel=True)
	

	'''
	Prefix and Suffix
	'''

	cmds.frameLayout(label="Prefix and Suffix", collapsable=True, collapse=True,  marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowLayout(numberOfColumns=3)
	cmds.text(label='Prefix :', width=prefixSize, align='center')
	cmds.textField('addPrefix_textField', width=prefixInputSize)
	cmds.button('addPrefix_button', width=prefixSize, label='Add Prefix', command=partial(addPrefixSuffix, 'prefix'))
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=3)
	cmds.text(label='Suffix :', width=prefixSize, align='center')
	cmds.textField('addSuffix_textField', width=prefixInputSize)
	cmds.button('addSuffix_button', width=prefixSize, label='Add Suffix', command=partial(addPrefixSuffix, 'suffix'))
	cmds.setParent(upLevel=True)

	cmds.checkBox('keepNamespacePrefix_checkbox', l='Keep Namespaces', v=0)

	cmds.separator( height=10, style='none' )
	cmds.setParent(upLevel=True)

	
	'''
	Namespaces Utilities
	'''

	cmds.frameLayout(label="Namespace Utilities", collapsable=True, collapse=True, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowLayout(numberOfColumns=2)

	cmds.columnLayout(rowSpacing=5)
	cmds.textScrollList('namespaces_list',allowMultiSelection=True, height=150, width=360)

	displayNamespacesList()

	cmds.setParent(upLevel=True)

	cmds.columnLayout(rowSpacing=5)
	cmds.button('removeSelectedNamespaces_button', label='Remove Selected Namespaces', width=namespaceButtonSize, command=removeSelectedNamespaces)
	cmds.button('removeAllNamespaces_button', label='Remove All Namespaces', width=namespaceButtonSize, command=removeAllNamespaces)
	cmds.setParent(upLevel=True)
	cmds.setParent(upLevel=True)

	
	cmds.separator( height=5, style='none' )
	cmds.setParent(upLevel=True)

	
	'''
	Lettering and numbering
	'''

	cmds.frameLayout(label="Padding", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowLayout(numberOfColumns=4)
	cmds.separator(width=paddingFrameSize*2, style='none' )
	cmds.text(label='Number of Digits', width=paddingFrameSize, align='center')
	cmds.text(label='Start Value (Offset)', width=paddingFrameSize, align='center')
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=4)
	cmds.radioCollection('numbersOrLetters_radioCollection')
	cmds.radioButton('numbers_radioButton' ,label='Numbers', width=paddingFrameSize, sl=True , onc=toggleNumberOfDigits)
	cmds.radioButton('letters_radioButton', label='Letters' , width=paddingFrameSize, onc=toggleNumberOfDigits)
	cmds.intField('paddingField', minValue=1, maxValue=10, value=4 , step=1, width=paddingFrameSize)
	cmds.intField('paddingStartField', minValue=1, step=1, value=1, width=paddingFrameSize)

	cmds.setParent(upLevel=True)
	cmds.separator( height=5, style='none' )
	cmds.setParent(upLevel=True)


	'''
	Renaming input fields
	'''

	cmds.frameLayout(label="Renaming Input Fields", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=10, style='none' )


	# Titles
	
	cmds.rowLayout(numberOfColumns=9)
	cmds.text(label="Material", align='center', width=materialSize)
	cmds.text(label="Color", align='center', width=colorSize)
	cmds.separator(style='none', width=spacingSize)
	cmds.text(label="Position", align='center', width=positionSize)
	cmds.separator(style='none', width=spacingSize)
	cmds.text(label="Name", align='center', width=nameSize)
	cmds.text(label="Padding", align='center', width=paddingSize)
	cmds.separator(style='none', width=spacingSize)
	cmds.text(label="Extension", align='center', width=extensionSize)
	cmds.setParent(upLevel=True)

		# Input fields

	cmds.rowLayout(numberOfColumns=9)

	cmds.optionMenu('materialMenu', width=materialSize)
	for m in materialList:
		cmds.menuItem( label=m )

	cmds.optionMenu('colorMenu', width=colorSize)
	for c in colorList:
		cmds.menuItem( label=c )

	cmds.text(label="_", align='center')

	cmds.optionMenu('positionMenu', width=positionSize)
	for p in positionList:
		cmds.menuItem( label=p )

	cmds.text(label="_", align='center')

	cmds.textField('nameField', width=nameSize)

	cmds.text(label="# # # #", align='center', width=paddingSize)

	cmds.text(label="_", align='center')

	cmds.optionMenu('extensionMenu', width=extensionSize)
	for e in extensionList:
		cmds.menuItem( label=e )



	cmds.setParent(upLevel=True)


	# Group Naming Template, Keep Namespace switch

	cmds.checkBox('keepNamespace_checkbox', l='Keep Namespaces', v=0)
	cmds.checkBox('groupNaming_checkbox', l='Group Naming Template', v=0, onc=enableGroupRename, ofc=disableGroupRename)

	cmds.separator( height=10, style='none' )
	cmds.setParent(upLevel=True)


	'''
	Buttons
	'''

	cmds.separator( height=10, style='none' )

	cmds.button( 'renameButton', label = 'Rename Selection', height=50, command=renameSelection )

	cmds.separator( height=20, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )
