def detectCreasedObject():
	objectList = cmds.listRelatives(cmds.ls(type='mesh', l=True),p=True, fullPath=True)

	creaseList = []

	for o in objectList:
	    if cmds.polyEvaluate(o, vertex=True):
	        vertexList = cmds.ls(cmds.polyListComponentConversion(o, tv=True), fl=True)
	        vertexCreaseList = cmds.polyCrease(vertexList, vv=True, q=True)
	        vertCreased = [x for x in vertexCreaseList if x > 0]
	        
	        edgeList = cmds.ls(cmds.polyListComponentConversion(o, te=True), fl=True)
	        edgeCreaseList = cmds.polyCrease(edgeList, v=True, q=True)
	        edgeCreased = [x for x in edgeCreaseList if x > 0]
	        
	        if vertCreased or edgeCreased:
	            creaseList.append(o)
	        
	        print 'Going through ' + str(objectList.index(o)+1)+'/'+str(len(objectList))+' objects...'
	            
	if creaseList:
	    print 'There are '+str(len(creaseList))+' objects with crease.'
	    for c in creaseList:
	        print c
	    cmds.select(creaseList, r=True)


detectCreasedObject()
