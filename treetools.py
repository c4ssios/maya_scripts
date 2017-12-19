import maya.cmds as cmds
import random

def doReplace(source, destination, mode):
    
    destinationSN = destination.split('|')[-1]
    destinationParent = cmds.listRelatives(destination, p=True, f=True)[0]
    
    tempName = destinationSN + '_tmp'
    
    if mode == "copy":
        cmds.duplicate(source, n=tempName)

    elif mode == "instance":
        cmds.instance(source, n=tempName)

    leafPos = cmds.xform(destination, t=True, q=True, ws=True)
    leafRot = cmds.xform(destination, ro=True, q=True, ws=True)
    leafScale = cmds.xform(destination, s=True, q=True, ws=True)
    cmds.xform(tempName, t=leafPos)
    cmds.xform(tempName, ro=leafRot)
    cmds.xform(tempName, s=leafScale)
    
    cmds.delete(destinationSN)
    cmds.rename(tempName, destinationSN)
    
    cmds.parent(destinationSN,destinationParent)

    
def listObjects():

    sel = cmds.ls(sl=True, l=True)
    
    newLeave = sel[1]

    leavesToReplace = listLeavesAlt(sel[0])

    return newLeave, leavesToReplace

 

def listLeaves(selection):

    children = cmds.listRelatives(selection, c=True, ad=True, typ='transform', f=True)

    leaves = []

    for c in children:
        if cmds.listRelatives(c, c=True, typ='transform')is None:
            leaves.append(c)

    return leaves

def listLeavesAlt(selection):

    children = cmds.listRelatives(selection, c=True, ad=True, typ='transform', f=True)

    leaves = []

    for c in children:
        if 'plantGreen' in c:
            leaves.append(c)

    return leaves



def selectLeaves():

    sel = cmds.ls(sl=True, l=True)

    cmds.select(cl=True)

    for s in sel:

        cmds.select(listLeaves(s), add=True)
    

def replaceLeaves(mode):
    
    source = listObjects()[0]
    destination = listObjects()[1]
    
    for d in destination:

        doReplace(source,d, mode)

def replaceClusters(mode):

    sel = cmds.ls(sl=True, l=True)
    source = sel[1]
    destinationClustersChildren = cmds.listRelatives(sel[0], c=True, ad=True,  typ='transform')

    destinationBranchList = []
    destinationLeavesList = []

    for c in destinationClustersChildren:
        if cmds.listRelatives(c, c=True, typ='transform')is None and 'branch' in c.lower():
            destinationBranchList.append(c)
        if cmds.listRelatives(c, c=True, typ='transform')is None and 'leave' in c.lower():
            destinationLeavesList.append(c)


    if len(destinationBranchList)==0 or len(destinationLeavesList)==0:

        print "Nothing to replace."

    else:
        cmds.group(em=True, name='tmpNull', p=source)

        leavesCombineName = 'plantGreen_C_' + source.split('|')[-1].split('_')[0] + 'leave00001_GEP'

        leavesList = listLeavesAlt(source)

        print 'leavesList =', leavesList

        if len(leavesList)>1:
            cmds.polyUnite(leavesList, ch=False, n=leavesCombineName)
        else:
            cmds.rename(leavesList[0], leavesCombineName)
            cmds.parent(leavesCombineName, w=True)


        branchesCombineName = 'woodbrown_C_' + source.split('|')[-1].split('_')[0] + 'branche00001_GEP'

        
        branchesList = cmds.listRelatives(cmds.listRelatives(source, c=True, ad=True, type='mesh', f=True), p=True, f=True)


        print 'branchesList', branchesList

        if len(branchesList)>1:
            cmds.polyUnite(branchesList, ch=False, n=branchesCombineName)
        else:
            cmds.rename(branchesList[0], branchesCombineName)
            cmds.parent(branchesCombineName, w=True)

        cmds.delete(cmds.listRelatives(source, c=True))

        cmds.parent(leavesCombineName, source)
        cmds.parent(branchesCombineName, source)


        # Disable undo queue
        cmds.undoInfo(st=False)



        for b in destinationBranchList:
            doReplace(source + '|' + branchesCombineName, b, mode)
            print str(destinationBranchList.index(b)+1) + '/' + str(len(destinationBranchList)) + ' branch replaced.'

        for l in destinationLeavesList:
            doReplace(source + '|' + leavesCombineName, l, mode)
            print str(destinationLeavesList.index(l)+1) + '/' + str(len(destinationLeavesList)) + ' leaf replaced.'


        # Enable undo queue
        cmds.undoInfo(st=True)



