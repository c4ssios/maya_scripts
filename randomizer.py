# this is the Randomizer by Roland Reyer, (c) Autodesk GmbH 2008
#
# this is Version 1.0
# 20. June 2008

# Ideen>
# - World Space, Object Space (alle Optionen des Move Tools)
# - verts in UVN bewegen (nicht nur N)
# - dnoise Funktion mit Skalierung benutzen
# - Faces und Edges *direkt* bewegen, damit deeren Verts sich nicht gegeneinander verschieben

import maya.cmds as mc
import maya.mel as mm
import random

sel = []
selCmp = []
selChnl = []
win = ''

def standardWindow( windowName, title, buttons):
	# this proc creates a standard window with a columnLayout and some button below
	# if $windowName is empty, a new window will be created (otherwise the existing window is shown
	
	# it returns an array with:
	# - the UI name of the window
	# - the UI name of the columnLayout
	# - the names of the buttons
	
	# The window is NOT shown, so that the contents can be added before the window appears
	
    if len( buttons) == 0:
        mc.error( 'This window should have at least one button!')
    
    if windowName == '': windowName = mc.window( rtf=1, title=title)        # if no UI name is given then create a window
    elif mc.window( windowName, exists=1):
        mc.showWindow( windowName)
        return( windowName)
    else: mc.window( windowName, rtf=1, title=title)
    
    result = []
    result.append( windowName)
    
    form = mc.formLayout( nd=100)
    tab = mc.tabLayout( tv=0, scr=1)
    result.append( mc.columnLayout( adj=1))
    
    mc.setParent( form)
    sep = mc.separator( h=10)
    
    for b in buttons: result.append( mc.button( label=b))
    
    mc.formLayout( form, edit=1,
                   attachForm = [(tab, 'top', 10),
                                 (tab, 'left', 5),
                                 (tab, 'right', 5),
                                 (sep, 'left', 5),
                                 (sep, 'right', 5)],
                   attachControl = [(tab, 'bottom', 5, sep),
                                    (sep, 'bottom', 5, result[2])],
                   attachNone = [(sep, 'top')])

    mc.formLayout( form, edit=1,
                   attachForm = [(result[2], 'left', 5),
                                 (result[2], 'bottom', 5),
                                 (result[-1], 'right', 5),
                                 (result[-1], 'bottom', 5)],
                   attachNone = [(result[2], 'top'),
                                 (result[-1], 'top')])

    gapStep = 100 / len(buttons)
    for i in range( 3, len( result)):
        mc.formLayout( form, edit=1,
                    attachPosition = [(result[i-1], 'right', 2, gapStep*(i-2)),
                                      (result[i], 'left', 2, gapStep*(i-2))],
                    attachForm = [(result[i], 'bottom', 5)])

    return result


