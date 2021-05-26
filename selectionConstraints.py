import maya.cmds as cmds

__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2010 - 2011 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["stacksHandler",
			"selectStarVertices",
			"ISelectStarVertices",
			"selectTrianglesFaces",
			"ISelectTrianglesFaces",
			"selectNsidesFaces",
			"ISelectNsidesFaces",
			"selectBoundaryEdges",
			"ISelectBoundaryEdges",
			"selectBorderEdges",
			"ISelectBorderEdges",
			"selectCreasesEdges",
			"ISelectCreasesEdges",
			"selectHardEdges",
			"ISelectHardEdges",
			"selectNonManifoldVertices",
			"ISelectNonManifoldVertices",
			"selectLaminaFaces",
			"ISelectLaminaFaces",
			"selectZeroGeometryAreaFaces",
			"ISelectZeroGeometryAreaFaces"]

def stacksHandler(object):
	"""
	This decorator is used to handle various Maya stacks.

	:param object: Python object. ( Object )
	:return: Python function. ( Function )
	"""

	def stacksHandlerCall(*args, **kwargs):
		"""
		This decorator is used to handle various Maya stacks.

		:return: Python object. ( Python )
		"""

		cmds.undoInfo(openChunk=True)
		value = object(*args, **kwargs)
		cmds.undoInfo(closeChunk=True)
		# Maya produces a weird command error if not wrapped here.
		try:
			cmds.repeatLast(addCommand="python(\"import %s; %s.%s()\")" % (__name__, __name__, object.__name__), addCommandLabel=object.__name__)
		except:
			pass
		return value

	return stacksHandlerCall

def selectStarVertices():
	"""
	This definition selects star vertices.
	"""

	cmds.polySelectConstraint(m=3, t=1, order=True, orb=(5, 65535))
	cmds.polySelectConstraint(dis=True)

@stacksHandler
def ISelectStarVertices(arg=None):
	"""
	This definition is the selectStarVertices definition Interface.
	"""

	selectStarVertices()

def selectTrianglesFaces():
	"""
	This definition selects triangles faces.
	"""

	cmds.polySelectConstraint(m=3, t=8, sz=1)
	cmds.polySelectConstraint(dis=True)

@stacksHandler
def ISelectTrianglesFaces(arg=None):
	"""
	This definition is the selectTrianglesFaces definition Interface.
	"""

	selectTrianglesFaces()

def selectNsidesFaces():
	"""
	This definition selects nsides faces.
	"""

	cmds.polySelectConstraint(m=3, t=8, sz=3)
	cmds.polySelectConstraint(dis=True)

@stacksHandler
def ISelectNsidesFaces(arg=None):
	"""
	This definition is the selectNsidesFaces definition Interface.
	"""

	selectNsidesFaces()

def selectBoundaryEdges(components):
	"""
	This definition selects selection boundaries edges.
	"""

	cmds.select(cmds.polyListComponentConversion(components, te=True, bo=True))

@stacksHandler
def ISelectBoundaryEdges(arg=None):
	"""
	This definition is the selectBoundaryEdges definition Interface.
	"""

	selection = cmds.ls(sl=True, l=True)
	selection and selectBoundaryEdges(selection)

def selectBorderEdges():
	"""
	This definition selects the border edges.
	"""

	cmds.polySelectConstraint(m=3, t=0x8000, w=1)
	cmds.polySelectConstraint(m=0)

@stacksHandler
def ISelectBorderEdges(arg=None):
	"""
	This definition is the selectBorderEdges definition Interface.
	"""

	selectBorderEdges()

def selectCreasesEdges(object):
	"""
	This definition cleans Maya hierarchical polygonal conversion.

	:param object: Object to select creases edges. ( String )
	"""

	edges = cmds.ls(object + ".e[0:" + str(cmds.polyEvaluate(object, edge=True) - 1) + "]", fl=True)
	creaseEdges = [edge for edge in edges if cmds.polyCrease(edge, q=True, v=True)[0] > 0.0]
	if creaseEdges:
		cmds.select(creaseEdges)

