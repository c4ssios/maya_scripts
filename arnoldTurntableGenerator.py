import maya.cmds as cmds
import maya.mel as mel
import mtoa.utils
from mtoa.core import createOptions

createOptions()



iblFilePath = '/servers/Departments/LIGHTING/maw/GREG/Turntable/sourceImages/ibl_neutral_rig_01.tx'

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
	#print mesh + ' attributes set succesfully.'



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
		cmds.xform('meshesCenter_LOC', t=getSceneBBoxCenter(roots))


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
		Create Assets Shaders
		'''
		materialList = ["default_MAT", "glass_MAT"]

		for m in materialList:

			shadingGroupName = m+"SG"
			cmds.shadingNode('aiStandardSurface', asShader=True, n=m)
			cmds.sets(name=shadingGroupName, empty=True, renderable=True, noSurfaceShader=True)
			cmds.connectAttr(m+'.outColor', shadingGroupName + '.surfaceShader')


		'''
		Setting Up Base Material Attributes
		'''
		cmds.shadingNode('aiColorJitter', asUtility=True, n='colorJitter_default')
		cmds.connectAttr('colorJitter_default.outColor', 'default_MAT.baseColor')
		cmds.select('colorJitter_default', r=True)
		mel.eval("ShowAttributeEditorOrChannelBox;")
		cmds.setAttr('colorJitter_default.typeSwitch', 2)
		cmds.setAttr('colorJitter_default.objGainMin', -0.03)
		cmds.setAttr('colorJitter_default.objGainMax', 0.03)
		cmds.setAttr('colorJitter_default.input', 0.18,0.18,0.18, type="double3")
		cmds.ToggleAttributeEditor()

		cmds.setAttr(materialList[0]+'.specularRoughness', 0.5)
		cmds.setAttr(materialList[0]+'.coatRoughness', 0.2)
		cmds.setAttr(materialList[0]+'.coat', 0.25)


		'''
		Setting Up Glass Material Attributes
		'''

		cmds.setAttr(materialList[1]+'.specularIOR', 1.52)
		cmds.setAttr(materialList[1]+'.specularRougness', 0)
		cmds.setAttr(materialList[1]+'.transmission', 1)
		cmds.setAttr(materialList[1]+'.thinWalled', 1)


		'''
		Assign Shaders
		'''
		for m in meshes:
			cmds.sets(m, e=True, forceElement=materialList[0]+"SG")

			if 'glass' in m:
				cmds.sets(m, e=True, forceElement=materialList[1]+"SG")
				cmds.setAttr(m+'.aiOpaque', 0)



		'''
		Create Ground
		'''
		groundName = "defaultColour_C_ground0001_GEP"
		cmds.polyPlane(n=groundName)
		cmds.delete(groundName, ch=True)

		rootsYMin = cmds.exactWorldBoundingBox(roots, ignoreInvisible=True)[1]

		cmds.xform("defaultColour_C_ground0001_GEP", translation=(0, rootsYMin, 0))
		cmds.xform("defaultColour_C_ground0001_GEP", scale=(scaleFactor*10, scaleFactor*10, scaleFactor*10))

		groundMaterialName = 'ground_MAT'
		cmds.shadingNode('aiShadowMatte', asShader=True, n=groundMaterialName)
		cmds.sets(name=groundMaterialName+'SG', empty=True, renderable=True, noSurfaceShader=True)
		cmds.connectAttr(groundMaterialName+'.outColor', groundMaterialName+ 'SG' + '.surfaceShader')
		cmds.sets('defaultColour_C_ground0001_GEP', e=True, forceElement=groundMaterialName+'SG')


		'''
		Create Camera
		'''
		cameraName = 'camera_turntable_CAM'
		cam = cmds.camera()
		cmds.rename(cam[0], cameraName)
		cmds.setAttr(cameraName+'.focalLength', 50)
		cmds.setAttr(cameraName+'.locatorScale', scaleFactor)
		cmds.setAttr(cameraName+'.displayGateMaskColor', 0,0,0, type='double3')
		cmds.setAttr(cameraName+'.displayGateMaskOpacity', 1)
		cmds.setAttr(cameraName+'.rotateX', -10)

		cmds.setAttr(cameraName+'.displayResolution', 1)
		#cmds.setAttr(cameraName+'.overscan', 1.3)

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