class RandomizerWindow( object):
    def __init__( self):
        self.cRange = []
        self.cOffset = []
        self.cStep = []
        window, columnLayout, closeButton, seedButton, selectButton, undoButton = standardWindow( "randomizerWin", "Randomizer", ( "Close", "New Seed", "Reload Sel", "Reset"))
        mc.setParent( columnLayout)
        mc.text( 'Select objects, channels, components\nand click on \"Reload Sel\"')
        mc.separator( style='none', h=10)


        mc.frameLayout( label='Objects', cll=1, cl=0)
        mc.columnLayout( adj=1)

        # Transform Objects
        self.tRange = mc.floatSliderGrp( label='Translate Range', fieldStep=.1, precision=3, field=True, min=0, fieldMinValue=0, max=50, fieldMaxValue=10000, cc='randomizer.updateTranslate(1)', dc='randomizer.updateTranslate(0)' )
        self.tScale = mc.floatFieldGrp( label='Scale Axis', precision=3, numberOfFields=3, value1=1, value2=1, value3=1, cc='randomizer.updateTranslate(1)', dc='randomizer.updateTranslate(0)' )
        for c in mc.layout( self.tScale, q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)
        mc.separator( style='in', h=20)

        # Rotate Objects
        self.rRange = mc.floatSliderGrp( label='Rotate Range', fieldStep=.1, precision=3, field=True, min=0, fieldMinValue=0, max=360, fieldMaxValue=10000, cc='randomizer.updateRotate(1)', dc='randomizer.updateRotate(0)' )
        self.rScale = mc.floatFieldGrp( label='Scale Axis', precision=3, numberOfFields=3, value1=1, value2=1, value3=1, cc='randomizer.updateRotate(1)', dc='randomizer.updateRotate(0)' )
        for c in mc.layout( self.rScale, q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)
        mc.separator( style='in', h=20)

        # Scale Objects
        self.sRange = mc.floatSliderGrp( label='Scale Range', fieldStep=.1, precision=3, field=True, min=0, fieldMinValue=0, max=5, fieldMaxValue=10000, cc='randomizer.updateScale(1)', dc='randomizer.updateScale(0)' )
        self.sScale = mc.floatFieldGrp( label='Scale Axis', precision=3, numberOfFields=3, value1=1, value2=1, value3=1, cc='randomizer.updateScale(1)', dc='randomizer.updateScale(0)' )
        for c in mc.layout( self.sScale, q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)
        self.uniformScale = mc.checkBoxGrp( label='Uniform Scale', l1='', ncb=1, v1=0, cc='randomizer.win.dimScaleFields()\nrandomizer.updateScale(1)')

        # Channels
        mc.setParent( columnLayout)
        mc.frameLayout( label='Channels',  cll=1, cl=1)
        self.channelsParent = mc.columnLayout( adj=1)
        createChannelsUI( self)

        # Components
        mc.setParent( columnLayout)
        mc.frameLayout( label='Components',  cll=1, cl=1)
        mc.columnLayout( adj=1)
        self.tCmpRange = mc.floatSliderGrp( label='Translate Range', fieldStep=.01, precision=3, field=True, min=0, fieldMinValue=0, max=1, fieldMaxValue=10000, cc='randomizer.updateComponents(1)', dc='randomizer.updateComponents(0)' )
        self.tCmpScale = mc.floatFieldGrp( label='Scale Axis', precision=3, numberOfFields=3, value1=1, value2=1, value3=1, cc='randomizer.updateComponents(1)', dc='randomizer.updateComponents(0)' )
        for c in mc.layout( self.tCmpScale, q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)

        self.cmpAlongNormal = mc.checkBoxGrp( label='Along Normal', l1='', ncb=1, v1=0, cc='randomizer.win.dimScaleFields()\nrandomizer.updateComponents(1)')
        mc.separator( h=10, style='none');

        self.cmpUseDnoise = mc.checkBoxGrp( label='Use Dnoise', l1='', ncb=1, v1=0, cc='randomizer.win.dimScaleFields()\nrandomizer.updateComponents(1)')
        self.cmpDnoiseScale = mc.floatFieldGrp( label='Scale Dnoise', precision=3, numberOfFields=3, value1=1, value2=1, value3=1, en=0, cc='randomizer.genDnoiseAll()\nrandomizer.updateComponents(1)', dc='randomizer.genDnoiseAll()\nrandomizer.updateComponents(0)' )
        for c in mc.layout( self.cmpDnoiseScale, q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)

        # Selection
        mc.setParent( columnLayout)
        mc.frameLayout( label='Selection',  cll=1, cl=1)
        mc.columnLayout( adj=1)
        self.selection = mc.floatSliderGrp( label='Selection Ratio', fieldStep=.1, precision=3, field=True, min=0, max=1, value=1, cc='randomizer.updateSelection(1)', dc='randomizer.updateSelection(0)' )

        mc.button( closeButton, edit=1, command='import maya.cmds\nmaya.cmds.deleteUI( \"' + window + '\")')
        mc.button( seedButton, edit=1, command='[o.generate() for o in randomizer.sel]\n[o.generate() for o in randomizer.selCmp]\n[o.generate() for o in randomizer.selChnl]\nrandomizer.updateAll()')
        mc.button( selectButton, edit=1, command='randomizer.start()')
        mc.button( undoButton, edit=1, command='randomizer.win.resetUI()')

    def dimScaleFields( self):
        status = 1 - mc.checkBoxGrp( self.uniformScale, q=1, v1=1)
        mc.floatFieldGrp( self.sScale, e=1, en=status)

        status = 1 - mc.checkBoxGrp( self.cmpAlongNormal, q=1, v1=1)
        mc.floatFieldGrp( self.tCmpScale, e=1, en=status)

        status = mc.checkBoxGrp( self.cmpUseDnoise, q=1, v1=1)
        mc.floatFieldGrp( self.cmpDnoiseScale, e=1, en=status)

