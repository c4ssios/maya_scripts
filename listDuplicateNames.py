import maya.cmds as cmds

def listDuplicateNames():
    transformList = cmds.ls(type='transform', l=True)
    uniqueNames = []
    nonUniqueNames = []
    for t in transformList:
        TRsn = t.split('|')[-1]
        if TRsn not in uniqueNames:
            uniqueNames.append(TRsn)
        else:
            if TRsn not in nonUniqueNames:
                nonUniqueNames.append(TRsn)
    
    result = ''
    
    if len(nonUniqueNames)==0:
        result = 'All Good !'
    else:
        result = 'Those objets are non-Uniques :\n\n'+'\n'.join(nonUniqueNames)
            
    cmds.confirmDialog( title='Non Unique List', message=result, button=['Close'], defaultButton='Close', cancelButton='Close', dismissString='Close' )
