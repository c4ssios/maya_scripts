#!/usr/bin/env python
#title           :FSrenamer.py
#description     :Renamer tool for modelling department using Framestore naming convention.
#date            :20161018
#==============================================================================


import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import mod_default_modules as mods
import math
import time


__title__ = "FS Renamer"
__version__ = '0.71'
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