# Reset des UI
    def resetUI( self):
        self.resetObjTranslate()
        self.resetObjRotate()
        self.resetObjScale()
        self.resetChannels()
        self.resetComponents()
        self.resetSelection()
        updateAll()

    # Transform Objects
    def resetObjTranslate( self):
        mc.floatSliderGrp( self.tRange, e=1, min=0, fieldMinValue=0, max=50, fieldMaxValue=10000, value=0)
        mc.floatFieldGrp( self.tScale, e=1, value1=1, value2=1, value3=1)

    def resetObjRotate( self):
        mc.floatSliderGrp( self.rRange, e=1, min=0, fieldMinValue=0, max=360, fieldMaxValue=10000, value=0)
        mc.floatFieldGrp( self.rScale, e=1, value1=1, value2=1, value3=1)

    def resetObjScale( self):
        mc.floatSliderGrp( self.sRange, e=1, min=0, fieldMinValue=0, max=5, fieldMaxValue=10000, value=0)
        mc.floatFieldGrp( self.sScale, e=1, value1=1, value2=1, value3=1, en=1)
        mc.checkBoxGrp( self.uniformScale, e=1, v1=0)

    # Channels
    def resetChannels( self):
        for slider in self.cRange: mc.floatSliderGrp( slider, e=1, min=0, fieldMinValue=-1000000, max=5, fieldMaxValue=1000000, value=0)
        for field in self.cOffset: mc.floatFieldGrp( field, e=1, value1=0)
        for field in self.cStep: mc.floatFieldGrp( field, e=1, value1=0)

    # Components
    def resetComponents( self):
        mc.floatSliderGrp( self.tCmpRange, e=1, min=0, fieldMinValue=0, max=1, fieldMaxValue=10000, value=0)
        mc.floatFieldGrp( self.tCmpScale, e=1, value1=1, value2=1, value3=1, en=1)
        mc.checkBoxGrp( self.cmpAlongNormal, e=1, v1=0)
        mc.checkBoxGrp( self.cmpUseDnoise, e=1, v1=0)
        mc.floatFieldGrp( self.cmpDnoiseScale, e=1, value1=1, value2=1, value3=1, en=0)

    # Selection
    def resetSelection( self):
        mc.floatSliderGrp( self.selection, e=1, min=0, max=1, value=1)

#-----------------------------------------------------------------

class SelChnlObj( object):
    def __init__( self, channel, object):
        self.channel = channel
        self.object = object
        self.value = self.savedValue = mc.getAttr( self.object + '.' + self.channel)
        self.generate()

    def generate( self):
        self.random = random.random()

    def update( self, ratio, offset, step):
        value = self.random * ratio + offset
        if step: value -= value % step
        mc.setAttr( self.object + '.' + self.channel, self.value + value)

    def saveValue( self):
        self.savedValue = mc.getAttr( self.object + '.' + self.channel)

    def getSavedValue( self):
        mc.setAttr( self.object + '.' + self.channel, self.savedValue)


