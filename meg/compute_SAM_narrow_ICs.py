# Script to calculate ICA on SAM narrow bands
# by Gustavo Sudre, July 2014
import numpy as np
import mne
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg
from scipy import stats
from sklearn.decomposition import FastICA
from sklearn.preprocessing import Imputer

def write2afni(vals, fname):
    template_dir = home+'/data/meg/sam_narrow_5mm/'
    data = np.genfromtxt(template_dir + '/voxelsInBrain.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data = np.hstack([data[:, :3], vals])
    np.savetxt(fname, data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat '+fname+ ' | 3dUndump -master '+template_dir+'/TT_N27_555+tlrc -ijk -datum float -prefix '+fname+' -overwrite -')


def export_afni_maps(maps, fname):
    nmaps = len(maps)
    tmp_fname = '/tmp/tmp'
    cat_str = '' 
    for i in range(nmaps):
        write2afni(maps[i], tmp_fname+'_'+str(i))
        cat_str += tmp_fname+'_'+str(i)+'+tlrc '
    os.system('3dTcat -overwrite -prefix '+fname+' '+cat_str)


# band = [1, 4]  #[[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
window_length=13.65  #s
fifs_dir = home + '/data/meg/rest/' #'/mnt/neuro/MEG_data/fifs/rest/'
out_dir = home + '/data/meg/sam_narrow_5mm/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
group_fname = home + '/data/meg/nv_subjs.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()    

init_sources = 20500
init_time = 38500

# create huge array so we can add all the data and then resize it appropriately
all_data = np.empty([init_sources, init_time])
all_data[:] = np.nan
cnt = 0

# open the saved files with the downsampled data
print 'Loading data...', band
ds_data = np.load(out_dir + '/downsampled_evelopes_%d-%d.npy'%(band[0],band[1]))[()]

print 'Concatenating subjects...'
fid = open(group_fname, 'r')
subj_group = [line.rstrip() for line in fid]
fid.close()
nsources = ds_data.values()[0].shape[0]
# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    if s in subj_group:
        subj_data = ds_data[s]
        all_data[0:nsources, cnt:(cnt+subj_data.shape[1])] = subj_data
        cnt += subj_data.shape[1]
all_data = all_data[:nsources, :cnt]

# # remove sources that have NaNs for at least one subject
# delme = np.nonzero(np.isnan(np.sum(all_data,axis=1)))[0]
# all_data = np.delete(all_data,delme,axis=0)

# replace the NaN sources by the mean over all sources... heuristics so that we don't lose too many sources because of one particular subject
imp = Imputer(missing_values='NaN', strategy='mean', axis=0)
imp = imp.fit(all_data)
all_data = imp.transform(all_data)
delme = []

# applying ICA and figuring out how each IC scores
print 'Applying FastICA, sources: %d original, %d estimated, time: %d'%(nsources, all_data.shape[0], all_data.shape[1])
ica = FastICA(n_components=25, random_state=0)
ICs = ica.fit_transform(all_data.T).T

corr_ICs = []
for i in range(ICs.shape[0]):
    print 'Scoring IC', i+1, '/', ICs.shape[0]
    corrs = np.empty([nsources,1])
    corrs[:] = np.nan
    cnt = 0
    for s in range(nsources):
        if s in list(delme):
            corrs[s] = 0
        else:
            r, p = stats.pearsonr(ICs[i,:], all_data[cnt,:])
            corrs[s] = r
            cnt += 1
    corr_ICs.append(corrs)