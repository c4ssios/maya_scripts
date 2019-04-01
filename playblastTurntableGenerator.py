import maya.cmds as cmds
import maya.mel as mel


def playblastTurntableGenerator():

	model = cmds.ls(sl=True, l=True)

	if len(model)<1:
		cmds.warning('Nothing is selected. Select at least 1 object/group.')
	else:
		scaleFactor = getSceneBBoxScale(model)
		modelCenter = getSceneBBoxCenter(model)


		'''
		Create lightRig
		'''
		namespaces = cmds.namespaceInfo(':', listOnlyNamespaces=True, r=True)
		if 'turntableSet' in namespaces:
			cmds.namespace(setNamespace=':')
			cmds.namespace(deleteNamespaceContent=True, removeNamespace='turntableSet')

		turntableSetNamespace = 'turntableSet'
		cmds.namespace(add=turntableSetNamespace)

		turntableSetGroupName = turntableSetNamespace + ':' + turntableSetNamespace + '_GRP'
		cmds.group(em=True, name=turntableSetGroupName)
		lightGroupName = (turntableSetNamespace + ':lights_GRP')
		cmds.group(em=True, name=lightGroupName)
		cmds.parent(lightGroupName,turntableSetGroupName)


		spotLight01 = 'turntableSpotLight01'
		cmds.spotLight(n=turntableSetNamespace + ':' + spotLight01, coneAngle=70, intensity=1.065, penumbra=7.5, dropOff=15)
		cmds.setAttr(turntableSetNamespace + ':' + spotLight01 + '.useDepthMapShadows', 1)
		cmds.setAttr(turntableSetNamespace + ':' + spotLight01 + '.dmapResolution', 4096)
		cmds.setAttr(turntableSetNamespace + ':' + spotLight01 + '.dmapFilterSize', 10)
		cmds.setAttr(turntableSetNamespace + ':' + spotLight01 + '.shadowColor', 0.213, 0.213, 0.213,type='double3')
		cmds.xform(turntableSetNamespace + ':' + spotLight01 , t=(10.68561, 10.28704, 13.95764), ro=(-27.66044, 32.98632, 0), ws=True)
		cmds.parent(turntableSetNamespace + ':' + spotLight01, lightGroupName)

		spotLight02 = 'turntableSpotLight02'
		cmds.spotLight(n=turntableSetNamespace + ':' + spotLight02, coneAngle=45, intensity=0.4, penumbra=7.5, dropOff=5)
		cmds.setAttr(turntableSetNamespace + ':' + spotLight02 + '.shadowColor', 1, 1, 1,type='double3')
		cmds.xform(turntableSetNamespace + ':' + spotLight02 , t=(-10.43612, 8.78771, -5.27289), ro=(-217.39926, -65.2236, -180), ws=True)
		cmds.parent(turntableSetNamespace + ':' + spotLight02, lightGroupName)

		directionalLight01 = 'turntableDirect01'
		cmds.directionalLight(n=turntableSetNamespace + ':' + directionalLight01, intensity=0.3, rotation=[-47.78754, 0, 0])
		cmds.setAttr(turntableSetNamespace + ':' + directionalLight01 + '.shadowColor', 1, 1, 1,type='double3')
		cmds.parent(turntableSetNamespace + ':' + directionalLight01, lightGroupName)

		cycloGeoCreation('turntableSet', 'defaultGrey_C_cycloA_GES')
		cmds.parent(turntableSetNamespace+':defaultGrey_C_cycloA_GES', turntableSetGroupName)


		'''
		Adjust Rig Scale and Pos
		'''

		cmds.xform(turntableSetGroupName, absolute=True, translation=[modelCenter[0],cmds.exactWorldBoundingBox(model, ignoreInvisible=True)[1],modelCenter[2]], ws=True)
		cmds.scale(scaleFactor,scaleFactor,scaleFactor, turntableSetGroupName , absolute=True)

		
		'''
		Create and Assign shaders
		'''

		createAndAssignShaders(turntableSetNamespace, model)


		'''
		Create Camera
		'''
		cameraName = turntableSetNamespace +':'+ 'turntableCameraA_CAM'
		cam = cmds.camera()
		cmds.rename(cam[0], cameraName)
		cmds.setAttr(cameraName+'.focalLength', 50)
		cmds.setAttr(cameraName+'.displayGateMaskColor', 0,0,0, type='double3')
		cmds.setAttr(cameraName+'.displayGateMaskOpacity', 1)
		cmds.xform(cameraName, absolute=True, translation=[0, modelCenter[1]*1.5, scaleFactor*12], ws=True)

		cameraAimLocatorName = turntableSetNamespace + ':cameraAim_CTRL'
		cmds.spaceLocator(n=cameraAimLocatorName)
		cmds.aimConstraint(cameraAimLocatorName, cameraName, n=turntableSetNamespace + ':cameraAimConstraint')
		cmds.setAttr(turntableSetNamespace + ':cameraAimConstraint.offsetY', -90)
		cmds.xform(cameraAimLocatorName, absolute=True, translation=modelCenter, ws=True)

		mel.eval('setNamedPanelLayout("Single Perspective View")')
		cmds.lookThru( cameraName )

		cmds.parent(cameraName,turntableSetGroupName)
		cmds.parent(cameraAimLocatorName, turntableSetGroupName)



		'''
		Create Turntable Locator
		'''
		locName = turntableSetNamespace +':turntableLocatorA_LOC'
		cmds.spaceLocator(n=locName)
		cmds.xform(locName, absolute=True, translation=[modelCenter[0], 0, modelCenter[2]], ws=True)
		cmds.parent(locName, turntableSetGroupName)
		cmds.parentConstraint(locName, model, maintainOffset=True, n=turntableSetNamespace +':parentConstraint_CTR')


		'''
		Turntable Animation
		'''
		setSpinAnim(locName, 1, 101)
		#setSpinAnim(lightGroupName, 101, 201)
		#setSpinAnim(lightGroupName, 101, 201)
		#setSpinAnim(lightGroupName, 101, 201)

		'''
		Time Settings
		'''
		startFrame = 1
		endFrame = 100

		cmds.playbackOptions(ast=startFrame, e=True)
		cmds.playbackOptions(aet=endFrame, e=True)
		cmds.playbackOptions(min=startFrame, e=True)
		cmds.playbackOptions(max=endFrame, e=True)


		'''
		Viewport Settings
		'''
		panel = getPanelFromCamera(turntableSetNamespace+':turntableCameraA_CAMShape')[0]

		cmds.modelEditor(panel ,e=True, displayAppearance='smoothShaded')
		cmds.modelEditor(panel ,e=True, dl='all')
		cmds.modelEditor(panel ,e=True, shadows=1)
		cmds.modelEditor(panel, e=True, allObjects=0)
		cmds.modelEditor(panel, e=True, polymeshes=1)
		cmds.modelEditor(panel, e=True, grid=0)
		cmds.setAttr ("hardwareRenderingGlobals.ssaoEnable", 1)
		cmds.setAttr ("hardwareRenderingGlobals.multiSampleEnable", 1)

		activateSmoothPreview(model)


		'''
		 Render Settings
		'''

		cmds.setAttr("defaultResolution.width", 1920)
		cmds.setAttr("defaultResolution.height", 1080)




