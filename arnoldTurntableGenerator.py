import maya.cmds as cmds
import maya.mel as mel
import mtoa.utils
from mtoa.core import createOptions

'''
Create Arnold Render Options nodes
'''
createOptions()


'''
Files Path
'''
iblFilePath = '/servers/Departments/LIGHTING/maw/GREG/Turntable/sourceImages/ibl_neutral_rig_01.tx'
cycloGeoFilePath = '/servers/RHS/DEV/nleblanc/dad/turntable/geo/cyclo_v003.abc'
camPropsFilePath = '/servers/RHS/DEV/nleblanc/dad/turntable/geo/props_cam.abc'
macBethFilePath = '/servers/RHS/DEV/nleblanc/dad/turntable/sourceimages/macBeth_1k.tx'


'''
Procedures
'''
def getSceneBBoxCenter(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	centerPos = [(rootBBox[0]+rootBBox[3])/2, (rootBBox[1]+rootBBox[4])/2, (rootBBox[2]+rootBBox[5])/2]
	return centerPos
	


def getSceneBBoxScale(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	bBoxSize = [abs(rootBBox[0]-rootBBox[3]), abs(rootBBox[1]-rootBBox[4]), abs(rootBBox[2]-rootBBox[5])]
	bBoxScaleFactor = max(bBoxSize)
	return bBoxScaleFactor


def setSpinAnim(obj, firstFrame, lastFrame, offset):
		cmds.setKeyframe(obj, at='rotateY', ott='linear', t=firstFrame, v=0 + offset)
		cmds.setKeyframe(obj, at='rotateY', itt='linear', t=lastFrame, v=-360 + offset)


def addArnoldSubdivAttr(mesh, subdLvl, pixelError):
	cmds.setAttr(mesh+'.aiSubdivType', 1)
	cmds.setAttr(mesh+'.aiSubdivIterations', subdLvl)
	cmds.setAttr(mesh+'.aiSubdivAdaptiveMetric', 1)
	cmds.setAttr(mesh+'.aiSubdivPixelError', pixelError)


def arnoldTurntableGenerator():
	meshes = cmds.ls(type='mesh', l=True)

	if len(meshes)<1:
		cmds.warning('No root group detected.')

	else:

		roots = []
		for m in meshes:
		    root = m.split('|')[1]
		    if root not in roots:
		        roots.append(root)


		scaleFactor = getSceneBBoxScale(roots)
		modelCenter = getSceneBBoxCenter(roots)

		cmds.spaceLocator(n='meshesCenter_LOC')
		cmds.xform('meshesCenter_LOC', t=modelCenter)


		'''
		Light Rig Creation
		'''
		mtoa.utils.createLocator("aiSkyDomeLight", asLight=True)
		name = cmds.ls(sl=True)[0]

		skydomeName = 'skyDome_LGT'

		cmds.rename(name, skydomeName)

		cmds.shadingNode( 'file', asTexture=True, n='skydome_file' )
		cmds.connectAttr( 'skydome_file.outColor', skydomeName +'Shape.color' )
		cmds.setAttr('skydome_file.fileTextureName', iblFilePath, type='string')
		cmds.setAttr(skydomeName+'Shape'+'.aiSamples', 2)

		cmds.setAttr(skydomeName+'.rotateY', 180)
		cmds.xform(skydomeName, scale=(scaleFactor, scaleFactor, scaleFactor))


		'''
		Create Cyclo
		'''
		cmds.AbcImport(cycloGeoFilePath)

		rootsYMin = cmds.exactWorldBoundingBox(roots, ignoreInvisible=True)[1]

		cmds.xform("cyclo_GRP", translation=(0, rootsYMin, 0))
		cmds.xform("cyclo_GRP", scale=(scaleFactor, scaleFactor, scaleFactor))


		for mesh in cmds.listRelatives("cyclo_GRP", ad=True, type='mesh', fullPath=True):
			meshes.append(mesh)



		'''
		Create Balls and macBeth
		'''
		cmds.AbcImport(camPropsFilePath)

		for mesh in cmds.listRelatives("propsCam_GRP", ad=True, type='mesh', fullPath=True):
			meshes.append(mesh)
			cmds.setAttr(mesh+'.castsShadows', 0)
			cmds.setAttr(mesh+'.aiVisibleInSpecularReflection', 0)

 

		'''
		Subdivide Mesh
		'''
		subdivSuffixList = ["_GES", "_GED", "_GEV"]

		for suffix in subdivSuffixList:
			subDivMeshes = cmds.ls('*' + suffix + '*', typ='mesh')
			if subDivMeshes >1:
				for m in subDivMeshes:
					addArnoldSubdivAttr(m, 3, 0.5)
			else:
				pass


		'''
		Create Assets Shaders
		'''
		materialList = ["default_MAT", "glass_MAT", "cyclo_MAT", "cameraMatteBalls_MAT", "cameraChromeBalls_MAT", "macBeth_MAT"]

		#Create aiUserDataColor Node
		userDataColorNode = "userDataColor_base"
		cmds.shadingNode('aiUserDataColor', asUtility=True, n=userDataColorNode)
		cmds.setAttr(userDataColorNode+'.attribute', "color", type="string")
		cmds.setAttr(userDataColorNode+'.default', 0.18,0.18,0.18, type="double3")

		for m in materialList:

			shadingGroupName = m+"SG"
			cmds.shadingNode('aiStandardSurface', asShader=True, n=m)
			cmds.sets(name=shadingGroupName, empty=True, renderable=True, noSurfaceShader=True)
			cmds.connectAttr(m+'.outColor', shadingGroupName + '.surfaceShader')


		'''
		Setting Up Materials Attributes
		'''
		#base
		cmds.shadingNode('aiColorJitter', asUtility=True, n='colorJitter_default')
		cmds.connectAttr('colorJitter_default.outColor', 'default_MAT.baseColor')
		cmds.connectAttr(userDataColorNode+'.outColor', 'colorJitter_default.input')
		cmds.select('colorJitter_default', r=True)
		mel.eval("ShowAttributeEditorOrChannelBox;")
		cmds.setAttr('colorJitter_default.typeSwitch', 2)
		cmds.setAttr('colorJitter_default.objGainMin', -0.03)
		cmds.setAttr('colorJitter_default.objGainMax', 0.03)
		cmds.ToggleAttributeEditor()

		cmds.setAttr(materialList[0]+'.specularRoughness', 0.5)
		cmds.setAttr(materialList[0]+'.coatRoughness', 0.2)
		cmds.setAttr(materialList[0]+'.coat', 0.15)

		#glass
		cmds.setAttr(materialList[1]+'.specularIOR', 1.52)
		cmds.setAttr(materialList[1]+'.specularRoughness', 0)
		cmds.setAttr(materialList[1]+'.transmission', 1)
		cmds.setAttr(materialList[1]+'.thinWalled', 1)

		#cyclo
		cmds.setAttr(materialList[2]+'.baseColor', 0.4, 0.4, 0.4, type="double3" )
		cmds.setAttr(materialList[2]+'.specular', 0)

		#cameraMatteBalls
		cmds.setAttr(materialList[3]+'.specular', 0)
		cmds.connectAttr(userDataColorNode+'.outColor', materialList[3]+'.baseColor')

		#cameraChromeBalls
		cmds.setAttr(materialList[4]+'.metalness', 1)
		cmds.setAttr(materialList[4]+'.specularRoughness', 0)

		#macBeth
		cmds.setAttr(materialList[5]+'.specular', 0)
		cmds.shadingNode( 'file', asTexture=True, n='macBeth_file' )
		cmds.connectAttr( 'macBeth_file.outColor', materialList[5]+'.baseColor' )
		cmds.setAttr('macBeth_file.fileTextureName', macBethFilePath, type='string')


		'''
		Assign Shaders and colors
		'''
		for m in meshes:
			#create Arnold Color Attribute
			cmds.addAttr(m, ln="mtoa_constant_color", attributeType="double3")
			cmds.addAttr(m, ln="mtoa_constant_colorX", attributeType="double", p="mtoa_constant_color")
			cmds.addAttr(m, ln="mtoa_constant_colorY", attributeType="double", p="mtoa_constant_color")
			cmds.addAttr(m, ln="mtoa_constant_colorZ", attributeType="double", p="mtoa_constant_color")
			cmds.setAttr(m+'.mtoa_constant_color', 0.18,0.18,0.18,  type="double3")



			#assign default_mat to all meshes
			cmds.sets(m, e=True, forceElement=materialList[0]+"SG")



			#material assignment
			if 'glass' in m:
				cmds.sets(m, e=True, forceElement=materialList[1]+"SG")
				cmds.setAttr(m+'.aiOpaque', 0)

			if 'cyclo' in m:
				cmds.sets(m, e=True, forceElement=materialList[2]+"SG")

			if 'greyBall' in m or 'whiteBall' in m:
				cmds.sets(m, e=True, forceElement=materialList[3]+"SG")

			if 'chromeBall' in m:
				cmds.sets(m, e=True, forceElement=materialList[4]+"SG")

			if 'macBeth' in m:
				cmds.sets(m, e=True, forceElement=materialList[5]+"SG")




			#color set attributes
			if 'Black' in m:
				cmds.setAttr(m+'.mtoa_constant_color', 0.03, 0.03, 0.03,  type="double3")

			if 'White' in m:
				cmds.setAttr(m+'.mtoa_constant_color', 1.0, 1.0, 1.0,  type="double3")






		'''
		Create Camera
		'''
		cameraName = 'camera_turntable_CAM'
		cam = cmds.camera()
		cmds.rename(cam[0], cameraName)
		cmds.setAttr(cameraName+'.focalLength', 100)
		cmds.setAttr(cameraName+'.locatorScale', scaleFactor)
		cmds.setAttr(cameraName+'.displayGateMaskColor', 0,0,0, type='double3')
		cmds.setAttr(cameraName+'.displayGateMaskOpacity', 1)
		cmds.setAttr(cameraName+'.rotateX', -5)

		cmds.setAttr(cameraName+'.displayResolution', 1)

		#Look Through
		mel.eval('setNamedPanelLayout("Single Perspective View")')
		cmds.lookThru(cameraName)


		#Fit View
		cmds.select(roots, r=True)
		cmds.viewFit(f=0.8)
		cmds.select(cl=True)

		cmds.setAttr(cameraName+'.farClipPlane', cmds.getAttr(cameraName+'.centerOfInterest')*10)


		
		'''
		Create Turntable Locator
		'''
		locName = 'locator_turntable_LOC'
		cmds.spaceLocator(n=locName)
		cmds.xform(locName, absolute=True, translation=[modelCenter[0], 0, modelCenter[2]], ws=True)
		for r in roots:
			cmds.parentConstraint(locName, r, maintainOffset=True, n='parentConstraint'+str(roots.index(r))+'_CTR')


		'''
		Turntable Animation
		'''
		setSpinAnim(locName, 1, 51, -45)
		setSpinAnim('skyDome_LGT', 51, 101, 180)

		'''
		Time Settings
		'''
		cmds.playbackOptions(ast=1, e=True)
		cmds.playbackOptions(aet=100, e=True)
		cmds.playbackOptions(min=1, e=True)
		cmds.playbackOptions(max=100, e=True)


		'''
		Render Settings
		'''
		cmds.setAttr("defaultResolution.width", 1920)
		cmds.setAttr("defaultResolution.height", 1080)
		cmds.setAttr('defaultRenderGlobals.animation', 1)
		cmds.setAttr('defaultRenderGlobals.animationRange', 0)
		cmds.setAttr('defaultRenderGlobals.startFrame', 1)
		cmds.setAttr('defaultRenderGlobals.endFrame', 100)
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
		cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseSamples', 3)
		cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', 2)