#---------------------------------------
class SelChnl( object):
    def __init__( self, channel, objects):
        self.channel = mc.listAttr( objects[0] + '.' + channel)[0]
        self.objects = []
        for obj in objects:
            self.objects.append( SelChnlObj( self.channel, obj))

    def createUI( self, win, index):
# hier muss ich noch das entspr. Attr analysieren und die Min/Max korrekt setzen
        win.cRange.append( mc.floatSliderGrp( label=self.channel, fieldStep=.1, precision=3, field=True, min=0, fieldMinValue=-1000000, max=5, fieldMaxValue=1000000, cc='randomizer.updateChannel( ' + str(index) + ', 1)', dc='randomizer.updateChannel( ' + str(index) + ', 0)' ))
        win.cOffset.append( mc.floatFieldGrp( label='Offset', precision=3, numberOfFields=1, value1=0, cc='randomizer.updateChannel( ' + str(index) + ', 1)', dc='randomizer.updateChannel( ' + str(index) + ', 0)' ))
        for c in mc.layout( win.cOffset[-1], q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)
        win.cStep.append( mc.floatFieldGrp( label='Step', precision=3, numberOfFields=1, value1=0, cc='randomizer.updateChannel( ' + str(index) + ', 1)', dc='randomizer.updateChannel( ' + str(index) + ', 0)' ))
        for c in mc.layout( win.cStep[-1], q=1, ca=1)[1:]: mc.floatField( c, e=1, step=.1)
        mc.separator( style="in", h=20)

    def saveValue( self):
        for obj in self.objects: obj.saveValue()

    def getSavedValue( self):
        for obj in self.objects: obj.getSavedValue()

    def generate( self):
        for obj in self.objects: obj.generate()

def deleteChannelsUI( win):
    chnlUI = mkList( mc.layout( win.channelsParent, q=1, ca=1))
    if len(chnlUI): mc.deleteUI( chnlUI)
    win.cRange = []
    win.cOffset = []
    win.cStep = []
    mc.setParent( win.channelsParent)

def createChannelsUI( win):
    index = 0
    for channel in selChnl:
        channel.createUI( win, index)
        index += 1

#--------------------------------------------------------------------

class SelCmp( object):
    def __init__( self, name):
        self.name = name
        self.translate = mc.xform( name, q=1, t=1, worldSpace=1)
        self.translateSaved = self.translate        # for a proper undo
        self.selected = 1
        self.generate()
        self.generateDnoise( 1, 1, 1)

    def moveGlobal( self, tRange, x, y, z, useDnoise ):
        if useDnoise:
            mc.move( self.translate[0] + self.dnoiseTx * x * tRange - tRange/2 * x,
                     self.translate[1] + self.dnoiseTy * y * tRange - tRange/2 * y,
                     self.translate[2] + self.dnoiseTz * z * tRange - tRange/2 * z,
                     self.name, ws=1, absolute=1)
        else:
            mc.move( self.translate[0] + self.tx * x * tRange - tRange/2 * x,
                     self.translate[1] + self.ty * y * tRange - tRange/2 * y,
                     self.translate[2] + self.tz * z * tRange - tRange/2 * z,
                     self.name, ws=1, absolute=1)

    def moveAlongNormal( self, tRange, useDnoise):
        mc.move( self.translate[0],
                 self.translate[1],
                 self.translate[2],
                 self.name, ws=1, absolute=1)
        if useDnoise:
            mc.moveVertexAlongDirection( self.name, n=self.dnoiseTx * tRange)
        else:
            mc.moveVertexAlongDirection( self.name, n=self.tx * tRange)

    def saveTranslate( self):
        self.translateSaved = mc.xform( self.name, q=1, t=1, worldSpace=1)

    def getSavedTranslate( self):
        mc.xform( self.name, t=self.translateSaved, worldSpace=1)

