from __future__ import print_function

import datetime
import enum
import logging
import re
from builtins import next
from typing import TYPE_CHECKING

from kids.cache import cache

import DrawingModule
import NodegraphAPI
from Katana import KatanaFile, Utils

import katanalib.nodes
from katanalib.app import KATANA_API_VERSION
from katanalib.utils import convertToNative
from pylib.compat import string_types

import luma.depend
import luma.filepath as filepath
import luma.helpers
import luma_katana.utils as utils
from luma_ftrack.api.publishing import asyncPublish
from luma_katana.constants import USD_LOOKFILE_FORMAT_DISPLAY_NAME

if KATANA_API_VERSION >= (4, 0):
    import LookFileBakeAPI.Constants as LookFileConstants  # isort:skip
else:
    from Nodes3DAPI import LookFileConstants  # isort:skip


if TYPE_CHECKING:
    from typing import *

    import PyFnGeolib as Geolib
    import PyFnGeolibProducers as GeolibProducers
    import PyFnScenegraphAttr as ScenegraphAttr

    import sequences

    import luma.render.jobs.interface
    import luma.render.managers
    import luma_deadline.manager
    import luma_katana.ui.pyqt


_logger = luma.helpers.getLumaLogger(__name__)

# This needs to match: [house, house_Roof, PRF_000_1420_CeilingDebris_debris]
SHADER_ASSET_RE = re.compile(
    filepath.Token.types['shot'].wrappedRegex + '_*(?P<descriptor>.*)')
# Kinds that are allowed to be the model root of a shader export
# FIXME: We probably want to remove 'group' as I think that was just a
#  workaround for assemblies and we may use group more later to be in compliance
#  with model hierarchy.
MODEL_ROOT_KINDS = ('component', 'assembly', 'group')

# FIXME: in Arnold-5: generate list of surface nodes by looking for CLOSURE outputs?
ARNOLD_SHADING_NODE_TYPES = [
    ('bump', lambda x: 'bump' in x.lower()),
    ('surface', lambda x: x in {
        'hair',
        'alSurface',
        'standard',
        'standard_surface',
        'standard_volume',
        'hair_marschner',
        'MayaSurfaceShader'
    }),
    ('pattern', lambda x: x in {
        'noise',
        'cell_noise',
        'checkerboard',
        'ramp_rgb',
        'BA_texture3d_warp',
        'BA_texture_cell3d3',
        'BA_texture_fractal4d3',
        'BA_texture_oily_specular2',
        'alCel',
        'alCellNoise',
        'alFlake',
        'alFlowNoise',
        'alFractal',
        'alPattern',
        'MayaFluidTexture2D',
        'MayaFractal',
        'MayaBrownian',
        'MayaStucco',
        'MayaGrid',
        'MayaSolidFractal',
        'MayaRampKatana',
    }),
    ('image', lambda x: x in {
        'image',
        'MayaFile',
    }),
    ('aov', lambda x: x.startswith('aov')),
]

ARNOLD_SHADING_NODE_COLORS = {
    'bump': (.178, .269, .434),  # Blue
    'surface': (.395, .250, .380),  # Fusia
    'pattern': (.27, .19, .46),  # Purple
    'aov': (.146, .460, .344),  # Green
    'image': (.648, .255, .189),  # Orange
    'default': (.365, .301, .179),  # Yellow
    'warning': (.45, .25, .25),  # Red (not used yet)
}

ARNOLD_PORT_TO_BREAKOUT_NAME = {
    'out.r': 'RED',
    'out.g': 'GREEN',
    'out.b': 'BLUE',
    'out.a': 'ALPHA',
    'out.x': 'X',
    'out.y': 'Y',
    'out.z': 'Z',
}

_shadingNodeColorCache = {}  # type: Dict[str, Tuple[float, float, float]]


def getShadingNodeTypeColor(nodeType):
    # type: (str) -> Tuple[float, float, float]
    """
    Given a shading node type name, return an RGB color to use in the node graph
    as a three-tuple of floats.

    Parameters
    ----------
    nodeType : str
        The shading node type name, as found in an ArnoldShadingNode's
        'nodeType' parameter.

    Returns
    -------
    Tuple[float, float, float]
    """
    try:
        return _shadingNodeColorCache[nodeType]
    except KeyError:
        pass
    for category, shouldColor in ARNOLD_SHADING_NODE_TYPES:
        if shouldColor(nodeType):
            break
    else:
        category = 'default'
    color = ARNOLD_SHADING_NODE_COLORS[category]
    _shadingNodeColorCache[nodeType] = color
    return color


def setShadingNodeColor(node, force=False):
    # type: (NodegraphAPI.Node, bool) -> None
    """
    Color an ArnoldShadingNode based on its node type.

    Parameters
    ----------
    node : NodegraphAPI.Node
    force : bool
        Only color if the node has no color already.
    """
    if force or DrawingModule.GetCustomNodeColor(node) is None:
        value = node.getParameterValue('nodeType', 0)
        if value:
            color = getShadingNodeTypeColor(value)
            DrawingModule.SetCustomNodeColor(node, *color)


def pathToNodeName(path):
    # type: (Union[str, filepath.PathType]) -> str
    """
    Convert a path string to a representative name for a shading node.

    Parameters
    ----------
    path : Union[str, filepath.PathType]

    Returns
    -------
    str
    """
    if not isinstance(path, filepath.LumaPath):
        path = filepath.Path(path.replace('<udim>.', '').replace('<UDIM>.', ''))
    try:
        tokens = path.tokenizeFilename()[-1]
    except Exception:
        return path.namebase
    return '{shot}_{element}{descriptor}_{version}_{pass_}_{extension}'.format(
        **tokens)


