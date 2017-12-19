# script that returns the number of UV shells for a given UV set on selected polygon meshes;
# Owen Burgess 2011
# findUvShells()
import maya.OpenMaya as om
import maya.cmds as cmds

def findUvShells(uvSet = 'map1'):

  data = [] # this is the array that will store, per object in the selection list, a dagPath and the number of shells in the given UV set.
  
  selList = om.MSelectionList()
  om.MGlobal.getActiveSelectionList(selList)
  selListIter = om.MItSelectionList(selList, om.MFn.kMesh)
  
  uvShellArray = om.MIntArray() 
  
  # step through the objects on our selection list
  while not selListIter.isDone():
    pathToShape = om.MDagPath()
    selListIter.getDagPath(pathToShape)
    meshNode = pathToShape.fullPathName()
	
    # continue only if the given UV set exists on the shape
    uvSets = cmds.polyUVSet(meshNode, query=True, allUVSets =True)
	
    if (uvSet in uvSets):
 
      shapeFn = om.MFnMesh(pathToShape)
  
      shells = om.MScriptUtil()
      shells.createFromInt(0)
      shellsPtr = shells.asUintPtr()
  
      shapeFn.getUvShellsIds(uvShellArray, shellsPtr, uvSet)
  
      data.append( meshNode )
      data.append( str(shells.getUint(shellsPtr)) ) # I've chosen to return a string variable, but the class method returns an int
  
      # optional : print the shell index of each UV
      #print uvShellArray.length()
      #for i in range(uvShellArray.length()):
        #print uvShellArray[i]
          
    uvShellArray.clear()      
    selListIter.next()
  
  return data
  
# end  
