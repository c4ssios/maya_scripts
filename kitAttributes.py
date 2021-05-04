import maya.cmds as cmds
from functools import partial


__title__ = "Kit Attribute"
__version__ = '0.13'
__author__ = "Nicolas Leblanc"
__company__ = "Me"
__maintainer__ = "Nicolas Leblanc"
__email__ = "c4ssios@gmail.com"


def checkSelection():
	sel = cmds.ls(sl=True, l=True)

	validSelection = []

	if len(sel)==0:
		cmds.warning("Nothing is selected.")

	else:
		if cmds.listRelatives(sel, typ="mesh", c=True, f=True) is None:
			cmds.warning("No mesh selected.")

		else:
			validSelection=sel

	return validSelection

#------------------------------
#Create Attributes def
#------------------------------

def addGeoId(*args):
	sel = checkSelection()

	if sel:

		idList = [0]
		meshWithNoIdList = []

		meshTransformList = cmds.listRelatives(cmds.ls(typ="mesh", l=True), p=True, f=True)

		for m in meshTransformList:
			if cmds.attributeQuery("geoId",node=m, exists=True):
				idList.append(cmds.getAttr(m+".geoId"))


		highestId = max(idList)


		for s in sel:
			geoIdValue = highestId + sel.index(s)+1

			if cmds.attributeQuery("geoId",node=s, exists=True):
				pass

			else:	
				cmds.addAttr(s, longName="geoId", defaultValue=geoIdValue, attributeType="long")

				
	else:
		pass


def addLibraryId(*args):
	sel = checkSelection()

	libraryIdValue = cmds.intField("libraryId_intField", v=True, q=True)

	for s in sel:
		if cmds.attributeQuery("libraryId",node=s, exists=True)==0:
			cmds.addAttr(s, longName="libraryId", defaultValue=libraryIdValue, attributeType="long")
		else:
			cmds.setAttr(s+".libraryId",  libraryIdValue)


def setGeoId(*args):
	sel = checkSelection()

	customGeoIdValue = cmds.intField("geoId_intField", v=True, q=True)

	for s in sel:
		if cmds.attributeQuery("geoId",node=s, exists=True)==0:
			cmds.addAttr(s, longName="geoId", defaultValue=customGeoIdValue, attributeType="long")
		else:
			cmds.setAttr(s+".geoId",  customGeoIdValue)


def setVariantId(*args):
	sel = checkSelection()

	variantIdValue = cmds.intField("variantId_intField", v=True, q=True)

	for s in sel:
		if cmds.attributeQuery("variantId",node=s, exists=True)==0:
			cmds.addAttr(s, longName="variantId", defaultValue=variantIdValue, attributeType="long")
		else:
			cmds.setAttr(s+".geoId",  variantIdValue)


#-----------------------------
#Select by Id def
#-----------------------------

def getAttrFromSelection(*args):
	sel = checkSelection()

	if len(sel)>1:
		cmds.warning("Select Only 1 object.")

	elif len(sel)==1:
		s=sel[0]

		if cmds.attributeQuery("geoId",node=s, exists=True)==0:
			cmds.warning("geoId attribute is missing on selected object.")

		if cmds.attributeQuery("libraryId",node=s, exists=True)==0:
			cmds.warning("libraryId attribute is missing on selected object.")

		if cmds.attributeQuery("geoId",node=s, exists=True) and cmds.attributeQuery("libraryId",node=s, exists=True):
			geoIdValueOnSelected = cmds.getAttr(s + ".geoId")
			libraryIdValueOnSelected = cmds.getAttr(s + ".libraryId")

			cmds.intField("selectByAttrGeoId_intField", v=geoIdValueOnSelected, e=True)
			cmds.intField("selectByAttrLibraryId_intField", v=libraryIdValueOnSelected, e=True)


def selectByGeoIdLibId(*args):

	geoIdValueFromUI = cmds.intField("selectByAttrGeoId_intField", v=True, q=True)
	libraryIdValueFromUI = cmds.intField("selectByAttrLibraryId_intField", v=True, q=True)

	listAllMeshTransform = cmds.listRelatives(cmds.ls(typ="mesh", l=True), p=True, typ="transform", f=True)

	matchingList = []

	for m in listAllMeshTransform:

		if cmds.attributeQuery("geoId", node=m, exists=True) and cmds.attributeQuery("libraryId", node=m, exists=True):

			currentGeoId = cmds.getAttr(m+".geoId")
			currentLibraryId = cmds.getAttr(m+".libraryId")

			if currentGeoId==geoIdValueFromUI and currentLibraryId==libraryIdValueFromUI:
				matchingList.append(m)

	if len(matchingList)>0:
		cmds.select(matchingList, r=True)

	else:
		cmds.warning("No matching geometry.")


def selectByGeoId():
	pass

def selectByLibraryId():
	pass


#------------------------------
#Remove Attributes def
#------------------------------

