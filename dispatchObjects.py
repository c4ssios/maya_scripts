import maya.cmds as cmds
import math


def dispatchObjects():
	
	sel = cmds.ls(sl=True, l=True)

	Xvalues = []
	Zvalues = []

	if len(sel)<=1:
		cmds.warning('Select at least 2 objects')

	else:
		for s in sel:
			cmds.xform(s, a=True, t=(0,0,0))
			bbox = cmds.exactWorldBoundingBox(s)

			Xvalues.append(abs(bbox[0]) + abs(bbox[3]))
			Zvalues.append(abs(bbox[2]) + abs(bbox[5]))

	columnIndex = int(math.sqrt(len(sel))) +1

	print columnIndex

	moveValueX = max(Xvalues)*1.1
	moveValueZ = max(Zvalues)*1.1

	for s in sel:

		index = sel.index(s)
		rowIndex = int(index/ columnIndex)

		cmds.xform(s, a=True, t=(index*moveValueX, 0, rowIndex*moveValueZ))
		cmds.xform(s, r=True, t=(-(rowIndex*moveValueX*columnIndex), 0, 0))

