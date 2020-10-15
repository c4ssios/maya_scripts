import maya.cmds as cmds
import maya.mel as mel
import mtoa.utils
from mtoa.core import createOptions
import dwpublish_index
import os
import json


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
iblFilePath = '/servers/RHS/DEV/nleblanc/dad/turntable/sourceimages/ibl_neutral_rig_01.tx'
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


def getLatestGeo():
	entity_fields = os.environ.get("WORKSPACE_ENTITIES")
	entity_fields = json.loads(entity_fields)
	entity_data = entity_fields.get("Asset")
	entity_code = entity_data.keys()[0]
	entity = entity_data.get(entity_code).get("fields").get("entity_fields")


	pkg = dwpublish_index.Package.get_package(entity)
	slots = pkg.get_slots_by_type()
	geo = slots.get("Geometry")
	if not len(geo):
	    raise Exception ("No Geometry")
	geo = geo[0]
	geo.load()
	publish_data = geo.link
	filepath = os.path.join(publish_data.get("sg_dw_publish_path"), "GEO.abc")

	cmds.AbcImport(filepath)



def assignShaderAndColor(mesh, defaultMat):

			#create Arnold Color Attribute
			cmds.addAttr(mesh, ln="mtoa_constant_color", attributeType="double3")
			cmds.addAttr(mesh, ln="mtoa_constant_colorX", attributeType="double", p="mtoa_constant_color")
			cmds.addAttr(mesh, ln="mtoa_constant_colorY", attributeType="double", p="mtoa_constant_color")
			cmds.addAttr(mesh, ln="mtoa_constant_colorZ", attributeType="double", p="mtoa_constant_color")
			cmds.setAttr(mesh +'.mtoa_constant_color', 0.18,0.18,0.18,  type="double3")

			#create Arnold Float Attribute for Transmission
			cmds.addAttr(mesh, ln="mtoa_constant_trans", attributeType="double", dv=0)

			#create Arnold Float Attribute for IOR
			cmds.addAttr(mesh, ln="mtoa_constant_IOR", attributeType="double", dv=1.52)


			#assign default_mat to all meshes
			cmds.sets(mesh, e=True, forceElement=defaultMat+"SG")


			#material assignment
			objectShortName = mesh.split('|')[-1]
			shapeSplitName = objectShortName.split('_')

			if len(shapeSplitName)!=4:
				pass

			else:

				#Assets materials

				if 'glass' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="glass_MAT"+"SG")
					cmds.setAttr(mesh+'.aiOpaque', 0)

				if 'metal' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="metal_MAT"+"SG")

				if 'paint' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="paint_MAT"+"SG")

				if 'rubber' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="rubber_MAT"+"SG")

				if 'skin' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="skin_MAT"+"SG")

				if 'cloth' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="cloth_MAT"+"SG")

				if 'hair' in shapeSplitName[0]:
					cmds.sets(mesh, e=True, forceElement="hair_MAT"+"SG")

				if 'sclera' in objectShortName.lower():
					cmds.sets(mesh, e=True, forceElement="sclera_MAT"+"SG")



				#Mesh light
				if 'light' in shapeSplitName[0]:
					meshTransform = cmds.listRelatives(mesh, p=True, type='transform')[0]
					cmds.select(meshTransform, r=True)
					mtoa.utils.createMeshLight()
					meshLightName = 'light_' + meshTransform
					cmds.setAttr(meshLightName+'.lightVisible', 1)
					cmds.setAttr(meshLightName+'.aiNormalize', 0)
					cmds.select(cl=True)



				#Turntable elements materials

				if 'cyclo' in shapeSplitName[2]:
					cmds.sets(mesh, e=True, forceElement="cyclo_MAT"+"SG")

				if 'greyBall' in shapeSplitName[2] or 'whiteBall' in shapeSplitName[3]:
					cmds.sets(mesh, e=True, forceElement="cameraMatteBalls_MAT"+"SG")

				if 'chromeBall' in shapeSplitName[2]:
					cmds.sets(mesh, e=True, forceElement="cameraChromeBalls_MAT"+"SG")

				if 'macBeth' in shapeSplitName[2]:
					cmds.sets(mesh, e=True, forceElement="macBeth_MAT"+"SG")




			#color set attributes
			if 'Black' in shapeSplitName[0]:
				cmds.setAttr(mesh +'.mtoa_constant_color', 0.03, 0.03, 0.03,  type="double3")

			if 'White' in shapeSplitName[0]:
				cmds.setAttr(mesh +'.mtoa_constant_color', 1.0, 1.0, 1.0,  type="double3")

			#Transmission set Attributes
			if 'Clear' in shapeSplitName[0]:
				cmds.setAttr(mesh +'.mtoa_constant_trans', 1)

			#IOR set attributes
			if 'cornea' in objectShortName.lower():
				cmds.setAttr(mesh +'.mtoa_constant_IOR', 1.336)