def loadTextures(path, extensions=('tx', 'exr'), maxDepth=1, group=None):
    # type: (Union[str, filepath.PathType], Union[str, Sequence[str]], int, Optional[NodegraphAPI.GroupNode]) -> List[NodegraphAPI.Node]
    """
    Finds all sequences and files matching the given pattern under the given
    path and creates an 'image' shading node for each.

    Parameters
    ----------
    path : Union[str, filepath.PathType]
    extensions : Union[str, Sequence[str]]
        When `path` is a directory, this controls which file extensions to
        search for under that directory. Note that this is also an extension
        priority order, so if two paths are found whose names are identical
        aside from the extension, the path whose extension appears first in this
        sequence will be loaded, and any others will be skipped.

        This value has no effect if `path` is a file or sequence path.
    maxDepth : int
        When `path` is a directory, this controls the maximum depth to traverse
        below it looking for texture paths.
    group : Optional[NodegraphAPI.GroupNode]
        The parent group for the shading nodes. If None, the root will be used.

    Returns
    -------
    List[NodegraphAPI.Node]
        The created shading nodes
    """
    if not isinstance(path, (filepath.Path, filepath.FileSequence)):
        path = filepath.Filepath(path)

    path = path.realpath()
    if not path.exists():
        raise ValueError('Nonexistent path: {0}'.format(path))

    if group is None:
        group = NodegraphAPI.GetRootNode()
    elif not isinstance(group, NodegraphAPI.GroupNode):
        raise TypeError('A GroupNode is required')

    txtrPaths = []  # type: List[filepath.PathType]
    if isinstance(path, filepath.FileSequence) or path.isfile():
        txtrPaths.append(path)
    else:
        if isinstance(extensions, string_types):
            extensions = (extensions,)
        pattern = re.compile('^[^._].+\.(?:%s)$' % (
            '|'.join(e.strip('. ') for e in extensions)))
        pathIter = path.walkSequencesAndFiles(pattern=pattern,
                                              allowSingleFrameSeqs=True,
                                              maxDepth=maxDepth, prune='_backup')

        pathTuples = []  # type: List[Tuple[int, str, filepath.PathType]]
        for rawPath in pathIter:
            basePath, ext = rawPath.splitext()
            pathTuples.append((extensions.index(ext.strip('.')), str(basePath),
                               rawPath))
        pathTuples.sort()

        # Remove duplicates based on extension ordering
        seenBasePaths = set()  # type: Set[str]
        for _, base, rawPath in pathTuples:
            if base in seenBasePaths:
                continue
            seenBasePaths.add(base)
            txtrPaths.append(rawPath)

    if not txtrPaths:
        return []

    createdNodes = []
    for txtrPath in txtrPaths:
        if isinstance(txtrPath, filepath.FileSequence):
            if txtrPath.isValid():
                txtrPathVal = str(txtrPath.setTokens(frames='<udim>'))
            else:
                txtrPathVal = str(txtrPath.replaceFrameStr('<udim>'))
        else:
            txtrPathVal = str(txtrPath)

        node = NodegraphAPI.CreateNode('ArnoldShadingNode', group)
        node.getParameter('nodeType').setValue('image', 0)
        node.checkDynamicParameters()
        node.getParameter('parameters.filename.enable').setValue(1, 0)
        node.getParameter('parameters.filename.value').setValue(txtrPathVal, 0)
        createdNodes.append(node)

    # Katana's node layout function sucks. Just stack the nodes vertically.
    if createdNodes:
        nodeIter = iter(createdNodes)
        x, y = NodegraphAPI.GetNodePosition(next(nodeIter))
        for node in nodeIter:
            y -= 30
            NodegraphAPI.SetNodePosition(node, (x, y))

    return createdNodes


def breakOutShaderChannels(nodes=None):
    # type: (Optional[Iterable[NodegraphAPI.Node]]) -> List[NodegraphAPI.Node]
    """
    Creates and connects new Dot nodes to the component outputs (`out.r`,
    `out.g`, etc.) of a set of Arnold shading nodes.

    Parameters
    ----------
    nodes : Optional[Iterable[NodegraphAPI.Node]]

    Returns
    -------
    List[NodegraphAPI.Node]
        Any created Dot nodes.
    """
    if not nodes:
        nodes = NodegraphAPI.GetAllSelectedNodes()
    if not nodes:
        return []

    def makeDot(dotName, group):
        dot = katanalib.nodes.createNode('Dot', name=dotName, group=group)
        oldNodeAttrs = NodegraphAPI.GetNodeShapeAttrs(dot).copy()
        DrawingModule.nodeWorld_setShapeAttr(dot, 'basicDisplay', 1)
        NodegraphAPI.SetNodeShapeAttr(dot, 'basicDisplay', 1)
        newNodeAttrs = NodegraphAPI.GetNodeShapeAttrs(dot)
        Utils.EventModule.QueueEvent(eventType='node_shapeAttrsChanged',
                                     eventID=hash(dot),
                                     nodeName=dot.getName(),
                                     oldAttrs=oldNodeAttrs,
                                     newAttrs=newNodeAttrs)
        return dot

    result = []
    for node in nodes:
        if node.getType() != 'ArnoldShadingNode':
            continue
        ports = node.getOutputPorts()
        if len(ports) < 2:
            continue

        dots = []
        nodeGroup = node.getParent()
        for port in ports:
            breakoutName = ARNOLD_PORT_TO_BREAKOUT_NAME.get(port.getName())
            if breakoutName is not None:
                dot = makeDot(breakoutName, nodeGroup)
                port.connect(dot.getInputPortByIndex(0))
                dots.append(dot)

        if dots:
            nodeX, nodeY = NodegraphAPI.GetNodePosition(node)
            # (left, bottom, right, top)
            nodeBounds = DrawingModule.nodeWorld_getBounds(node)
            dotX = nodeBounds[2] + 100
            # totalDotVSpace = 20 * len(dots) + 50 * (len(dots) - 1)
            dotY = nodeY + ((len(dots) - 1) * 50) / 2.0
            for dot in dots:
                NodegraphAPI.SetNodePosition(dot, (dotX, dotY))
                dotY -= 50
            result.extend(dots)

    Utils.EventModule.QueueEvent('nodegraph_redraw', 0)
    return result


# keep names in sync with `usdshadebakehelper` sub commands
class UsdBakeMode(enum.Enum):
    materials = 'materials'
    bindings = 'bindings'
    split = 'split'
    combined = 'combined'


