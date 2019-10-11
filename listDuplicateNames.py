import maya.cmds as cmds


__title__ = "List Duplicate Names"
__version__ = '0.1'
__author__ = "Nicolas Leblanc"
__company__ = "Dwarf Animation"
__maintainer__ = "Nicolas Leblanc"
__email__ = "nicolas.leblanc@dwarfanimation.com"

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
    
    
    if len(nonUniqueNames)==0:

        cmds.confirmDialog( title='Non Unique List', message='All Good !', button=['Close'], defaultButton='Close', cancelButton='Close', dismissString='Close' )
        
    else:
        
        listDuplicateNamesResultUI(nonUniqueNames)
            

def listDuplicateNamesResultUI(list):
    windowWidth = 500
    windowHeight = 300
    
    if (cmds.window("listDuplicateNames_window", exists=True)):
        cmds.deleteUI("listDuplicateNames_window")

    window = cmds.window("listDuplicateNames_window", title= __title__+ ' ' +__version__, iconName='listDuplicateNames', width=windowWidth, height=windowHeight)
    
    cmds.columnLayout( adjustableColumn=True )
    cmds.separator( height=20, style='none' )
    cmds.text(label='Those objects names are not uniques' )
    cmds.separator( height=20, style='none' )
    cmds.textScrollList('listDuplicateNames_scrollList')
    
    for l in list:
        cmds.textScrollList('listDuplicateNames_scrollList', e=True, append=l)
    
    cmds.separator( height=20, style='double' )

    cmds.button( label='Close', height=30, command=('cmds.deleteUI(\"' + window + '\", window=True)') )

    cmds.setParent(upLevel=True)
    cmds.window(window, e=True, width=windowWidth, height=windowHeight)
    cmds.showWindow( window )
