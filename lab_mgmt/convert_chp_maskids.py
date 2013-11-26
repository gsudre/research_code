''' Quickly creates symbolic links to the CIVET output (20mm smoothing kernel) sent by Francois so that we can map it from CHP mask ids to our own. We avoid copying the data to save storage space. 

    Gustavo Sudre, 11/2013 '''

import numpy as np
import glob
import os
import shutil

# wherever the data resides
dataDir = '/Volumes/neuro/cortical_civet/original_from_francois/'
# wherever the links will be places
ncrDir = '/Volumes/neuro/cortical_civet/ncr_maskids_new/'

# read in mapping file. Needs to CHP mask ids in the first column and NCR mask ids in the second
res = np.recfromcsv('/Volumes/neuro/cortical_civet/chp2ncr.csv', skip_header=1)

maskidDirs = glob.glob(dataDir + '0*')
ncrMaskids = [int(m.split('/')[-1]) for m in maskidDirs]

def copyFiles(myfolder, ncr, chp):
    baseDir = ncrDir + ('/%04.0d/'%ncr)
    stub = '/'.join(myfolder.split('/')[7:])
    # copy over all the files inside the folder with the correct names
    files = glob.glob(myfolder + '/*')
    for fid in files:
        oldName = fid.split('/')[-1]
        # ignore the stupid symlink
        if oldName!='nih_chp_%05.0d_t1.mnc'%chp:
            newName = oldName.replace('%05.0d'%chp,'%04.0d'%ncr)
            shutil.copy(fid,  baseDir + stub + '/' + newName)


def makeFolders(myfolder, ncr, chp):
    os.mkdir(myfolder)
    # for each folder inside the original folder
    copyFolders = glob.glob(dataDir + ('/%05.0d/*' % chp))
    for folder in copyFolders:
        thisFolder = folder.split('/')[-1]
        # create the correct folder in the ncr corresponding folder
        os.mkdir(myfolder + '/' + thisFolder)
        if thisFolder != 'transforms': 
            copyFiles(folder, ncr, chp)
        else:
            moreFolders = glob.glob(dataDir + ('/%05.0d/transforms/*' % chp))
            for mfolder in moreFolders:
                anotherFolder = mfolder.split('/')[-1]
                os.mkdir(myfolder + '/transforms/' + anotherFolder)
                copyFiles(mfolder, ncr, chp)


# for each NCR mask id we found in the data directory
for m in ncrMaskids:
    # check if it's in the mapping file. If so, retrieve its NCR maskid
    for line in res:
        # if it's a valid NCR mask
        if line[0]==m and line[1]>0:
            print 'Working on NCR maskid', line[1]
            # create the correct folder
            targetDir = ncrDir + ('/%04.0d/' % line[1])
            makeFolders(targetDir, line[1], line[0])