class ShaderExportContext(object):
    def __init__(self, shdrExportNode):
        self.exportNode = shdrExportNode
        # Using getChildByIndex() because the internal node name can change
        self.lookFileBakeNode = self.exportNode.getChildByIndex(0)
        self.usdBakeNode = self.exportNode.getChildByIndex(1)

        exportRootParam = self.lookFileBakeNode.getParameter('rootLocations')
        rootLocations = [x.getValue(0) for x in exportRootParam.getChildren()]
        assert len(rootLocations) == 1

        self.beforeNode = self.exportNode.getInputPort(
            'before').getConnectedPort(0).getNode()
        while self.beforeNode.getType() == 'Dot':
            self.beforeNode = self.beforeNode.getInputPort(
                'input').getConnectedPort(0).getNode()
        self.afterNode = self.exportNode.getInputPort(
            'after').getConnectedPort(0).getNode()

        self.client = katanalib.nodes.getClientFromNode(self.afterNode)
        self.exportRoot = rootLocations[0].rstrip('/')
        self.exportLoc = self.client.cookLocation(self.exportRoot)

        # problems may set this to true, if they have run solutions that have
        # invalidated any of the cached data in this context.
        self.dirty = False

    @cache
    @property
    def modelLoc(self):
        # type: () -> Optional[Geolib.LocationData]
        """
        Get the models location in the DAG by traversing up the parents until
        we get a match.

        Returns
        -------
        Optional[Geolib.LocationData]
        """
        testPath = self.exportRoot
        while testPath:
            modelLoc = self.client.cookLocation(testPath)
            # If the modelLoc we've cooked looks appropriate then break the loop
            # and return the value
            if self.looksLikeUSDModelRoot(modelLoc):
                return modelLoc
            # This level didn't match so check if the parent matches
            testPath = testPath.rsplit('/', 1)[0]
        return None

    @cache
    @property
    def modelName(self):
        # type: () -> str
        """
        Returns
        -------
        str
        """
        return self.modelLoc.getAttrs().getChildByName('modelName').getValue()

    @cache
    @property
    def parentsWithAssignments(self):
        # type: () -> List[Geolib.LocationData]
        """
        Get a list of all the parents above modelLoc that appear to have
        material, look file, or Arnold settings overrides assigned to them.

        Returns
        -------
        List[Geolib.LocationData]
        """
        parentsWithAssignments = []
        # start with parent of export root
        testPath = self.exportRoot.rsplit('/', 1)[0]
        while testPath:
            testLoc = self.client.cookLocation(testPath)
            # Basic check for material/attribute assignments above export level
            locAttrs = testLoc.getAttrs()
            if not locAttrs:
                break
            if any(locAttrs.getChildByName(name) is not None for name in
                   ('materialAssign', 'material', 'arnoldStatements', 'lookfile')):
                parentsWithAssignments.append(testPath)
            testPath = testPath.rsplit('/', 1)[0]
        return parentsWithAssignments

    @cache
    def looksLikeUSDModelRoot(self, location):
        # type: (Geolib.LocationData) -> bool
        """
        Basic check to ensure we're working on a USD model

        Parameters
        ----------
        location : Geolib.LocationData

        Returns
        -------
        bool
        """
        attrs = location.getAttrs()
        if not attrs or attrs.getChildByName('modelName') is None:
            return False
        # typeName = attrs.getChildByName('type').getValue()
        kind = attrs.getChildByName('kind').getValue()
        # allow exporting off of components, assemblies or groups.
        # FIXME: We should probably warn on kind == assembly because those
        #  can be better handled by exporting off of each child component in
        #  cases where the assembly structure evolves more than the children.
        return kind in MODEL_ROOT_KINDS

    @cache
    def getShadingVariant(self):
        # type () -> Optional[str]
        if utils.getUserParamValue(self.exportNode, 'addShadingVariant'):
            variant = utils.getUserParamValue(self.exportNode, 'shadingVariant')
            assert variant, 'shadingVariant parameter is blank'
            return variant
        return None

    @cache
    def getTextureVariations(self):
        # type: () -> Dict[str, Any]
        """
        Get all pertinant model variant selections for a Texture export from
        the scene graph.

        Returns
        -------
        Dict[str, Any]
        """
        txtrVariants = {}

        modelAttrs = self.modelLoc.getAttrs()
        modelVariants = modelAttrs.getChildByName('info.usd.selectedVariants')

        # use a whitelist to avoid grabbing variant selections on parent prims
        # like layout version, etc.
        txtrVariantSetNames = ('mesh', 'rigg', 'lod',
                               # get the fx variant just for skipping warning
                               'fx',
                               # to skip no mesh/rigg warning for agents
                               'skeleton',)
        # crowd shaders are assigned over version variants of many named
        # "DescriptorX_variations" which supply the possible meshes for a
        # crowd agent.
        txtrVariantSetSuffixes = ('variations',)

        for childName, childAttr in modelVariants.childList():
            value = childAttr.getValue()
            if (childName in txtrVariantSetNames or
                    childName.endswith(txtrVariantSetSuffixes)):
                txtrVariants[childName] = childAttr.getValue()
            else:
                _logger.debug('disregarding scene variant selection for txtr '
                              'registry: %s=%s'
                              % (childName, value))

        shadingVariant = self.getShadingVariant()
        if shadingVariant:
            txtrVariants['shadingVariant'] = shadingVariant

        return txtrVariants

    @cache
    def getContributingNodes(self):
        # type: () -> Set[NodegraphAPI.Node]
        """
        Get all nodes between before and after nodes that make up the shader.

        Returns
        -------
        Set[NodegraphAPI.Node]
        """
        nodeList = set((self.afterNode,))
        nodeList.update(katanalib.nodes.iterLogicalNodeGraph(self.afterNode))
        nodeList.discard(self.beforeNode)
        nodeList.difference_update(
            katanalib.nodes.iterLogicalNodeGraph(self.beforeNode))
        return nodeList

    @cache
    def getAssetTokens(self):
        # type: () -> Tuple[str, str]
        """
        Returns
        -------
        str
            Asset or shot name
        str
            Descriptor value
        """
        match = SHADER_ASSET_RE.match(self.modelName)
        if not match:
            raise ValueError('Could not parse model name: %s' % self.modelName)
        asset = match.group('asset') or match.group('shot')
        assetDesc = match.group('descriptor').replace('_', '.')
        return asset, assetDesc

    def getExportPath(self, extension, initials=None):
        # type: (str, Optional[str]) -> filepath.Path
        """
        Parameters
        ----------
        extension : str
        initials : Optional[str]

        Returns
        -------
        filepath.Path
        """
        shotOrAsset, descriptor = self.getAssetTokens()
        pass_ = ''
        if self.exportNode.getParameterValue('user.addShadingVariant', 0):
            pass_ = self.exportNode.getParameterValue('user.shadingVariant', 0)

        scenePath = utils.scenePath()
        # since we can have a txtr per agent variation we also need the
        # scenes descriptor for crowd textures:
        # (note: we may want to just roll this out for all shaders so that the
        # descriptor of the scene matches the output path. We'd have to alter
        # the config parsing too).
        if descriptor == 'Agent':
            descriptor = 'Agent.{}'.format(scenePath.descriptor)
        sourcePath = scenePath.setTokens(shot=shotOrAsset,
                                         descriptor=descriptor)
        assert isinstance(sourcePath, filepath.Path)
        outputPath = filepath.Path(
            utils.getOutputPath(extension, pass_=pass_, seq=False,
                                sourcePath=sourcePath))
        if initials:
            outputPath = outputPath.setInitials(initials)
        return outputPath

    def getMode(self):
        # type: () -> UsdBakeMode
        split = self.exportNode.getParameterValue('user.splitExport', 0)
        if not split:
            return UsdBakeMode.combined
        bindings = self.exportNode.getParameterValue(
            'user.splitOptions.bindings', 0)
        if self.exportNode.getParameterValue('user.splitOptions.materials', 0):
            if bindings:
                return UsdBakeMode.split
            return UsdBakeMode.materials
        elif bindings:
            return UsdBakeMode.bindings
        raise ValueError('Invalid mode. Nothing selected for export.')

    def getSourceMaterialsPath(self):
        # type: () -> Optional[filepath.Path]
        path = self.exportNode.getParameterValue(
            'user.splitOptions.sourceMaterialsUsdPath', 0)
        if not path:
            return None
        return filepath.Path(path)