@stacksHandler
def ISelectCreasesEdges(arg=None):
	"""
	This definition is the selectCreasesEdges definition Interface.
	"""

	selection = cmds.ls(sl=True, l=True)
	selection and selectCreasesEdges(selection[0])

def selectHardEdges():
	"""
	This definition selects the hard edges.
	"""

	cmds.polySelectConstraint(m=3, t=0x8000, sm=1)
	cmds.polySelectConstraint(m=0)

@stacksHandler
def ISelectHardEdges(arg=None):
	"""
	This definition is the selectHardEdges definition Interface.
	"""

	selectHardEdges()

def selectNonManifoldVertices():
	"""
	This definition selects the non manifold vertices.
	"""

	cmds.polySelectConstraint(m=3, t=1, nonmanifold=True)
	cmds.polySelectConstraint(m=0)

@stacksHandler
def ISelectNonManifoldVertices(arg=None):
	"""
	This definition is the selectNonManifoldVertices definition Interface.
	"""

	selectNonManifoldVertices()

def selectLaminaFaces():
	"""
	This definition selects the lamina faces.
	"""

	cmds.polySelectConstraint(m=3, t=8, tp=2)
	cmds.polySelectConstraint(m=0)

@stacksHandler
def ISelectLaminaFaces(arg=None):
	"""
	This definition is the selectLaminaFaces definition Interface.
	"""

	selectLaminaFaces()

def selectZeroGeometryAreaFaces():
	"""
	This definition selects the zero geometry area faces.
	"""

	cmds.polySelectConstraint(m=3, t=8, ga=True, gab=(0, 0.001))
	cmds.polySelectConstraint(m=0)

@stacksHandler
def ISelectZeroGeometryAreaFaces(arg=None):
	"""
	This definition is the selectZeroGeometryAreaFaces definition Interface.
	"""

	selectZeroGeometryAreaFaces()

def closeWindow(arg=None):
	"""
	This definition close the window UI.
	"""
	
	cmds.deleteUI("selectionConstraint_window", window=True)

def selectionConstraintUI():
    """
    This definition is the selection Constraints UI
    """
        
    if (cmds.window("selectionConstraint_window", exists=True)):
        cmds.deleteUI("selectionConstraint_window")
        
   
    window = cmds.window("selectionConstraint_window", title="Selection Constraints Tool", width=250 )
    cmds.columnLayout( adjustableColumn=True )
    cmds.button( "selectStarVertices_button", label='Select Star Vertices', command=ISelectStarVertices )
    cmds.button( "selectTrianglesFaces_button", label='Select Triangles Faces', command=ISelectTrianglesFaces )
    cmds.button( "selectNsidesFaces_button", label='Select NSides Faces', command=ISelectNsidesFaces )
    cmds.button( "selectBoundaryEdges_button", label='Select Boundary Edges', command=ISelectBoundaryEdges )
    cmds.button( "selectBorderEdges_button", label='Select Border Edges', command=ISelectBorderEdges )
    cmds.button( "selectCreasesEdges_button", label='Select Creases Edges', command=ISelectCreasesEdges )
    cmds.button( "selectHardEdges_button", label='Select Hard Edges', command=ISelectHardEdges )
    cmds.button( "selectNonManifoldVertices_button", label='Select Non Manifold Vertices', command=ISelectNonManifoldVertices )
    cmds.button( "selectLaminaFaces_button", label='Select Lamina Faces', command=ISelectLaminaFaces )
    cmds.button( "selectZeroGeometryAreaFaces_button", label='Select Zero Geometry Area Faces', command=ISelectZeroGeometryAreaFaces )
    cmds.text ("")
    cmds.button("close_button", label='Close', command=closeWindow )
    cmds.setParent( '..' )
    cmds.showWindow("selectionConstraint_window")
    cmds.window( "selectionConstraint_window", edit=True, widthHeight=(250, 300) )