def cycloGeoCreation(namespace, name):

	pp1 = [-12, -2.6394186146319176e-15, 11]
	pp2 = [-12, 15.735990524291992, -7.29987907409668]
	pp3 = [-12, -2.6394186146319176e-15, -4.922739028930664]
	pp4 = [-12, 0.18094894289970398, -5.832431793212891]
	pp5 = [-12, 0.696247935295105, -6.603630065917969]
	pp6 = [-12, 1.4674474000930786, -7.118930816650391]
	pp7 = [-12, 2.37713885307312, -7.29987907409668]
	pp8 = [-12, 12.396276473999023, -7.29987907409668]
	pp9 = [-12, 9.056564331054688, -7.29987907409668]
	pp10 = [-12, 5.716851234436035, -7.29987907409668]
	pp11 = [-12, -2.6394186146319176e-15, -0.9603691101074219]
	pp12 = [-12, -2.6394186146319176e-15, 3.002007007598877]
	pp13 = [-12, -2.6394186146319176e-15, 7]

	cmds.curve(n=namespace+':tempCurve', d=1, p=[pp1, pp13,  pp12, pp11, pp3 ,pp4, pp5, pp6, pp7,pp10, pp9,  pp8, pp2])
	cmds.extrude(namespace+':tempCurve', ch=True, rn=False, po=1, et=0, upn=0, d=[1,0,0], length=24, scale=1, dl=1, n=namespace+':'+name)
	tesselateNode = cmds.listHistory(namespace+':'+name, pdo=True)[0]

	cmds.setAttr(tesselateNode+'.polygonType', 1)
	cmds.setAttr(tesselateNode+'.format', 2)
	cmds.setAttr(tesselateNode+'.uNumber', 1)
	cmds.setAttr(tesselateNode+'.vNumber', 6)
	cmds.polyNormal(namespace+':'+name, ch=False)

	cmds.delete(namespace+':'+name,ch=True)
	cmds.delete(namespace+':tempCurve')
	cmds.select(cl=True)

	cycloShader = cmds.shadingNode('lambert', name=namespace+':'+'cyclo_MAT', asShader=True)
	cycloShaderSG = cmds.sets(name=namespace+':'+'cyclo_MAT_SG', empty=True, renderable=True, noSurfaceShader=True)
	cmds.connectAttr(cycloShader+'.outColor', cycloShaderSG+'.surfaceShader')
	cmds.setAttr(cycloShader+'.color', 0.9, 0.9, 0.9, type='double3')
	cmds.sets(namespace+':'+name, e=True, forceElement=cycloShaderSG)

	activateSmoothPreview(namespace+':'+name)


