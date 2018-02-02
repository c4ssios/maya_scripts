import maya.cmds as mc
import maya.cmds as cmds
import maya.mel as mel

# SET correct brush -------------------------------------------------------------------------
version = mc.about(v=True)  # command to get Maya version you are now running
OS = mc.about(os=True)
    
if OS == 'win64':
    if version == '2018':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "C:/Program Files/Autodesk/Maya2018/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2017':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "C:/Program Files/Autodesk/Maya2017/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2016':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "C:/Program Files/Autodesk/Maya2016/brushes/trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2015':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "C:/Program Files/Autodesk/Maya2015/brushes/trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2014':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "C:/Program Files/Autodesk/Maya2014/brushes/trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2019':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "C:/Program Files/Autodesk/Maya2019/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')

elif OS == 'mac':
    if version == '2018':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/Applications/Autodesk/maya2018/Maya.app/Contents/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2017':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/Applications/Autodesk/maya2017/Maya.app/Contents/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2016':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/Applications/Autodesk/maya2016/Maya.app/Contents/brushes/trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2015':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/Applications/Autodesk/maya2015/Maya.app/Contents/brushes/trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2014':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/Applications/Autodesk/maya2014/Maya.app/Contents/brushes/trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')
    elif version == '2019':
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/Applications/Autodesk/maya2019/Maya.app/Contents/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')


elif OS == 'linux64':
    if version == '2018':
        print ("Linux2018")
    elif version == '2017':
        print ("Linux2017")

    elif '2016' in version:
        mel.eval('visorPanelBrushPressCallback files1VisorEd "/lucas/ilm/sww/rhel6/tools/autodesk/maya2016-x64_ext2_sp2_p11/Examples/Paint_Effects/Trees/birchLimb.mel";')
        mel.eval('setToolTo $gMove;')




# SET default setting for the tube --------------------------------------------------------------
#mel.eval('brushToolSettings;')
mc.setAttr("birchLimb.globalScale", 10)
mc.setAttr("birchLimb.brushWidth", 0.1)
mc.setAttr("birchLimb.forwardTwist", 0)
mc.setAttr(("birchLimb.color1"), 0, 0.149078, 0.228, type='double3')
mc.setAttr(("birchLimb.specularColor"), 0, 0, 0, type='double3')
mc.setAttr(("birchLimb.tubeSections"), 8)

  
    
#UI_______________________________________