def _setupBakeNodeParameters(bakeNode, outputPath, outputFormatValue):
    # type: (NodegraphAPI.Node, Union[str, filepath.Path], str) -> None
    """
    Set the output filepath on a look file bake node.

    Parameters
    ----------
    bakeNode : NodegraphAPI.Node
    outputPath : Union[str, filepath.Path]
    outputFormatValue : str
        The value to apply to the `options.outputFormat` parameter.
    """
    bakeNode.getParameter('options.outputFormat').setValue(outputFormatValue, 0)
    bakeNode.getParameter('options.includeGlobalAttributes').setValue('Yes', 0)
    p = bakeNode.getParameter('saveTo')
    p.setExpressionFlag(False)
    p.setValue(str(outputPath), 0)


def _setupUsdBakeParameters(exportNode, mode, materialsPath):
    # type: (NodegraphAPI.Node, UsdBakeMode, Optional[filepath.Path]) -> None
    """
    Saves the pre-existing or caculated material path to the necessary
    attributes.

    Parameters
    ----------
    exportNode : NodegraphAPI.Node
    mode : UsdBakeMode
    materialsPath : Optional[filepath.Path]
    """
    from luma_katana.constants import BAKE_MATERIAL_PATH_ATTR, BAKE_MODE_ATTR

    bakeModeAttr = exportNode.getParameter('user.%s' % BAKE_MODE_ATTR)
    if bakeModeAttr is None:
        # This is an older version of the ShaderExportNode that will always
        # usd 'combined' mode.
        return
    bakeModeAttr.setValue(str(mode.value), 0)
    exportNode.getParameter('user.%s' % BAKE_MATERIAL_PATH_ATTR).setValue(
        str(materialsPath or ''), 0)


def _checkProblems(context):
    # type: (ShaderExportContext) -> bool
    """
    The primary entry point called by our shader export node.

    Parameters
    ----------
    context : ShaderExportContext

    Returns
    -------
    bool
    """
    import problems

    import luma_katana.preflight as preflight
    from luma_qt import rehabilitator
    from luma_qt.Qt import QtWidgets

    shaderProblems = preflight.getShaderPreflightProblems(context)
    hasProblems = [prob for prob in shaderProblems if prob.hasProblem()]
    if hasProblems:
        problemManager = problems.ProblemManager(shaderProblems)
        rehab = rehabilitator.StandaloneRehabilitator(
            problemManager,
            description='Your shader export has encountered problems!')

        continued = rehab.exec_() == QtWidgets.QDialog.Accepted
        if continued and rehab.problemsThatRanSolution:
            # Some "fixes" like setting "ignoring missing textures=OFF", mean
            # that other checks like shader validation will start to
            # fail, so we run test agin. The exporter relies on all checks to
            # have passed if this function returns True.
            return _checkProblems(context)
        return continued
    return True


@utils.printtraceback
def testExport(shdrExportNode):
    # type: (NodegraphAPI.Node) -> None
    """
    The primary entry point called by our shader export node.

    Parameters
    ----------
    shdrExportNode : NodegraphAPI.Node
    """
    from UI4.Widgets import MessageBox
    context = ShaderExportContext(shdrExportNode)
    if _checkProblems(context):
        MessageBox.Information('Tests', 'Test Successful!', cancelText='Ok')


