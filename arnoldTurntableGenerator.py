import maya.cmds as cmds
import maya.mel as mel
import mtoa.utils
from mtoa.core import createOptions


"""
Load MTOA plugin if not present
"""
if cmds.renderer("arnold", exists=True)==0:
	cmds.loadPlugin("mtoa.so")


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
dadGeoFilePath = '/servers/RHS/DEV/nleblanc/dad/turntable/geo/dad_v001.abc'


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


def getSceneXZBBoxScale(model):
	rootBBox = cmds.exactWorldBoundingBox(model, ignoreInvisible=True)
	XZbBoxSize = [abs(rootBBox[0]-rootBBox[3]), abs(rootBBox[2]-rootBBox[5])]
	XZbBoxScaleFactor = max(XZbBoxSize)
	return XZbBoxScaleFactor


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

		cmds.shadingNode('file', asTexture=True, n='skydome_file')
		cmds.shadingNode('aiColorCorrect', asUtility=True, n='skydome_colorCorrect')
		cmds.connectAttr('skydome_file.outColor', 'skydome_colorCorrect.input')
		cmds.connectAttr('skydome_colorCorrect.outColor', skydomeName +'Shape.color' )

		cmds.setAttr('skydome_file.fileTextureName', iblFilePath, type='string')
		cmds.setAttr('skydome_colorCorrect.saturation', 0)
		cmds.setAttr(skydomeName+'Shape'+'.aiSamples', 2)

		cmds.setAttr(skydomeName+'.rotateY', 180)
		cmds.xform(skydomeName, scale=(scaleFactor, scaleFactor, scaleFactor))


		'''
		Create Cyclo
		'''
		cmds.group( em=True, name='cycloRoot_GRP' )
		cmds.AbcImport(cycloGeoFilePath, rpr='cycloRoot_GRP')

		rootsYMin = cmds.exactWorldBoundingBox(roots, ignoreInvisible=True)[1]

		cmds.xform("cyclo_GRP", translation=(0, rootsYMin, 0))
		cmds.xform("cyclo_GRP", scale=(scaleFactor, scaleFactor, scaleFactor))


		for mesh in cmds.listRelatives("cycloRoot_GRP", ad=True, type='mesh', fullPath=True):
			meshes.append(mesh)


		'''
		Create Dad model scale reference
		'''
		cmds.group( em=True, name='dadRoot_GRP' )
		cmds.AbcImport(dadGeoFilePath, rpr='dadRoot_GRP')
		for mesh in cmds.listRelatives("dadRoot_GRP", ad=True, type='mesh', fullPath=True):
			meshes.append(mesh)

		dadXOffset = ((getSceneXZBBoxScale(roots)/2)+abs(cmds.exactWorldBoundingBox("dadRoot_GRP")[0]-cmds.exactWorldBoundingBox("dadRoot_GRP")[3])/2)*1.2
		cmds.xform("dadRoot_GRP", absolute=True, t=[dadXOffset, rootsYMin, 0])

		cmds.duplicate('dadRoot_GRP', n='temp_dadRoot_GRP')
		dadXOffset2 = (-(getSceneXZBBoxScale(roots)/2)-abs(cmds.exactWorldBoundingBox("dadRoot_GRP")[0]-cmds.exactWorldBoundingBox("dadRoot_GRP")[3])/2)*1.2
		cmds.xform("temp_dadRoot_GRP", absolute=True, t=[dadXOffset2, rootsYMin, 0])

		cmds.setAttr("dadRoot_GRP"+".ty", lock=True)
		cmds.setAttr("dadRoot_GRP"+".tz", lock=True)
		cmds.setAttr("dadRoot_GRP"+".rx", lock=True)
		cmds.setAttr("dadRoot_GRP"+".ry", lock=True)
		cmds.setAttr("dadRoot_GRP"+".rz", lock=True)
		cmds.setAttr("dadRoot_GRP"+".sx", lock=True)
		cmds.setAttr("dadRoot_GRP"+".sy", lock=True)
		cmds.setAttr("dadRoot_GRP"+".sz", lock=True)



		'''
		Create Balls and macBeth
		'''
		cmds.group( em=True, name='propsCamRoot_GRP' )
		cmds.AbcImport(camPropsFilePath, rpr='propsCamRoot_GRP')

		for mesh in cmds.listRelatives("propsCamRoot_GRP", ad=True, type='mesh', fullPath=True):
			meshes.append(mesh)
			cmds.setAttr(mesh+'.castsShadows', 0)
			cmds.setAttr(mesh+'.aiVisibleInSpecularReflection', 0)
			cmds.setAttr(mesh+'.aiVisibleInDiffuseReflection', 0)
			cmds.setAttr(mesh+'.aiVisibleInDiffuseTransmission', 0)
			cmds.setAttr(mesh+'.aiVisibleInSpecularTransmission', 0)
			cmds.setAttr(mesh+'.aiVisibleInVolume', 0)
			cmds.setAttr(mesh+'.aiSelfShadows', 0)

		cmds.xform('propsCamRoot_GRP', relative=True, t=[-2.8, 1.3, -19.5])
			
 
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
		materialList = ["default_MAT", "glass_MAT", "cyclo_MAT", "cameraMatteBalls_MAT", "cameraChromeBalls_MAT", "macBeth_MAT", "metal_MAT", "paint_MAT", "rubber_MAT"]

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

		cmds.setAttr('default_MAT'+'.specularRoughness', 0.5)
		cmds.setAttr('default_MAT'+'.coatRoughness', 0.2)
		cmds.setAttr('default_MAT'+'.coat', 0.15)

		#glass
		cmds.setAttr('glass_MAT'+'.specularIOR', 1.52)
		cmds.setAttr('glass_MAT'+'.specularRoughness', 0)
		cmds.setAttr('glass_MAT'+'.transmission', 1)
		cmds.setAttr('glass_MAT'+'.thinWalled', 1)

		#cyclo
		cmds.setAttr('cyclo_MAT'+'.baseColor', 0.4, 0.4, 0.4, type="double3" )
		cmds.setAttr('cyclo_MAT'+'.specular', 0)

		#cameraMatteBalls
		cmds.setAttr('cameraMatteBalls_MAT'+'.specularRoughness', 0.6)
		cmds.connectAttr(userDataColorNode+'.outColor', 'cameraMatteBalls_MAT'+'.baseColor')

		#cameraChromeBalls
		cmds.setAttr('cameraChromeBalls_MAT'+'.baseColor', 0.65, 0.65, 0.65, type="double3" )
		cmds.setAttr('cameraChromeBalls_MAT'+'.metalness', 1)
		cmds.setAttr('cameraChromeBalls_MAT'+'.specularRoughness', 0)

		#macBeth
		cmds.setAttr('macBeth_MAT'+'.base', 1)
		cmds.setAttr('macBeth_MAT'+'.specular', 0)
		cmds.shadingNode( 'file', asTexture=True, n='macBeth_file' )
		cmds.connectAttr( 'macBeth_file.outColor', materialList[5]+'.baseColor' )
		cmds.setAttr('macBeth_file.fileTextureName', macBethFilePath, type='string')

		#metal
		cmds.setAttr('metal_MAT'+'.metalness', 1)
		cmds.setAttr('metal_MAT'+'.specularRoughness', 0.35)
		cmds.shadingNode('aiColorCorrect', asUtility=True, n='metalColor_colorCorrect')
		cmds.connectAttr('colorJitter_default.outColor', 'metalColor_colorCorrect.input')
		cmds.connectAttr('metalColor_colorCorrect.outColor', 'metal_MAT.baseColor')
		cmds.setAttr('metalColor_colorCorrect.exposure', 0.5)

		#paint
		cmds.connectAttr('colorJitter_default.outColor', 'paint_MAT.baseColor')
		cmds.setAttr('paint_MAT'+'.specularRoughness', 0.4)
		cmds.setAttr('paint_MAT'+'.coat', 0.4)
		cmds.setAttr('paint_MAT'+'.coatRoughness', 0.05)

		#rubber
		cmds.connectAttr('colorJitter_default.outColor', 'rubber_MAT.baseColor')
		cmds.setAttr('rubber_MAT'+'.diffuseRoughness', 1)
		cmds.setAttr('rubber_MAT'+'.specularRoughness', 0.6)
		cmds.setAttr('rubber_MAT'+'.specular', 0.5)


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

			objectShortName = m.split('|')[-1]
			shapeSplitName = objectShortName.split('_')

			if len(shapeSplitName)!=4:
				pass

			else:

				#Assets materials

				if 'glass' in shapeSplitName[0]:
					cmds.sets(m, e=True, forceElement="glass_MAT"+"SG")
					cmds.setAttr(m+'.aiOpaque', 0)

				if 'metal' in shapeSplitName[0]:
					cmds.sets(m, e=True, forceElement="metal_MAT"+"SG")

				if 'paint' in shapeSplitName[0]:
					cmds.sets(m, e=True, forceElement="paint_MAT"+"SG")

				if 'rubber' in shapeSplitName[0]:
					cmds.sets(m, e=True, forceElement="rubber_MAT"+"SG")


				#Mesh light
				if 'light' in shapeSplitName[0]:
					meshTransform = cmds.listRelatives(m, p=True, type='transform')[0]
					cmds.select(meshTransform, r=True)
					mtoa.utils.createMeshLight()
					meshLightName = 'light_' + meshTransform
					cmds.setAttr(meshLightName+'.lightVisible', 1)
					cmds.setAttr(meshLightName+'.aiNormalize', 0)
					cmds.select(cl=True)



				#Turntable elements materials

				if 'cyclo' in shapeSplitName[2]:
					cmds.sets(m, e=True, forceElement="cyclo_MAT"+"SG")

				if 'greyBall' in shapeSplitName[2] or 'whiteBall' in shapeSplitName[3]:
					cmds.sets(m, e=True, forceElement="cameraMatteBalls_MAT"+"SG")

				if 'chromeBall' in shapeSplitName[2]:
					cmds.sets(m, e=True, forceElement="cameraChromeBalls_MAT"+"SG")

				if 'macBeth' in shapeSplitName[2]:
					cmds.sets(m, e=True, forceElement="macBeth_MAT"+"SG")




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
		cmds.setAttr(cameraName+'.displayResolution', 1)


		cmds.parentConstraint(cameraName, 'propsCamRoot_GRP', maintainOffset=True, n='propsCam_parentConstraint')

		'''
		Place Camera
		'''
		cmds.setAttr(cameraName+'.rotateX', -5)

		#Look Through
		mel.eval('setNamedPanelLayout("Single Perspective View")')
		cmds.lookThru(cameraName)


		#Fit View
		cmds.select(roots, r=True)
		cmds.select("dadRoot_GRP", add=True)
		cmds.select("temp_dadRoot_GRP", add=True)
		cmds.viewFit(f=0.9)
		cmds.select(cl=True)

		cmds.setAttr(cameraName+'.farClipPlane', cmds.getAttr(cameraName+'.centerOfInterest')*10)

		cmds.setAttr(cameraName+".tx", lock=True)
		cmds.setAttr(cameraName+".ry", lock=True)
		cmds.setAttr(cameraName+".rz", lock=True)
		cmds.setAttr(cameraName+".sx", lock=True)
		cmds.setAttr(cameraName+".sy", lock=True)
		cmds.setAttr(cameraName+".sz", lock=True)


		cmds.delete("temp_dadRoot_GRP")
		
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
		cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', 3)


