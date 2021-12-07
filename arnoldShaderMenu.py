"""
Registers a layered menu for the Node Graph, which shows the names of available
Arnold shaders and creates an ArnoldShadingNode node with the chosen shader set
on it when one of the menu entries is chosen.
"""
import os

from Katana import NodegraphAPI, RenderingAPI, LayeredMenuAPI

import luma_katana.constants
import luma_katana.shading


# Non-core shaders that we still want to include in the layered menu.
NON_CORE_SHADER_WHITELIST = frozenset((
    'luma_ramp_float',
    'luma_ramp_rgb',
    'luma_remap_hsv',
    'luma_remap_rgb',
    'luma_luminance',
    'luma_luminance_mix_surface',
))


def PopulateCallback(menuInstance):
    """
    Callback for the layered menu, which adds entries to the given layered menu
    based on the available Arnold shaders.
    """
    infoPlugin = RenderingAPI.RenderPlugins.GetInfoPlugin('arnold')
    kShaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
    ktoaRoot = os.environ['REZ_KTOA_ROOT']

    for shaderName in infoPlugin.getRendererObjectNames(kShaderType):
        shaderInfo = infoPlugin.getRendererObjectInfo(shaderName, kShaderType)
        shaderPath = shaderInfo.getFullPath()
        if shaderName in NON_CORE_SHADER_WHITELIST \
                or shaderPath.startswith(ktoaRoot) \
                or os.path.splitext(shaderPath)[1] in ('.osl', '.oso'):
            color = luma_katana.shading.getShadingNodeTypeColor(shaderName)
            menuInstance.addEntry(shaderName, text=shaderName, color=color)


def ActionCallback(value):
    """
    Callback for when an item is selected from the layered menu.

    Creates an ArnoldShadingNode node and sets its 'nodeType' parameter to the
    given value (i.e. the shader type name).
    """
    node = NodegraphAPI.CreateNode('ArnoldShadingNode')
    node.getParameter('nodeType').setValue(value, 0)
    node.setName(value)
    node.getParameter('name').setValue(node.getName(), 0)
    node.checkDynamicParameters()
    return node


# Only register the layered menu if arnold is available
if 'arnold' in luma_katana.constants.RENDERER_VERSION_STRINGS:
    layeredMenu = LayeredMenuAPI.LayeredMenu(PopulateCallback, ActionCallback,
                                             'Ctrl+1', alwaysPopulate=False,
                                             onlyMatchWordStart=False)
    LayeredMenuAPI.RegisterLayeredMenu(layeredMenu, 'arnoldShaders')