@utils.printtraceback
def exportShaders(shdrExportNode):
    # type: (NodegraphAPI.Node) -> None
    """
    The primary entry point called by our shader export node.

    Parameters
    ----------
    shdrExportNode : NodegraphAPI.Node
    """
    from UI4.Widgets import MessageBox

    import importExport.utils

    import luma.render.managers
    import luma.sync
    from luma_katana.ui.pyqt import ProgressCallback

    try:
        import pxr.UsdAi
        usdSupported = True
    except ImportError:
        usdSupported = False

    with ProgressCallback(logger=_logger,
                          progressLogLevel=logging.DEBUG) as progressCallback:
        context = ShaderExportContext(shdrExportNode)
        if not _checkProblems(context):
            return
        # Note: So far none of the problems actually change the info on the
        # context. But we'll need to get a fresh context if any fixes are run.
        if context.dirty:
            context = ShaderExportContext(shdrExportNode)

        modelName = context.modelName

        scenePath = utils.scenePath()
        dependInputs = getExportDependencies(scenePath, context)
        sceneState = luma.depend.FileStateNode(scenePath, new=True)
        shadingVariant = context.getShadingVariant() or 'None'
        manager = luma.render.managers.getManager(
            '_'.join([scenePath.namebase, shadingVariant, 'ShaderExport']))

        outputs = []  # type: List[filepath.Path]
        syncDeps = []  # type: List[luma_deadline.manager.LumaDeadlineProxy]

        results = exportKlf(context, progressCallback)
        if results is not None:
            outputs.extend(results)
            klfPath, katanaPath = results
            klfState = _addShaderDependencies(scenePath, klfPath, dependInputs)
            _addImporterDependencies(sceneState, klfState, katanaPath)

        compatibilityInfo = 'not a usd shader export'
        # ensure that the code is backward compatible by not assuming that
        # the usdBakeNode exists.
        if usdSupported and context.usdBakeNode and modelName:
            from luma_usd.pipe.txtr import (
                addRefToMaterialRegistry, emailReportInSubprocess,
                pruneShadersForVariants, validateNewShader
            )
            from luma_usd.registry import (
                AgentTxtrConfig, AssetUsd, AssetUsdConfig, BasicTxtrConfig,
                ConfigValueError, TxtrCharBindingsConfig, TxtrCharConfig,
                TxtrCharMaterialsOnlyConfig
            )
            from luma_usd.variants import PrimVariant

            materialsPath, bindingsPath = \
                exportUsd(context, progressCallback=progressCallback)
            usdPaths = [p for p in [materialsPath, bindingsPath] if p]
            if usdPaths:
                outputs.extend(usdPaths)
                txtrVariants = context.getTextureVariations()

                for output in usdPaths:
                    _addShaderDependencies(sceneState, output, dependInputs)

                # "main" usd path for this export
                usdPath = usdPaths[0]
                isCrowdExport = 'skeleton' in txtrVariants
                if isCrowdExport:
                    config = AgentTxtrConfig(**txtrVariants)  # type: AssetUsdConfig
                elif len(usdPaths) == 2:
                    config = TxtrCharBindingsConfig(**txtrVariants)
                    usdPath = usdPaths[1]
                else:
                    try:
                        config = TxtrCharConfig(**txtrVariants)
                    except ConfigValueError:
                        config = BasicTxtrConfig()

                # model name can be "asset_desc" or "asset"
                if not modelName == config.assetName(usdPath):
                    raise ValueError('Txtr output should match asset being '
                                     'shaded. %s != %s'
                                     % (modelName, config.assetName(usdPath)))

                if isCrowdExport:
                    _logger.info('Optimizing shader for each mesh variant')
                    pruneShadersForVariants(
                        config.getAssetUsdPath(usdPath),
                        usdPath,
                        [PrimVariant(p, v) for p, v in txtrVariants.items()])

                mode = context.getMode()
                if (materialsPath and
                        mode in (UsdBakeMode.materials, UsdBakeMode.split)):
                    TxtrCharMaterialsOnlyConfig().register(materialsPath,
                                                           asset=modelName)
                if len(usdPaths) == 2:
                    assert bindingsPath and materialsPath
                    addRefToMaterialRegistry(bindingsPath, materialsPath)
                    config.register(bindingsPath, asset=modelName)
                elif mode == UsdBakeMode.combined:
                    config.register(usdPath, asset=modelName)

                # TODO: Shader validation for split bindings.
                # if isinstance(config, TxtrCharConfig):
                if type(config) == TxtrCharConfig:
                    # shader validation:
                    latestRiggCompatible, compatibilityInfo, _ = \
                        validateNewShader(usdPath, txtrVariants['lod'],
                                          numToValidate=10, register=True)
                    # using subprocess because pandas requires numpy >= 1.9.0,
                    # which is higher than katana's 1.5.1 version
                    emailReportInSubprocess(usdPath, txtrVariants['lod'],
                                            numToValidate=20)
                    # record the variants that a texture was exported on only
                    # for forensic purposes
                    config.recordConfigMetadata(usdPath, modelName)
                else:
                    compatibilityInfo = 'no validation occurred'

                # preview job will save over usd file in place. (skip
                # generatePreview if just doing test export. We may want to
                # make this an option on the export node as well.)
                generatePreview = usdPath.initials != 'XXX'
                if generatePreview:
                    _logger.info(
                        'Submitting job to generate preview shaders...')
                    _, jobData = createPreviewShadersJob(manager, usdPath)
                    syncDeps.append(jobData)

        progressCallback.info('Publishing outputs...')
        notes = utils.getUserParamValue(shdrExportNode, 'notes')
        turntable = utils.getUserParamValue(shdrExportNode, 'turntable')
        validPaths = [output for output in outputs if output.isValid()]
        asyncPublish(validPaths, action='export', note=notes,
                     reviewComponent=turntable)

        progressCallback.info('Heroing texture outputs...')

        txtrPaths, extraTxtrPaths = _getTextureDependencies(dependInputs)
        for txtrPath in txtrPaths:
            txtrPath.hero(skipFtrack=True)

        # also sync off-pipe textures
        # (it could also be a good idea to warn about this)
        syncPaths = [scenePath]
        syncPaths.extend(outputs)
        syncPaths.extend(extraTxtrPaths)

        submitter = luma.sync.SyncSubmitter(luma.sync.getDefaultRemoteDomain(),
                                            appName='export-katana')

        # main sync of shader outputs, wait for all jobs that alter outputs.
        submitter.createJob(syncPaths, jobTitle=scenePath.namebase)
        syncJobData = submitter.addToManager(manager, prioritizeBySize=True,
                                             delayDump=2)
        if syncDeps:
            syncJobData.addDependencies(*syncDeps)

        # Spawn a secondary sync job for the linked Mari textures, so it can be
        # more easily managed in the case of duplicate jobs.
        if txtrPaths:
            submitter.createJob(
                txtrPaths,
                jobTitle='{0}_textures'.format(scenePath.namebase))
            submitter.addToManager(manager, prioritizeBySize=True, delayDump=2)

        manager.submit()

        # restrict to just email, as xmpp is not working in Katana
        importExport.utils.notifyArtistOfExport(
            scenePath,
            messageInfo={'notes': notes,
                         'shader compatibility': compatibilityInfo},
            deliveryMethods=['email', 'growl'],
            lead=True,
            coord=True)

        progressCallback.info('Export complete')

    if not progressCallback.aborted:
        MessageBox.Information('Export Complete',
                               'Successfully exported and heroed the following '
                               'files:\n\n{0}'.format('\n'.join(outputs)))