# selection
    def saveSelection( self, ratio):
        if self.tx < ratio: self.selected = 1
        else: self.selected = 0

    def getSavedSelection( self):
        if self.selected: mc.select( self.name, add=1)


    def generate( self):
        self.tx = random.random()
        self.ty = random.random()
        self.tz = random.random()

    def generateDnoise( self, x, y, z):
        x *= self.translate[0]
        y *= self.translate[1]
        z *= self.translate[2]

        dnoise = mm.eval( "dnoise( <<" + str( x) + ", " + str( y) + ", " + str( z) + ">>)")
        self.dnoiseTx = dnoise[0]
        self.dnoiseTy = dnoise[1]
        self.dnoiseTz = dnoise[2]

#-------------------------------------------------------------------

class SelObj( object):
    def __init__( self, name):
        self.name = name
        self.translate  = mc.getAttr( name + '.translate')
        self.rotate     = mc.getAttr( name + '.rotate')
        self.scale      = mc.getAttr( name + '.scale')
        self.selected   = 1

        # the "saved" stuff is for a proper undo
        self.rotateSaved    = self.rotate
        self.translateSaved = self.translate
        self.scaleSaved     = self.scale

        # creates radom numbers for all channels
        self.generate()

# Translate

    def setTranslate( self, tRange, x, y, z):
        mc.setAttr( self.name + '.translateX', self.translate[0][0] + self.tx * x * tRange - tRange/2 * x)
        mc.setAttr( self.name + '.translateY', self.translate[0][1] + self.ty * y * tRange - tRange/2 * y)
        mc.setAttr( self.name + '.translateZ', self.translate[0][2] + self.tz * z * tRange - tRange/2 * z)

    def saveTranslate( self):
        self.translateSaved = mc.getAttr( self.name + '.translate')

    def getSavedTranslate( self):
        mc.setAttr( self.name + '.translate', self.translateSaved[0][0], self.translateSaved[0][1], self.translateSaved[0][2])

# Rotate

    def setRotate( self, rRange, x, y, z):
        mc.setAttr( self.name + '.rotateX', self.rotate[0][0] + self.rx * x * rRange - rRange/2 * x)
        mc.setAttr( self.name + '.rotateY', self.rotate[0][1] + self.ry * y * rRange - rRange/2 * y)
        mc.setAttr( self.name + '.rotateZ', self.rotate[0][2] + self.rz * z * rRange - rRange/2 * z)

    def saveRotate( self):
        self.rotateSaved = mc.getAttr( self.name + '.rotate')

    def getSavedRotate( self):
        mc.setAttr( self.name + '.rotate', self.rotateSaved[0][0], self.rotateSaved[0][1], self.rotateSaved[0][2])

# Scale

    def setScale( self, sRange, x, y, z, uniform):
        if uniform: scaleX = scaleY = scaleZ = 1 + self.sx * sRange
        else:
            scaleX = 1 + self.sx * x * sRange
            scaleY = 1 + self.sy * y * sRange
            scaleZ = 1 + self.sz * z * sRange

        if self.sDir:
            mc.setAttr( self.name + '.scaleX', self.scale[0][0] * scaleX)
            mc.setAttr( self.name + '.scaleY', self.scale[0][1] * scaleY)
            mc.setAttr( self.name + '.scaleZ', self.scale[0][2] * scaleZ)
        else:
            mc.setAttr( self.name + '.scaleX', self.scale[0][0] / scaleX)
            mc.setAttr( self.name + '.scaleY', self.scale[0][1] / scaleY)
            mc.setAttr( self.name + '.scaleZ', self.scale[0][2] / scaleZ)

    def saveScale( self):
        self.scaleSaved = mc.getAttr( self.name + '.scale')

    def getSavedScale( self):
        mc.setAttr( self.name + '.scale', self.scaleSaved[0][0], self.scaleSaved[0][1], self.scaleSaved[0][2])