def cableUI():

  if mc.window("Cable", exists =True):
      mc.deleteUI("Cable")



  ram = mc.window("Cable", t="Cable v1.4", tlb=True, menuBar=True)
  mc.columnLayout(adj = True, w=300, h=365)

  mc.menu( label='Info' )
  mc.menuItem( label='Arstation',annotation='My Website', c= "goArtstation(()")
  mc.menuItem( label='Gumroad', annotation='Tutorial', c= "goGumroad()" )
  mc.menuItem( label='Contact', annotation='For Any Help', c= "goFacebook()" )

  mc.menu( label='Thanks' )
  mc.menuItem( label='Adnan Chaumette', c= "goAdnan()")
  mc.menuItem( label='Clement Feuillet', c= "goClement()" )
  mc.menuItem( label='Klaudio Ladavac', c= "goKlaudio()" )
	      

  cH1 = mc.columnLayout(adj =True)
  #frameCreate = mc.frameLayout(l = "CREATE", cll =1, cl =0, bgc= [0.302, 0.494, 0.588])
  mc.text ( l= '  > CREATE', al= 'left', h= 18, font= 'smallPlainLabelFont', bgc= [0.302, 0.494, 0.588])


  ########################################
  # ADDED row column bor icons and buttons 
  ########################################
  mc.rowColumnLayout ( numberOfRows = 1 )
  mc.separator (w = 50, style = 'none') 
  toolCV = mc.symbolButton( image='curveEP.png', c= mc.EPCurveTool, ann= "EP Curve")
  mc.separator (w = 40, style = 'none') 
  toolBezier = mc.symbolButton( image='curveBezier.png', c= mc.CreateBezierCurveTool, ann= "Bezier Curve")
  mc.separator (w = 40, style = 'none') 
  toolPen = mc.symbolButton( image='pencil.png', c= mc.PencilCurveTool, ann= "Pencil Curve")
  mc.separator (w = 40, style = 'none') 
  mc.setParent( '..' )


  mc.rowColumnLayout ( numberOfRows = 1 )
  mc.separator (w = 2, style = 'none') 
  buttonCreate = mc.button('buttonCreate', w= 290, l= "CREATE Cables", c= Attach_Cable, ann= "Create cables")
  mc.setParent( '..' )
  ########################################


  mc.setParent(cH1)
  mc.separator(h= 10, style = 'none')

  cH2 = mc.columnLayout(adj =True)
  #frameEdit = mc.frameLayout(l = "EDIT", cll =1, cl =0, bgc= [0.302, 0.494, 0.588])
  mc.text ( l= '  > EDIT', al= 'left', h= 18, font= 'smallPlainLabelFont', bgc= [0.302, 0.494, 0.588])

  mc.separator(h= 3, style = 'none')
  slideScale = mc.floatSliderGrp('Slider_Scale', l = "Scale",min =0.1, max =500,po =True, field =True, cc=Scale_Val, dc=Scale_Val, v= 100, adj =0, cat= [1, "left", 3], cw= [1, 60], ann= "Configure to scene set in cm")
  slideWidth = mc.floatSliderGrp('Slider_Width', l = "Width",min =0.1, max =1,po =True, field =True, cc=Width_Val, dc=Width_Val, v= 0.1, pre= 3, adj =0, cat= [1, "left", 3], cw= [1, 60])
  slideDensity = mc.floatSliderGrp('Slider_Density', l = "Density",min =0.1, max =5,po =True, field =True, cc=Density_Val, dc=Density_Val, v= 1, adj =0, cat= [1, "left", 3], cw= [1, 60])
  slideSection = mc.intSliderGrp('Slider_Section', l = "Section",min =3, max =12,po =True, field =True, cc=Section_Val, dc=Section_Val, v= 8, adj =0, cat= [1, "left", 3], cw= [1, 60])
  slideSmoothing = mc.floatSliderGrp('Slider_Smoothing', l = "Smoothing",min =0, max =500,po =True, field =True, cc=Smoothing_Val, dc=Smoothing_Val, v= 0, adj =0, cat= [1, "left", 3], cw= [1, 60])
  checkboxLearn = mc.checkBoxGrp('Check_Twist', l= "Twist", onc=twist_on, ofc=twist_off,adj =0, cat= [1, "left", 3], cw= [1, 60])
  slideTwist = mc.floatSliderGrp('Slider_Twist', l = "Twist Rate",min =0, max =300,po =True, field =True, cc=Twist_Val, dc=Twist_Val, v= 0, adj =0, cat= [1, "left", 3], cw= [1, 60])
  reference = mc.checkBoxGrp('Check_Manip', l= "Manipulation", onc=Manip_on, ofc=Manip_off,adj =0, cat= [1, "left", 1], cw= [1, 80], v1= 0, ann= "Easier to manipulate curves")

  mc.setParent(cH2)
  mc.separator(h= 15, style = 'none')

  cH3 = mc.columnLayout(adj =True)
  #frameEdit = mc.frameLayout(l = "CONVERT", cll =1, cl =0, bgc= [0.302, 0.494, 0.588])
  mc.text ( l= '  > CONVERT', al= 'left', h= 18, font= 'smallPlainLabelFont', bgc= [0.302, 0.494, 0.588])



  #mc.text(l= "To finish you should convert into Mesh the cable.", al= "left", h= 25, w= 293, backgroundColor= [0.24, 0.24, 0.24])
  #mc.text(l= "But once you've bake to geo, you loose Edit possibility", al= "left", h= 25, w= 293, backgroundColor= [0.24, 0.24, 0.24])
  mc.separator(h=3, style = 'none')
  mc.rowColumnLayout ( numberOfRows = 1 )
  buttonBakeHistory = mc.button('buttonBakeHistory', w=95, l= "Bake + History", c=B_History, ann= "Convert to Mesh and keep history to manipulate with Curve")
  mc.separator (w = 4, style = 'none') 
  buttonBake = mc.button('buttonBake', w=95, l= "BAKE", c=B_Bake, ann= "Convert to Mesh, delete history and remove extra node")
  mc.separator (w = 4, style = 'none') 
  buttonBakeCurve = mc.button('buttonBakeCurve', w=95, l= "Bake + Curve", c=B_BakeC, ann= "Convert to Mesh, delete history but keep the original curve")
  mc.setParent( '..' )

  mc.rowColumnLayout ( numberOfRows = 1 )
  mc.separator (w = 1, h=5, style = 'none') 
  buttonBackToC = mc.button('buttonBackToCurve', w=290, l= "Back to Curve", c=B_BtoC, ann= "Rebuild curve based on Geo")
  #referenceMesh = mc.checkBoxGrp('Check_ManipMesh', l= "Manipulation", onc="Manip_Mesh_on()", ofc="Manip_Mesh_off()",adj =0, cat= [1, "left", 1], cw= [1, 80], v1= 0)
  #referenceMeshX = mc.checkBoxGrp('Check_ManipMeshX', l= "ManipulationX", onc="Manip_MeshX_on()", ofc="Manip_MeshX_off()",adj =0, cat= [1, "left", 1], cw= [1, 80], v1= 0)
  mc.setParent( '..' )


  mc.setParent(cH3)
  mc.separator(h= 1, style = 'none')
  cH4 = mc.columnLayout(adj =True)

  mc.showWindow(ram)

  ########################################
  # ADDED - edit the size of the wwindow to fit new organization
  ########################################
  mc.window (ram, edit=True, h=385)
  ########################################



