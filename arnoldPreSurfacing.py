import maya.cmds as cmds
import random
import re


materialList = ['stone','paint','metal','wood','plastic','rubber','cloth','glass','ceramic','skin','hair','nail','bone','liquid','polysterene','leather','default','paper','felt','light', 'concrete', 'plant']
colorList = ['Grey','Black','White','Yellow','Red','Green','Blue','Orange','Purple','Brown','Pink','Colour','Clear','Mixed']


def randomRename():
	sel = cmds.ls(sl=True)
	for s in sel:
	    name = random.choice(materialList)+random.choice(colorList)+'_C_sphere' + ('%04d') % (sel.index(s)+1) + '_GEP'
	    cmds.rename(s, name)


def camelCaseSplit(string):
	splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', string)).split()
	return splitted


def filterSelection(selection):
	offenders = []
	for obj in selection:
		if '_' not in obj:
			offenders.append(obj)
		elif len(obj.split('_'))!=4:
			offenders.append(obj)
		elif len(camelCaseSplit(obj.split('_')[0]))!=2:
			offenders.append(obj)
		elif camelCaseSplit(obj.split('_')[0])[0] not in materialList:
			offenders.append(obj)
		elif camelCaseSplit(obj.split('_')[0])[1] not in colorList:
			offenders.append(obj)

	return offenders