def removeIdAttr(attr, *args):
	sel = checkSelection()

	for s in sel:
		if cmds.attributeQuery(attr, node=s, exists=True):
			cmds.deleteAttr(s, at=attr)



#----------------------------
# UI
#----------------------------
def kitAttributesUI():
	'''
	Create UI Window
	'''
	# Size Parameters

	windowWidth = 300
	windowHeight = 720
	buttonWidth1 = 200
	intFielddWidth1 = 100
	intFielddWidth2 = 150
	intFielddWidth3 = 50


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


	# Window Creation

	if (cmds.window("kitAttribute_window", exists=True)):
		cmds.deleteUI("kitAttribute_window")

	window = cmds.window("kitAttribute_window", title= __title__+ ' ' +__version__, iconName='kitAttribute', width=windowWidth, height=windowHeight, sizeable=False)

	cmds.columnLayout( adjustableColumn=True )

#----------------------------------------------------------------
	cmds.frameLayout(label="Create Attributes", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.button("createGeoId_button", label="Add Geo ID", command=addGeoId)

	cmds.separator( height=10, style='none' )
	cmds.setParent(upLevel=True)

#----------------------------------------------------------------
	cmds.frameLayout(label="Customize Attributes", collapsable=True, collapse=True, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.rowLayout(numberOfColumns=2)
	cmds.button("setGeoId_button", label="Set Geo ID", w=buttonWidth1, command=setGeoId )
	cmds.intField('geoId_intField', minValue=1, maxValue=999, value=123 , step=1, w=intFielddWidth1)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=2)
	cmds.button("createLibraryId_button", label="Add Library ID", w=buttonWidth1, command=addLibraryId)
	cmds.intField('libraryId_intField', minValue=1, maxValue=999999, value=12345 , step=1, w=intFielddWidth1)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=2)
	cmds.button("createVariantId_button",  w=buttonWidth1, label="Add/Set Variant ID", command=setVariantId)
	cmds.intField('variantId_intField', minValue=1, maxValue=999, value=1 , step=1, w=intFielddWidth1)
	cmds.setParent(upLevel=True)

	cmds.separator( height=10, style='double' )

	cmds.rowLayout(numberOfColumns=3)
	cmds.button("randomizeVariantId_button",  w=buttonWidth1, label="Randomize Variant ID")
	cmds.intField('randomVariantIdMin_intField', minValue=1, maxValue=999, value=1 , step=1, w=intFielddWidth3)
	cmds.intField('randomVariantIdMax_intField', minValue=1, maxValue=999, value=9 , step=1, w=intFielddWidth3)
	cmds.setParent(upLevel=True)

	cmds.separator( height=10, style='none' )
	cmds.setParent(upLevel=True)

#----------------------------------------------------------------
	cmds.frameLayout(label="Remove Attributes", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.button("removeGeoId_button", label="Remove Geo ID", command=partial(removeIdAttr, 'geoId'))
	cmds.button("removeLibraryId_button", label="Remove Library ID", command=partial(removeIdAttr, 'libraryId'))
	cmds.button("removeVariantId_button", label="Remove Variant ID", command=partial(removeIdAttr, 'variantId'))

	cmds.separator(height=10, style='none')
	cmds.setParent(upLevel=True)

#----------------------------------------------------------------
	cmds.frameLayout(label="Select By Attributes", collapsable=True, collapse=False, marginWidth=frameLayoutMargin, bgc=frame_bgc)
	cmds.separator( height=5, style='none' )

	cmds.button("getAttrFromSelection_button", label="Get Attributes from Selection", command=getAttrFromSelection)

	cmds.rowLayout(numberOfColumns=2)
	cmds.text(label='Geo ID',  align='center', w=intFielddWidth2)
	cmds.text(label='Library ID',  align='center', w=intFielddWidth2)
	cmds.setParent(upLevel=True)

	cmds.rowLayout(numberOfColumns=2)
	cmds.intField('selectByAttrGeoId_intField', minValue=1, maxValue=999, value=123 , step=1, w=intFielddWidth2)
	cmds.intField('selectByAttrLibraryId_intField', minValue=1, maxValue=999999, value=12345 , step=1, w=intFielddWidth2)
	cmds.setParent(upLevel=True)

	cmds.separator( height=10, style='double' )

	cmds.button("selectByGeoIdLibId_button", label="Select by Geo ID and Library ID", command=selectByGeoIdLibId)
	cmds.button("selectByGeoId_button", label="Select by Geo ID")
	cmds.button("selectByLibId_button", label="Select by Library ID")

	cmds.separator(height=10, style='none')
	cmds.setParent(upLevel=True)
#----------------------------------------------------------------


	'''
	Close Button
	'''
	cmds.separator( height=10, style='double' )

	cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

	cmds.setParent(upLevel=True)
	cmds.window(window, e=True, width=windowWidth, height=windowHeight)
	cmds.showWindow( window )