###________________________________________CREATE_______________________________###

def Attach_Cable(*args):
    import maya.mel as mel
    mel.eval('AttachBrushToCurves')
    mel.eval('convertCurvesToStrokes')
    mel.eval('setToolTo $gMove;')
               

###________________________________________INFO_______________________________###

def goArtstation():
    mc.launch(web= "https://wizix.artstation.com/")

def goGumroad():
    mc.launch(web= "https://gumroad.com/wzx")
    
def goFacebook():
    mc.launch(web= "https://www.facebook.com/WizixPage/")

def goAdnan():
    mc.launch(web= "https://www.artstation.com/fansub")
    
def goClement():
    mc.launch(web= "https://www.artstation.com/artist/grxz")
    
def goKlaudio():
    mc.launch(web= "https://www.artstation.com/klaudio2u")



###________________________________________EDIT_______________________________###

##___________________________________________________PaintEffectControl
#SCALE__________________
def Scale_Val(*args):

    myValueWidght = mc.floatSliderGrp("Slider_Scale", q= True, value=True)

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')

    buffer = mc.listConnections(selection, d = True, scn=True, type= 'brush')

    for each in buffer:
        mc.setAttr(each + ".globalScale", myValueWidght)

#WIDTH__________________
def Width_Val(*args):

    myValueWidght = mc.floatSliderGrp("Slider_Width", q= True, value=True)

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')

    buffer = mc.listConnections(selection, d = True, scn=True, type= 'brush')

    for each in buffer:
        mc.setAttr(each + ".brushWidth", myValueWidght)

#SECTION__________________
def Section_Val(*args):

    myValueWidght = mc.intSliderGrp("Slider_Section", q= True, value=True)

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')

    buffer = mc.listConnections(selection, d = True, scn=True, type= 'brush')

    for each in buffer:
        mc.setAttr(each + ".tubeSections", myValueWidght)


#TWIST__________________
def twist_on(*args):

    myValueWidght = 0

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')

    buffer = mc.listConnections(selection, d = True, scn=True, type= 'brush')

    for each in buffer:
        mc.setAttr(each + ".forwardTwist", myValueWidght)

def twist_off(*args):

    myValueWidght = 1

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')

    buffer = mc.listConnections(selection, d = True, scn=True, type= 'brush')

    for each in buffer:
        mc.setAttr(each + ".forwardTwist", myValueWidght)

#MANIP__________________
def Manip_on(*args):
    
    selection = mc.ls(typ='stroke', ni=True, o=True, r=True)
       
    for each in selection:
        mc.setAttr(each + ".overrideEnabled", 1)
        mc.setAttr(each + ".overrideDisplayType", 2)
        mc.select(d= True)

def Manip_off(*args):

    selection = mc.ls(typ='stroke', ni=True, o=True, r=True)
         
    for each in selection:
        mc.setAttr(each + ".overrideEnabled", 0)
        
#TWIST RATE__________________
def Twist_Val(*args):

    myValueWidght = mc.floatSliderGrp("Slider_Twist", q= True, value=True)

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')

    buffer = mc.listConnections(selection, d = True, scn=True, type= 'brush')

    for each in buffer:
        mc.setAttr(each + ".twistRate", myValueWidght)



##___________________________________________________Stroke 
#DENSITY__________________
def Density_Val(*args):

    myValueWidght = mc.floatSliderGrp("Slider_Density", q= True, value=True)

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')


    for each in selection:
        mc.setAttr(each + ".sampleDensity", myValueWidght)
        

#SMOOTHING__________________
def Smoothing_Val(*args):

    myValueWidght = mc.floatSliderGrp("Slider_Smoothing", q= True, value=True)

    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')


    for each in selection:
        mc.setAttr(each + ".smoothing", myValueWidght)
        
        
###________________________________________BAKE_______________________________###