def createAndAssignShaders(namespace, objects):

	objectList = cmds.listRelatives(objects, typ='mesh', ad=True, f=True)
	
	'''
	default grey Shader
	'''
	defaultShader = cmds.shadingNode('blinn', name=namespace+':'+'turntable_MAT', asShader=True)
	defaultShaderSG = cmds.sets(name=namespace+':'+'turntable_MAT_SG', empty=True, renderable=True, noSurfaceShader=True)
	cmds.connectAttr(defaultShader+'.outColor', defaultShaderSG+'.surfaceShader')
	cmds.setAttr(defaultShader+'.color', 0.35, 0.35, 0.35, type='double3')


	'''
	glass Shader
	'''
	glassShader = cmds.shadingNode('blinn', name=namespace+':'+'glassTurntable_MAT', asShader=True)
	glassShaderSG = cmds.sets(name=namespace+':'+'glassTurntable_MAT_SG', empty=True, renderable=True, noSurfaceShader=True)
	cmds.connectAttr(glassShader+'.outColor', glassShaderSG+'.surfaceShader')
	cmds.setAttr(glassShader+'.color', 0, 0, 0, type='double3')
	cmds.setAttr(glassShader+'.specularColor', 1, 1, 1, type='double3')
	cmds.setAttr(glassShader+'.transparency', 1, 1, 1, type='double3')
	cmds.setAttr(glassShader+'.reflectedColor', 0.084, 0.084, 0.084, type='double3')
	cmds.setAttr(glassShader+'.eccentricity', 0.266)
	cmds.setAttr(glassShader+'.specularRollOff', 0.720)


	for o in objectList:
		if 'glass' in o:
			cmds.sets(o, e=True, forceElement=glassShaderSG)
		else:
			cmds.sets(o, e=True, forceElement=defaultShaderSG)


def getPanelFromCamera(cameraName):
    listPanel=[]
    for panelName in cmds.getPanel( type="modelPanel" ):
        if cmds.modelPanel( panelName,query=True, camera=True) == cameraName:
            listPanel.append( panelName )
    return listPanel


def activateSmoothPreview(model):

	meshes = cmds.listRelatives(model, typ='mesh', ad=True, f=True)
	for m in meshes:
		if 'GES' in m:
			cmds.setAttr(m+'.displaySmoothMesh', 2)
			cmds.setAttr(m+'.smoothLevel', 2)



def setSpinAnim(obj, firstFrame, lastFrame):
		cmds.setKeyframe(obj, at='rotateY', ott='linear', t=firstFrame, v=0)
		cmds.setKeyframe(obj, at='rotateY', itt='linear', t=lastFrame, v=-360)



def getSceneBBoxCenter(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	centerPos = [(rootBBox[0]+rootBBox[3])/2, (rootBBox[1]+rootBBox[4])/2, (rootBBox[2]+rootBBox[5])/2]
	return centerPos
	


def getSceneBBoxScale(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	bBoxSize = [abs(rootBBox[0]-rootBBox[3]), abs(rootBBox[1]-rootBBox[4]), abs(rootBBox[2]-rootBBox[5])]
	bBoxScaleFactor = max(bBoxSize)/4
	return bBoxScaleFactor