# selection
    def saveSelection( self, ratio):
        if self.tx < ratio: self.selected = 1
        else: self.selected = 0

    def getSavedSelection( self):
        if self.selected: mc.select( self.name, add=1)

    def generate( self):
        self.tx = random.random()
        self.ty = random.random()
        self.tz = random.random()

        self.rx = random.random()
        self.ry = random.random()
        self.rz = random.random()

        self.sx = random.random()
        self.sy = random.random()
        self.sz = random.random()
        self.sDir = random.random() > .5

#-------------------------------------------------------------------


def updateChannel( index, undoState):
    global selChnl
    global win

    if undoState:
        for chnl in selChnl[index].objects: chnl.getSavedValue()
    mc.undoInfo( stateWithoutFlush=undoState)

    ratio = mc.floatSliderGrp( win.cRange[index], q=1, v=1)
    offset = mc.floatFieldGrp( win.cOffset[index], q=1, v=1)[0]
    step = mc.floatFieldGrp( win.cStep[index], q=1, v=1)[0]
    for obj in selChnl[index].objects:
        obj.update( ratio, offset, step)

    if undoState:
        for chnl in selChnl[index].objects: chnl.saveValue()

def updateAllChannels( undoState):
    for index in range( len(selChnl)): updateChannel( index, undoState)

def updateSelection(undoState):
    global sel
    global selCmp
    global win

    if undoState:
        mc.select( cl=1)
        for obj in sel: obj.getSavedSelection()
        for cmp in selCmp: cmp.getSavedSelection()
    mc.undoInfo( stateWithoutFlush=undoState)

    ratio = mc.floatSliderGrp( win.selection, q=1, v=1)
    mc.select( cl=1)
    #if len( sel) : random.seed( sel[0].tx)
    #elif len( selCmp): random.seed( selCmp[0].tx)

    for obj in sel:
        if obj.tx < ratio:
            mc.select( obj.name,  add=1)

    for cmp in selCmp:
        if cmp.tx < ratio:
            mc.select( cmp.name,  add=1)

    if undoState:
        for obj in sel: obj.saveSelection( ratio)
        for cmp in selCmp: cmp.saveSelection( ratio)


def updateComponents(undoState):
    global selCmp
    global win

    if undoState:
        for cmp in selCmp: cmp.getSavedTranslate()
    mc.undoInfo( stateWithoutFlush=undoState)
    tRange = mc.floatSliderGrp( win.tCmpRange, q=1, v=1)
    tScaleX, tScaleY, tScaleZ = mc.floatFieldGrp( win.tCmpScale, q=1, v=1)
    alongNormal = mc.checkBoxGrp( win.cmpAlongNormal, q=1, v1=1)
    useDnoise = mc.checkBoxGrp( win.cmpUseDnoise, q=1, v1=1)
    if alongNormal:
        for cmp in selCmp: cmp.moveAlongNormal( tRange, useDnoise)
    else:
        for cmp in selCmp: cmp.moveGlobal( tRange, tScaleX, tScaleY, tScaleZ, useDnoise)
    if undoState:
        for cmp in selCmp: cmp.saveTranslate()

def genDnoiseAll():
    scaleX, scaleY, scaleZ = mc.floatFieldGrp( win.cmpDnoiseScale, q=1, v=1)
    for cmp in selCmp: cmp.generateDnoise( scaleX, scaleY, scaleZ)


def updateTranslate(undoState):
    global sel
    global win

# the undo is switched off while using a slider
# after release there is one call to this function with undoState = 1
# and in this call I will fist set the previously *saved* state
# and then switch on the undoQueue and set the new position
# this way, the user gets a proper undo

    if undoState:
        for obj in sel: obj.getSavedTranslate()
    mc.undoInfo( stateWithoutFlush=undoState)

    tRange = mc.floatSliderGrp( win.tRange, q=1, v=1)
    tScaleX, tScaleY, tScaleZ = mc.floatFieldGrp( win.tScale, q=1, v=1)
    for obj in sel: obj.setTranslate( tRange, tScaleX, tScaleY, tScaleZ)

    if undoState:
        for obj in sel: obj.saveTranslate()