def exportUsd(context, outputPath=None, progressCallback=None):
    # type: (ShaderExportContext, Optional[filepath.Path], Optional[luma_katana.ui.pyqt.ProgressCallback]) -> Tuple[Optional[filepath.Path], Optional[filepath.Path]]
    """
    Export the USD shading file.

    Parameters
    ----------
    context : ShaderExportContext
    outputPath : Optional[filepath.Path]
    progressCallback : Optional[luma_katana.ui.pyqt.ProgressCallback]

    Returns
    -------
    Tuple[Optional[filepath.Path], Optional[filepath.Path]]
        exported usd materials file and/or separate bindings file
    """
    from UI4.Widgets import MessageBox

    from katanalib.app import QtWidgets

    if outputPath is None:
        outputPath = context.getExportPath('usd')

    bindingsPath = None
    materialsPath = None
    mode = context.getMode()
    if mode == UsdBakeMode.combined:
        outputPaths = [outputPath]
    else:
        outputPaths = []
        if mode == UsdBakeMode.bindings:
            materialsPath = context.getSourceMaterialsPath()
            if not materialsPath:
                raise ValueError('If only exporting bindings, you must provide '
                                 'a source materials usd path.')
        else:
            # we will author our own materials to the proper path.
            matPass = (outputPath.pass_ +
                       '_materials' if outputPath.pass_ else 'materials')
            materialsPath = outputPath.setPass(matPass)
            outputPaths.append(materialsPath)

        bindingPass = (outputPath.pass_ +
                       '_bindings' if outputPath.pass_ else 'bindings')
        bindingsPath = outputPath.setPass(bindingPass)
        outputPaths.append(bindingsPath)

    existingPaths = [str(p) for p in outputPaths if p.exists()]
    if existingPaths:
        if MessageBox.Warning(
                'Overwrite Existing USD',
                'Output USD path(s) already exists:\n\t {0!s}\n\n'
                'Are you sure you want to overwrite it?'.format(
                    ',\n\t'.join(existingPaths)),
                acceptText='Overwrite',
                cancelText='Cancel') == QtWidgets.QMessageBox.RejectRole:
            if progressCallback:
                progressCallback.interrupt()
            return None, None

    if KATANA_API_VERSION >= (3, 1):
        # In 3.1+, we use the existing LookFileBake node instead of our custom
        # UsdWrite node, so we need to set the output format explicitly.
        bakeNode = context.lookFileBakeNode
        outputFormatValue = USD_LOOKFILE_FORMAT_DISPLAY_NAME
    else:
        bakeNode = context.usdBakeNode
        outputFormatValue = 'usda'

    exportRootParam = bakeNode.getParameter('rootLocations')
    rootLocations = [x.getValue(0) for x in exportRootParam.getChildren()]
    assert len(rootLocations) == 1

    mainExportPath = bindingsPath or outputPath
    _setupUsdBakeParameters(context.exportNode, mode, materialsPath)
    _setupBakeNodeParameters(bakeNode, mainExportPath, outputFormatValue)
    # XXX: I switched to `WriteToAsset` here because it's the only method that
    # fires the `preLookFileBake` callback, and the USD look file format plugin
    # currently depends on that callback. We should be able to change this (if
    # we need/want to) once the format plugins have access to the scene graph.
    # First arg is graph state. None is treated as "current".
    assert mainExportPath
    bakeNode.WriteToAsset(None, mainExportPath, progressCallback=progressCallback)
    if mode == UsdBakeMode.combined:
        return outputPath, None
    return materialsPath, bindingsPath


def findUsdAssetFromProducer(producer):
    # type: (GeolibProducers.GeometryProducer) -> Optional[GeolibProducers.GeometryProducer]
    """
    Parameters
    ----------
    producer : GeolibProducers.GeometryProducer

    Returns
    -------
    Optional[GeolibProducers.GeometryProducer]
    """
    def looksLikeUSDModelRoot(p):
        if p.getAttribute('modelName') is None:
            return False
        kindAttr = p.getAttribute('kind')
        if not kindAttr:
            return False
        return kindAttr.getValue() in MODEL_ROOT_KINDS

    while producer is not None:
        if looksLikeUSDModelRoot(producer):
            return producer
        producer = producer.getParent()
    return None


