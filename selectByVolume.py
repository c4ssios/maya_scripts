import maya.cmds as cmds

def selectByVolume(volumeMin, volumeMax):
    
    trans = cmds.ls(typ='transform')
    debris = []
    for t in trans:
        if cmds.attributeQuery ('geoId', n=t, ex=True):
            debris.append(t)
    
    matchingVolumeList = []
    
    for d in debris:
        bbox = cmds.exactWorldBoundingBox(d)
        
        X = bbox[3]- bbox[0]
        Y = bbox[4]- bbox[1]
        Z = bbox[5]- bbox[2]
        
        objectVolume = X*Y*Z
        
        if  volumeMin <= objectVolume <=volumeMax:
            matchingVolumeList.append(d)
            
    cmds.select(matchingVolumeList)


selectByVolume( 0.6 , 10 )
