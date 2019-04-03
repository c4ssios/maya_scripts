import maya.cmds as cmds
import maya.mel as mel


lightRigFilePath = '/servers/Home/nleblanc/maya/projects/default/scenes/modelPresentation_lightRig02.ma'
shaderLibFilePath = '/servers/Home/nleblanc/maya/projects/default/scenes/modelPresentation_shaderLib02.ma'


def turntableGenerator(presentationType):
	
	model_root = cmds.ls('root*', typ='transform')

	if len(model_root)<1:
		cmds.warning('No root group detected.')
	if len(model_root)>1:
		cmds.warning('More than one root group detected.')
	if len(model_root)==1:

		scaleFactor = getSceneBBoxScale(model_root)
		modelCenter = getSceneBBoxCenter(model_root)

		'''
		Light Rig Import
		'''
		lightRigShortName = lightRigFilePath.split('/')[-1].split('.')[0]
		cmds.file(lightRigFilePath, i=True, namespace=lightRigShortName)

		lightRigRoot = cmds.ls(lightRigShortName+':root*', typ='transform')
		lightCtrl = cmds.ls(lightRigShortName+':*Aim_CTRL*', typ='transform')

		#add namespaces exists check
		
		'''
		Adjust Rig Scale and Pos
		'''
		cmds.xform(lightRigRoot, absolute=True, translation=[modelCenter[0],cmds.exactWorldBoundingBox(model_root, ignoreInvisible=True)[1],modelCenter[2]], ws=True)
		cmds.scale(scaleFactor,scaleFactor,scaleFactor, lightRigRoot , absolute=True)
		cmds.xform(lightCtrl, absolute=True, translation=modelCenter, ws=True)

		'''
		Shader Lib Import
		'''

		shaderLibShortName = shaderLibFilePath.split('/')[-1].split('.')[0]
		cmds.file(shaderLibFilePath, i=True, namespace=shaderLibShortName)

		'''
		Assign Shader
		'''
		meshes = cmds.listRelatives(model_root, c=True, ad=True, typ='mesh')
		for m in meshes:
			cmds.sets(m, e=True, forceElement=shaderLibShortName+':clay_matSG')

			if 'glass' in m:
				cmds.sets(m, e=True, forceElement=shaderLibShortName+':glass_matSG')
				cmds.setAttr(m+'.aiOpaque', 0)

			if 'White' in m and 'glass' not in m:
				cmds.sets(m, e=True, forceElement=shaderLibShortName+':clayWhite_matSG')

			if 'Black' in m and 'glass' not in m:
				cmds.sets(m, e=True, forceElement=shaderLibShortName+':clayBlack_matSG')

				

		'''
		Create Camera
		'''
		cameraName = lightRigShortName +':'+ 'camera_'+presentationType+'Presentation_CAM'
		cam = cmds.camera()
		cmds.rename(cam[0], cameraName)
		cmds.setAttr(cameraName+'.focalLength', 50)
		cmds.setAttr(cameraName+'.locatorScale', 10*scaleFactor)
		cmds.setAttr(cameraName+'.displayGateMaskColor', 0,0,0, type='double3')
		cmds.setAttr(cameraName+'.displayGateMaskOpacity', 1)
		cmds.xform(cameraName, absolute=True, translation=[0, modelCenter[1]*1.5, scaleFactor*350], ws=True)

		cameraAimLocatorName = lightRigShortName + ':_cameraAim_CTRL'
		cmds.spaceLocator(n=cameraAimLocatorName)
		cmds.aimConstraint(cameraAimLocatorName, cameraName, n=lightRigShortName + ':cameraAimConstraint')
		cmds.setAttr(lightRigShortName + ':cameraAimConstraint.offsetY', -90)
		cmds.xform(cameraAimLocatorName, absolute=True, translation=modelCenter, ws=True)

		mel.eval('setNamedPanelLayout("Single Perspective View")')
		cmds.lookThru( cameraName )


		'''
		Create Turntable Locator
		'''
		locName = lightRigShortName +':locator_'+presentationType+'Presentation_LOC'
		cmds.spaceLocator(n=locName)
		cmds.xform(locName, absolute=True, translation=[modelCenter[0], 0, modelCenter[2]], ws=True)
		cmds.parentConstraint(locName, model_root, maintainOffset=True, n=lightRigShortName +':parentConstraint_'+presentationType+'Presentation_CTR')

		'''
		Turntable Animation
		'''
		setSpinAnim(locName, 1, 101)
		setSpinAnim(lightRigShortName+':lights_GRP', 101, 201)

		'''
		Time Settings
		'''
		cmds.playbackOptions(ast=1, e=True)
		cmds.playbackOptions(aet=201, e=True)
		cmds.playbackOptions(min=1, e=True)
		cmds.playbackOptions(max=201, e=True)


		'''
		Render Settings
		'''
		cmds.setAttr("defaultResolution.width", 1920)
		cmds.setAttr("defaultResolution.height", 1080)
		cmds.setAttr('defaultRenderGlobals.animation', 1)
		cmds.setAttr('defaultRenderGlobals.animationRange', 0)
		cmds.setAttr('defaultRenderGlobals.startFrame', 1)
		cmds.setAttr('defaultRenderGlobals.endFrame', 201)
		cmds.setAttr('defaultRenderGlobals.useFrameExt', 1)
		cmds.setAttr('defaultRenderGlobals.outFormatControl', 2)
		mel.eval('setMayaSoftwareFrameExt("3", 0);')
		cmds.setAttr(cameraName+'.renderable', 1)
		cmds.setAttr('perspShape.renderable', 0)
		cmds.setAttr('frontShape.renderable', 0)
		cmds.setAttr('sideShape.renderable', 0)
		cmds.setAttr('topShape.renderable', 0)

		#MTOA
		cmds.setAttr('defaultArnoldRenderOptions.AASamples', 5)
		cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseSamples', 2)
		cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', 2)




def setSpinAnim(obj, firstFrame, lastFrame):
		cmds.setKeyframe(obj, at='rotateY', ott='linear', t=firstFrame, v=0)
		cmds.setKeyframe(obj, at='rotateY', itt='linear', t=lastFrame, v=360)



def getSceneBBoxCenter(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	centerPos = [(rootBBox[0]+rootBBox[3])/2, (rootBBox[1]+rootBBox[4])/2, (rootBBox[2]+rootBBox[5])/2]
	return centerPos
	


def getSceneBBoxScale(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	bBoxSize = [abs(rootBBox[0]-rootBBox[3]), abs(rootBBox[1]-rootBBox[4]), abs(rootBBox[2]-rootBBox[5])]
	bBoxScaleFactor = max(bBoxSize)/100
	return bBoxScaleFactor