def usdShadeBakeHelper(assetRoot, diffRoot, materials,
                       outputRootList, sharedOverrides, rootOverrides,
                       materialsPath=None, sourceMaterialsPath=None,
                       bindingsPath=None, looksParent=None, sparseParams=False,
                       mode=UsdBakeMode.combined):
    # type: (str, str, Dict[str, Tuple[str, ScenegraphAttr.Attr]], List[Tuple[Dict[str, str], str, str]], Dict[str, Dict[str, ScenegraphAttr.Attr]], Optional[Dict[str, ScenegraphAttr.Attr]], Optional[str], Optional[str], Optional[str], Optional[str], bool, UsdBakeMode) -> None
    """
    Write material and override data produced by Katana's LookFile API to USD
    using the `usdshadebakehelper` script in a subprocess.

    Parameters
    ----------
    assetRoot : str
        The scene graph path to the root of the asset being exported.
    diffRoot :  str
        The root scene graph path of the attribute diff. This must be equal to
        or a child of `assetRoot`.
    materials : Dict[str, Tuple[str, ScenegraphAttr.Attr]]
        Maps material scene graph paths to tuples of `(locationType, attr)`,
        where `locationType` is usually 'material', and `attr` is the attribute
        containing the material data.
    outputRootList : List[Tuple[Dict[str, str], str, str]]
        Tuples describing the export root locations and any of their children
        that have overrides baked. Each tuple contains:
        - A dictionary mapping relative location paths to opaque identifiers,
          which are used as keys into `sharedOverrides` to look up attribute
          overrides for the location.
        - The name of the root location being baked.
        - The type of the root location being baked.
    sharedOverrides : Dict[str, Dict[str, ScenegraphAttr.Attr]]
        A dictionary mapping the opaque identifiers in the children of
        `outputRootList` to dictionaries of name-attribute override pairs.
    rootOverrides : Optional[Dict[str, ScenegraphAttr.Attr]]
        An optional dictionary of name-attribute override pairs for '/root'.
    materialsPath : Optional[str]
        Output USD path of materials or materials and bindings in 'combined' mode.
    sourceMaterialsPath : Optional[str]
        Input USD path of materials to use if just exporting bindings.
    bindingsPath : Optional[str]
        Output USD path of bindings.
    looksParent : Optional[str]
    sparseParams : bool
        Only author values for explicitly set material parameters.
    mode : UsdBakeMode
    """
    import os
    import subprocess
    import tempfile

    from pylib.serializers import pickle_dumps

    from luma_usd.registry import getCleanName

    # XXX: Guard to avoid surprises. There's no technical reason we can't
    # handle multiple root locations per bake, but our pipeline does not
    # currently support it.
    assert len(outputRootList) == 1, \
        'Multiple root locations are not currently supported'

    if not diffRoot.startswith(assetRoot):
        raise ValueError('Diff root %s is not a child of the given asset '
                         'root %s' % (diffRoot, assetRoot))

    # FIXME: Temporary(?) workaround for strange crashes in USD that are
    # triggered by the bake helper script.
    env = os.environ.copy()
    env['LD_PRELOAD'] = os.path.expandvars('${ARNOLD_HOME}/bin/libai.so')
    # END FIXME

    # FIXME: Crowd specific behavior.
    outPath = filepath.Path(materialsPath or bindingsPath)
    isCrowdExport = outPath.descriptor.startswith('Agent')
    if isCrowdExport and not looksParent:
        # we need looks to be under mesh so that the modelingVariant can
        # deactivate unused materials for an optimized agent
        looksParent = assetRoot + '/mesh'
        # since crowd exports are overlayed we want to make sure that
        # any materials are in a new group so they avoid name conflicts
        if outPath.descriptor:
            cleanDesc = getCleanName(
                outPath.descriptor.replace('Agent.', '', 1))
            looksParent = looksParent + '/' + cleanDesc + '_Looks'

    bakeData = {'materials': convertToNative(materials, mapping=dict),
                'outputRootList': outputRootList,
                'sharedOverrides': convertToNative(sharedOverrides,
                                                   mapping=dict),
                'rootOverrides': convertToNative(rootOverrides)}

    with tempfile.NamedTemporaryFile(prefix='usdShadeBakeData_', suffix='.bin',
                                     delete=False) as fh:
        fh.write(pickle_dumps(bakeData))
        fh.flush()
        success = True
        command = ['usdshadebakehelper', '--asset-root', assetRoot,
                   '--diff-root', diffRoot, '--datafile', fh.name]
        if looksParent:
            command.extend(['--looks-parent', looksParent])
        if sparseParams:
            command.append('--sparse-params')

        # subcommand and args:
        command.append(mode.value)
        if materialsPath:
            command.extend(['--materials-output', materialsPath])
        if sourceMaterialsPath:
            command.extend(['--source-materials', sourceMaterialsPath])
        if bindingsPath:
            command.extend(['--bindings-output', bindingsPath])

        print('running command: "' + ' '.join(command) + '"')
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT,
                                             env=env, text=True)
        except subprocess.CalledProcessError as e:
            from UI4.Widgets import MessageBox
            output = e.output
            MessageBox.Critical(
                'USD Shader Bake Error',
                'An unexpected error occurred in the USD shader bake script\n\n'
                'See detailed info (or the terminal) for the complete script '
                'output.',
                detailedText=output)
            success = False
        print(output)
    if success:
        os.unlink(fh.name)