def B_History(*args):
    
    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')
    
    for each in selection:
        mc.select(each)
        import maya.mel as mel    
        mel.eval('doPaintEffectsToPoly(1,0,1,1,100000);')
        mel.eval('polyMultiLayoutUV -lm 1 -sc 1 -rbf 0 -fr 1 -ps 0.05 -l 2 -gu 1 -gv 1 -psc 1 -su 1 -sv 1 -ou 0 -ov 0;')
        mc.CenterPivot()
        mc.hyperShade( a= "lambert1")
        selected_objects = mc.ls("birchLimb*MeshGroup")
        newname = "Cable_Hist_"
        for number, object in enumerate(selected_objects):
            print 'Old Name:', object
            print 'New Name:', '%s%02d' % (newname, number)
            mc.rename(object, ('%s%02d' % (newname, number)))
        
    print "Done"
       
    
    
def B_Bake(*args):
    
    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')
         
    
    for each in selection:
        sel1 = mc.ls(sl= True, fl = True, dag = True)
        sel2 = mc.listConnections(sel1)
        selAll = sel1 + sel2
        import maya.mel as mel    
        mel.eval('doPaintEffectsToPoly(1,0,1,1,100000);')
        mel.eval('polyMultiLayoutUV -lm 1 -sc 1 -rbf 0 -fr 1 -ps 0.05 -l 2 -gu 1 -gv 1 -psc 1 -su 1 -sv 1 -ou 0 -ov 0;')
        mc.delete(ch= True)
        mc.parent(w= True)
        sel4 = mc.ls("birchLimb*MeshGroup")
        mc.delete(selAll)
        mc.delete(sel4)
        mc.CenterPivot()
        mc.hyperShade( a= "lambert1")
        selected_objects = mc.ls(selection=True)
        newname = "Cable_"
        for number, object in enumerate(selected_objects):
            print 'Old Name:', object
            print 'New Name:', '%s%02d' % (newname, number)
            mc.rename(object, ('%s%02d' % (newname, number)))
    

def B_BakeC(*args):
    
    selection = mc.ls(sl = True, fl = True, dag = True, type= 'stroke')
         
    
    for each in selection:
        sel1 = mc.ls(sl= True, fl = True, dag = True)
        sel2 = mc.listConnections(sel1)
        sel2 = mc.listConnections(sel1, type= 'stroke')
        sel3 = mc.listConnections(sel1, type= 'transform')
        import maya.mel as mel    
        mel.eval('doPaintEffectsToPoly(1,0,1,1,100000);')
        mel.eval('polyMultiLayoutUV -lm 1 -sc 1 -rbf 0 -fr 1 -ps 0.05 -l 2 -gu 1 -gv 1 -psc 1 -su 1 -sv 1 -ou 0 -ov 0;')
        mc.delete(ch= True)
        mc.parent(w= True)
        sel4 = mc.ls("birchLimb*MeshGroup")
        mc.delete(sel1)
        mc.delete(sel2)
        mc.delete(sel3)
        mc.delete(sel4)
        mc.CenterPivot()
        mc.hyperShade( a= "lambert1")
        selected_objects = mc.ls(selection=True)
        newname = "Cable_"
        for number, object in enumerate(selected_objects):
            print 'Old Name:', object
            print 'New Name:', '%s%02d' % (newname, number)
            mc.rename(object, ('%s%02d' % (newname, number)))
            
    print "Done"


def B_BtoC(*args):
    
    getSelect=mc.ls(sl=True)
    
    for each in getSelect:
        #mc.select(each)        
        #mc.ConvertSelectionToEdgePerimeter()
        #sel = mc.ls(sl= True)
        #selA = mc.select(sel[1])
        #mc.SelectEdgeLoopSp()
        #mc.CreateCluster()
        #mc.rename("ClusterTps")
        #selClu = mc.ls(sl= True)
        mc.select(each)        
        mc.ConvertSelectionToEdgePerimeter()
        mc.ConvertSelectionToFaces()
        mc.ConvertSelectionToContainedEdges()
        sel = mc.ls(sl= True)
        selO = mc.ls(os= True)
        selA = mc.select(selO[1])
        mc.SelectEdgeLoopSp()
        mc.polyToCurve(form= 2,degree= 1,conformToSmoothMeshPreview= 0)      
        mc.CenterPivot()
        mc.DeleteHistory()
        mc.rename("Curve_0")
        selCurv = mc.ls(sl= True)
        posX = mc.getAttr(selCurv[0]+".controlPoints[0].xValue")
        posY = mc.getAttr(selCurv[0]+".controlPoints[0].yValue")
        posZ = mc.getAttr(selCurv[0]+".controlPoints[0].zValue")
        mc.move(posX, posY, posZ, selCurv[0] + ".scalePivot", selCurv[0] + ".rotatePivot", absolute=True)
        #selAll = mc.ls(selClu + selCurv)
        #mc.matchTransform(selCurv, selClu)
        #mc.delete("ClusterTps")