def updateRotate(undoState):
    global sel
    global win

    if undoState:
        for obj in sel: obj.getSavedRotate()
    mc.undoInfo( stateWithoutFlush=undoState)

    rRange = mc.floatSliderGrp( win.rRange, q=1, v=1)
    rScaleX, rScaleY, rScaleZ = mc.floatFieldGrp( win.rScale, q=1, v=1)
    for obj in sel: obj.setRotate( rRange, rScaleX, rScaleY, rScaleZ)

    if undoState:
        for obj in sel: obj.saveRotate()


def updateScale(undoState):
    global sel
    global win

    if undoState:
        for obj in sel: obj.getSavedScale()
    mc.undoInfo( stateWithoutFlush=undoState)

    sRange = mc.floatSliderGrp( win.sRange, q=1, v=1)
    sScaleX, sScaleY, sScaleZ = mc.floatFieldGrp( win.sScale, q=1, v=1)
    uniform = mc.checkBoxGrp( win.uniformScale, q=1, v1=1)
    for obj in sel: obj.setScale( sRange, sScaleX, sScaleY, sScaleZ, uniform)

    if undoState:
        for obj in sel: obj.saveScale()

def updateAll():
    updateTranslate(1)
    updateRotate(1)
    updateScale(1)
    updateSelection(1)
    updateAllChannels(1)
    updateComponents(1)


def mkList( stuff):
    if type( stuff) == list: return stuff
    else: return []


def start():

    global sel
    sel=[]
    global selCmp
    selCmp = []
    global selChnl
    selChnl = []
    global win

# the Channels first

    cb = mm.eval( "$temp = $gChannelBoxName")
    cbObjects   = mc.channelBox( cb, q=1, mainObjectList=1)
    cbShapes    = mc.channelBox( cb, q=1, shapeObjectList=1)
    cbHistory   = mc.channelBox( cb, q=1, historyObjectList=1)
    cbOutputs   = mc.channelBox( cb, q=1, outputObjectList=1)

    cbMainAttrList      = mkList( mc.channelBox( cb, q=1, selectedMainAttributes=1))
    cbShapesAttrList    = mkList( mc.channelBox( cb, q=1, selectedShapeAttributes=1))
    cbHistoryAttrList   = mkList( mc.channelBox( cb, q=1, selectedHistoryAttributes=1))
    cbOutputsAttrList   = mkList( mc.channelBox( cb, q=1, selectedOutputAttributes=1))

    for attr in cbMainAttrList:
        selChnl.append( SelChnl( attr, cbObjects))
    for attr in cbShapesAttrList:
        selChnl.append( SelChnl( attr, cbShapes))
    for attr in cbHistoryAttrList:
        selChnl.append( SelChnl( attr, cbHistory))
    for attr in cbOutputsAttrList:
        selChnl.append( SelChnl( attr, cbOutputs))

# now the selected Transforms
    for obj in mc.ls( sl=1, objectsOnly=1, l=1, type='transform'):
        sel.append( SelObj( obj))

# finaly the selected components
    polyComponents = mc.ls( sl=1, l=1, type='float3')
    otherComponents = mc.ls( sl=1, l=1, flatten=1, type='double3')
    if len(polyComponents): polyComponents = mc.ls( mc.polyListComponentConversion( polyComponents, toVertex=1), l=1, flatten=1)
    components = polyComponents + otherComponents
    for cmp in components:
        selCmp.append( SelCmp( cmp))

    #mc.select( selection, replace=1)
    if not mc.window( 'randomizerWin', exists=1):
        win = RandomizerWindow()
    else:
        deleteChannelsUI( win)
        createChannelsUI( win)

    win.resetUI()
    mc.showWindow( 'randomizerWin')


