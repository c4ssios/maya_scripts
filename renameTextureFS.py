import os
import shutil

#####################################################################
path = '/job/marylou/dev/prop/TreeD/work/nleblanc/mudbox/MAPS/v001'
assetName = 'TreeD'
assetDefinition = 'primary'
assetResolution = 'default'
assetVariant = 'burn'
mapType = 'VDM'
assetColorSpace = 'sRGB'
textureVariant = '00'
mapExtension = "exr"
####################################################################


for f in os.listdir(path+'/'):
    if mapExtension in f:
      
        ext = f[-8:]
      
        newName = assetName + '_' + assetDefinition + '_' + assetResolution + '_' + assetVariant + '_' + mapType + '_' + assetColorSpace + '_' + textureVariant + '.' + ext
        os.rename(path + '/' + f, path + '/' + newName)