def uniformScale():
    
    sel = cmds.ls(sl=True, l=True)
    
    children = cmds.listRelatives(sel, c=True, ad=True, typ='transform', f=True)

    leaves = []

    for c in children:
        if cmds.listRelatives(c, c=True, typ='transform')is None:
            leaves.append(c)
    
    for l in leaves:
        scaleValues = cmds.xform(l, scale=True, q=True, relative=True)
        cmds.xform(l, s=(min(scaleValues),min(scaleValues),min(scaleValues)))


def chooseXpercent(givenItems, percent):

    #sel = cmds.ls(sl=True, l=True)

    if len(givenItems)==0:
        cmds.warning('Nothing is selected')

    else:

        numberOfItem = len(givenItems)*percent/100

        chosenList = random.sample(givenItems, numberOfItem)
        
        return chosenList


def createBoudingSphere(object):

    bbox = cmds.xform(object, bb=True, q=True)
    centerPosition = [(bbox[0]+bbox[3])/2 , (bbox[1]+bbox[4])/2, (bbox[2]+bbox[5])/2]
    size = max(bbox[3]-bbox[0], bbox[4]-bbox[1], bbox[5]-bbox[2])
    sphereName = object+'_bSphere'
    cmds.polySphere(n=sphereName, r=size/2)
    cmds.xform(sphereName, translation = centerPosition, ws=True)

def randomUDIMshift(number):

    sel = cmds.ls(sl=True, l=True)

    if len(sel) < number :
        cmds.warning ('Number of UDIMS superior to number of selected objects.')

    else:
        members = len(sel)/number
        random.shuffle(sel)
        for i in range(len(sel) // members + 1):

            group = sel[i*members:i*members + members]

            if len(group)<members:
                for g in group:
                    uvs = cmds.ls(cmds.polyListComponentConversion(g, toUV=True), fl=True)
                    cmds.polyEditUV(uvs,  u=number-1)

            else:
                for g in group:
                    uvs = cmds.ls(cmds.polyListComponentConversion(g, toUV=True), fl=True)
                    cmds.polyEditUV(uvs,  u=i)



            

def uvOrientationCheck():
    sel = cmds.ls(sl=True, l=True)
    offenders = []
    for s in sel :
        uvs = cmds.ls(cmds.polyListComponentConversion(s, toUV=True), fl=True)

        vMax = cmds.polyEvaluate(s, b2=True)[1][0]
        vMin = cmds.polyEvaluate(s, b2=True)[1][1]

        highestUV = ''
        lowestUV = ''
        for u in uvs :
            vValue = cmds.polyEditUV(u, q=True)[1]
            if vValue > vMax:
                vMax = vValue
                highestUV = u
            if vValue < vMin:
                vMin = vValue
                lowestUV = u

        highestVert = cmds.polyListComponentConversion(highestUV, toVertex=True)
        lowestVert = cmds.polyListComponentConversion(lowestUV, toVertex=True)
        
        highestVertY = cmds.xform(highestVert, t=True, q=True, ws=True)[1]
        lowsetVertY = cmds.xform(lowestVert, t=True, q=True, ws=True)[1]
        
        if lowsetVertY < highestVertY:
            pass
        else:
            offenders.append(s)
            
    if len(offenders)>0:
        cmds.select(offenders, r=True)
    else:
        print "All good so far."


def transfertUVtoHierarchy():

    objList = cmds.listRelatives(cmds.ls(sl=True, l=True), typ='transform', c=True, ad=True, f=True)
    
    for o in objList:
        shortName = cmds.ls(o,sn=True)[0]
        
        objParent = cmds.listRelatives(o, p=True, f=True)[0]
        objectChildren = cmds.listRelatives(o, c=True, typ='transform')
        
        cmds.parent(o, w=True)
        if objectChildren:
            cmds.parent(objectChildren, w=True)
        
        cmds.transferAttributes('temp:'+shortName, shortName, transferUVs=2, spa=4)
        cmds.delete(shortName, ch=True)
        cmds.delete('temp:'+shortName)
        
        if objectChildren:
            cmds.parent(objectChildren, shortName)
        cmds.parent(shortName, objParent)
        
        print "UVs transfer successfully on " + str(objList.index(o)+1) + '/' + str(len(objList)) + ' objects.'