def arnoldTurntableGenerator():

	#getLatestGeo()


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

		skydomeName = 'skyDome_LGT'


		'''
		Create Dad model scale reference
		'''
		cmds.group( em=True, name='dadRoot_GRP' )
		cmds.AbcImport(dadGeoFilePath, rpr='dadRoot_GRP')
		for mesh in cmds.listRelatives("dadRoot_GRP", ad=True, type='mesh', fullPath=True):
			meshes.append(mesh)
			cmds.setAttr(mesh+'.aiVisibleInSpecularReflection', 0)
			cmds.setAttr(mesh+'.aiVisibleInDiffuseReflection', 0)


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
			subDivMeshes = cmds.ls('*' + suffix + '*', typ='mesh', l=True)
			if len(subDivMeshes) >1:
				for m in subDivMeshes:
					addArnoldSubdivAttr(m, 3, 0.5)
			else:
				pass

		'''
		Non renderable mesh
		'''
		nonRenderableMeshes = cmds.ls('*_PLY*', typ='mesh', l=True)
		if len(nonRenderableMeshes)>1:
			for m in nonRenderableMeshes:
				if '_PLY' in m:
					cmds.setAttr(m+'.primaryVisibility', 0)
					cmds.setAttr(m+'.castsShadows', 0)
					cmds.setAttr(m+'.aiVisibleInDiffuseReflection', 0)
					cmds.setAttr(m+'.aiVisibleInSpecularReflection', 0)
					cmds.setAttr(m+'.aiVisibleInDiffuseTransmission', 0)
					cmds.setAttr(m+'.aiVisibleInSpecularTransmission', 0)
					cmds.setAttr(m+'.aiVisibleInVolume', 0)
					cmds.setAttr(m+'.aiSelfShadows', 0)

		else:
			pass


		'''
		Create Assets Shaders
		'''
		materialList = ["default_MAT", "glass_MAT", "cyclo_MAT", "cameraMatteBalls_MAT", "cameraChromeBalls_MAT", "macBeth_MAT", "metal_MAT", "paint_MAT", "rubber_MAT", "skin_MAT", "cloth_MAT", "hair_MAT", "sclera_MAT"]

		#Create aiUserDataColor Node
		userDataColorNode = "userDataColor_base"
		cmds.shadingNode('aiUserDataColor', asUtility=True, n=userDataColorNode)
		cmds.setAttr(userDataColorNode+'.attribute', "color", type="string")
		cmds.setAttr(userDataColorNode+'.default', 0.18,0.18,0.18, type="double3")

		#Create aiUserDataFloat Node for transmissiom
		userDataFloatTrans = "userDataFloat_trans"
		cmds.shadingNode('aiUserDataFloat', asUtility=True, n=userDataFloatTrans)
		cmds.setAttr(userDataFloatTrans+'.attribute', "trans", type="string")
		cmds.setAttr(userDataFloatTrans+'.default', 0)

		#Create aiUserDataFloat Node for IOR
		userDataFloatIOR = "userDataFloat_IOR"
		cmds.shadingNode('aiUserDataFloat', asUtility=True, n=userDataFloatIOR)
		cmds.setAttr(userDataFloatIOR+'.attribute', "IOR", type="string")
		cmds.setAttr(userDataFloatIOR+'.default', 1.52)




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
		cmds.connectAttr('colorJitter_default.outColor', 'glass_MAT.baseColor')
		cmds.setAttr('glass_MAT'+'.specularIOR', 1.52)
		cmds.setAttr('glass_MAT'+'.specularRoughness', 0)
		cmds.setAttr('glass_MAT'+'.transmission', 1)
		cmds.setAttr('glass_MAT'+'.thinWalled', 1)
		cmds.connectAttr(userDataFloatTrans+'.outValue', 'glass_MAT'+'.transmission')
		cmds.connectAttr(userDataFloatIOR+'.outValue', 'glass_MAT'+'.specularIOR')

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

		#skin
		cmds.setAttr('skin_MAT'+'.base', 0)
		cmds.setAttr('skin_MAT'+'.specularRoughness', 0.4)
		cmds.setAttr('skin_MAT'+'.specularIOR', 1.330)
		cmds.setAttr('skin_MAT'+'.subsurface', 1)
		cmds.setAttr('skin_MAT'+'.subsurfaceScale', 0.1)
		cmds.setAttr('skin_MAT'+'.subsurfaceColor', 0.4, 0.4, 0.4, type="double3")
		cmds.setAttr('skin_MAT'+'.subsurfaceRadius', 0.25, 0.25, 0.25, type="double3")
		cmds.shadingNode('aiColorCorrect', asUtility=True, n='skinColor_colorCorrect')
		cmds.connectAttr('colorJitter_default.outColor', 'skinColor_colorCorrect.input')
		cmds.connectAttr('skinColor_colorCorrect.outColor', 'skin_MAT.subsurfaceColor')
		cmds.setAttr("skinColor_colorCorrect.gamma", 1.6)
		cmds.setAttr("skinColor_colorCorrect.contrast", 1.5)


		#cloth
		cmds.connectAttr('colorJitter_default.outColor', 'cloth_MAT.baseColor')
		cmds.setAttr('cloth_MAT'+'.specular', 0.5)
		cmds.setAttr('cloth_MAT'+'.specularRoughness', 0.6)
		cmds.setAttr('cloth_MAT'+'.sheen', 0.5)

		#hair
		cmds.setAttr('hair_MAT'+'.base', 0.2)
		cmds.setAttr('hair_MAT'+'.baseColor', 0.18, 0.18, 0.18, type="double3" )
		cmds.setAttr('hair_MAT'+'.specular', 0.1)
		cmds.setAttr('hair_MAT'+'.specularRoughness', 0.45)
		cmds.setAttr('hair_MAT'+'.sheen', 0.5)
		cmds.setAttr('hair_MAT'+'.sheenRoughness', 0.2)

		#sclera
		#gradient Color
		cmds.shadingNode('ramp', asTexture=True, n='rampColor_sclera')
		cmds.shadingNode('place2dTexture', asUtility=True, n='place2dTextureColor_sclera')
		cmds.connectAttr('place2dTextureColor_sclera.outUV', 'rampColor_sclera.uvCoord')
		cmds.connectAttr('place2dTextureColor_sclera.outUvFilterSize', 'rampColor_sclera.uvFilterSize')
		cmds.setAttr("rampColor_sclera.colorEntryList[0].position", 0.0)
		cmds.setAttr("rampColor_sclera.colorEntryList[0].color", 0, 0, 0, type='double3')
		cmds.setAttr("rampColor_sclera.colorEntryList[1].position", 0.2)
		cmds.setAttr("rampColor_sclera.colorEntryList[1].color", 0.18, 0.18, 0.18, type='double3')
		cmds.setAttr("rampColor_sclera.colorEntryList[2].position", 0.5)
		cmds.setAttr("rampColor_sclera.colorEntryList[2].color", 0.8, 0.8, 0.8, type='double3')
		cmds.setAttr("rampColor_sclera.interpolation", 0)
		cmds.connectAttr('rampColor_sclera.outColor', 'sclera_MAT.baseColor')

		cmds.setAttr('sclera_MAT'+'.specular', 0)




		'''
		Assign Shaders and colors
		'''
		for m in meshes:
			assignShaderAndColor(m, materialList[0])


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
		cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseSamples', 2)
		cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', 2)
		cmds.setAttr('defaultArnoldRenderOptions.GISssSamples', 6)