def exportKlf(context, progressCallback):
    # type: (ShaderExportContext, luma_katana.ui.pyqt.ProgressCallback) -> Optional[Tuple[filepath.Path, filepath.Path]]
    """
    Export the klf file and the katana file used to import it.

    Parameters
    ----------
    context : ShaderExportContext
    progressCallback : luma_katana.ui.pyqt.ProgressCallback

    Returns
    -------
    Optional[Tuple[filepath.Path, filepath.Path]]
        exported klf file
        exported katana file, for import
    """
    from UI4.Widgets import MessageBox

    from katanalib.app import QtWidgets

    import luma.render.utils

    outputPath = context.getExportPath('klf')

    if outputPath.exists():
        if MessageBox.Warning(
                'Overwrite Existing KLF',
                'Output KLF path {0!r} already exists\n\n'
                'Are you sure you want to overwrite it?'.format(str(outputPath)),
                acceptText='Overwrite',
                cancelText='Cancel') == QtWidgets.QMessageBox.RejectRole:
            progressCallback.interrupt()
            return None

    progressCallback.info('Exporting shader lookfile: {}'.format(outputPath))
    bakeNode = context.lookFileBakeNode
    _setupBakeNodeParameters(bakeNode, outputPath,
                             LookFileConstants.OutputFormat.AS_ARCHIVE)

    luma.render.utils.createOutputDir(outputPath)
    # First arg is graph state. None is treated as "current".
    bakeNode.WriteToLookFile(None, outputPath, includeGlobalAttributes=True,
                             progressCallback=progressCallback)

    # Create and configure a ShaderImport macro to be exported to a .katana file
    katanaPath = outputPath.outputPath(ext='katana')
    leafLoc = context.exportRoot.rsplit('/', 1)[-1]
    nameParts = ['ShaderImport', leafLoc]
    try:
        version = outputPath.version
    except Exception:
        pass
    else:
        nameParts.append(version)

    importNode = katanalib.nodes.createNode('ShaderImportNode',
                                            name='_'.join(nameParts))

    matGroup = None
    try:
        matGroup = str(outputPath.tokenizeFilename()[-1]['shot'])
    except Exception:
        pass
    if not matGroup:
        matGroup = 'defaultLookfileGroup'

    try:
        importNode.getParameter('user.CEL').setValue('//' + leafLoc, 0)
        importNode.getParameter('user.lookFilePath').setValue(str(outputPath), 0)
        importNode.getParameter('user.materialGroupName').setValue(matGroup, 0)
        progressCallback.info('Exporting wrapper scene: {}'.format(katanaPath))
        luma.render.utils.createOutputDir(katanaPath)
        KatanaFile.Export(str(katanaPath), [importNode])
    finally:
        importNode.delete()

    outputPath.hero()
    katanaPath.hero()
    return outputPath, katanaPath


def _getTextureDependencies(dependencies):
    # type: (Any) -> Tuple[Set[filepath.Path], Set[filepath.Path]]
    """
    Sort through dependencies and find mari textures, and off-pipe textures.

    Parameters
    ----------
    dependencies

    Returns
    -------
    Tuple[Set[filepath.Path], Set[filepath.Path]]
        mari textures:
            should be heroed (to trigger next Mari export to version up)
        off-pipe textures:
            should be synced
    """
    import imageinfo
    imageTypes = set(['.' + x for x in imageinfo.listImageTypes()])
    txtrPaths = set()
    extraTxtrPaths = set()  # off-pipe textures
    for dependInput in dependencies:
        # Collect txtr output paths to hero
        dependPath = dependInput.path().realpath()
        try:
            tokens = dependPath.tokenize()[-1]
        except Exception:
            if dependPath.ext in imageTypes:
                extraTxtrPaths.add(dependPath)
        else:
            if tokens['element'] == 'txtr' \
                    and tokens['subdir'] == 'mari/_output/images':
                txtrPaths.add(dependPath)
            elif dependPath.ext in imageTypes:
                extraTxtrPaths.add(dependPath)
    return txtrPaths, extraTxtrPaths


def getExportDependencies(scenePath, context):
    # type: (filepath.Path, ShaderExportContext) -> List[luma.depend.DependInput]
    """
    Parameters
    ----------
    scenePath : filepath.Path
    context: ShaderExportContext

    Returns
    -------
    List[luma.depend.DependInput]
    """
    import luma_katana.depends

    # Find the set of nodes between the 'before' and 'after' inputs.
    klfInputNodes = context.getContributingNodes()
    dependSession = luma_katana.depends.KatanaSession(projectFile=scenePath,
                                                      nodes=klfInputNodes)
    return dependSession.getInputs()


def _addShaderDependencies(sceneState, shaderPath, dependencies):
    # type: (Optional[Union[str, sequences.PathType, luma.depend.FileNodeType]], filepath.Path, Any) -> luma.depend.FileStateNode
    """
    Commit dependencies.

    Parameters
    ----------
    sceneState : Optional[Union[str, sequences.PathType, luma.depend.FileNodeType]]
    shaderPath : filepath.Path

    Returns
    -------
    luma.depend.FileStateNode
        depend node for `shaderPath`
    """
    shaderState = luma.depend.FileStateNode(shaderPath, new=True)
    shaderState.producedBy(sceneState)

    for dependInput in dependencies:
        shaderState.addInput(dependInput)

    shaderState.commit()
    return shaderState


def _addImporterDependencies(sceneState, shaderState, katanaPath):
    # type: (luma.depend.FileStateNode, luma.depend.FileStateNode, Any) -> None
    """
    Add additional dependencies for the katana import node.

    Parameters
    ----------
    sceneState : luma.depend.FileStateNode
    shaderState : luma.depend.FileStateNode
    """
    katanaState = luma.depend.FileStateNode(katanaPath, new=True)
    katanaState.producedBy(sceneState)
    katanaState.hasLinkTo(shaderState)
    katanaState.commit()


def createPreviewShadersJob(manager, usdPath):
    # type: (luma.render.managers.QueueManager, filepath.Path) -> Tuple[luma.render.jobs.interface.JobInterface, luma_deadline.manager.LumaDeadlineProxy]
    """
    Submits a job that generates preview shaders for materials in the given usd
    path.

    Parameters
    ----------
    manager : luma.render.managers.QueueManager
    usdPath : filepath.Path

    Returns
    -------
    Tuple[luma.render.jobs.interface.JobInterface, luma_deadline.manager.LumaDeadlineProxy]
    """
    from pylib.types import DeferredCallable

    import luma.render.jobs.interface as _jobs
    import luma_deadline.manager

    job = _jobs.PythonCallable(
        func=DeferredCallable(
            'luma_usd.pipe.txtr.updatePreviewShaders'),
        args=(str(usdPath),),
        runtimeEnviron=_jobs.RuntimeEnviron(packages=['usd_arnold']),
        forcePackages=['usd_arnold']
    )
    time = datetime.datetime.today().strftime("%Y.%m.%d-%H:%M:%S.%f")
    job.title = job.title + '_{}_{}'.format(usdPath.namebase, time)

    jobData = manager.addJob(job)
    if manager.NAME == 'deadline':
        jobSettings = luma_deadline.manager.DeadlineJobSettings(
            priority=1000).withDefaults()
        jobSettings.apply(job, jobData)

    return job, jobData
