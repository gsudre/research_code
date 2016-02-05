''' Generates correlations toa given seed for all subjects. Saves it as a STC file where each time point is a different subject, but it works because they have all previously morphed to fsaverage. '''

import mne
import numpy as np
from scipy import stats

# seed = [-10, -35, 2]  #JAMA, ACC
# seed = [-53, -48, 20]  #JAMA, TPJ
# seed = [-37, -18, 1]  #JAMA, VFC
# seed = [-27, -58, 49]  #JAMA, IPS
# seed = [-24, -13, 51]  #JAMA, FEF
# seed = [-36, 27, 29]  #JAMA, DLPFC
# seed = [-7, -60, 21]  #JAMA, precuneus
seed = [41, -25, 49]  # Brooks 2011, motor
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/aligned_subjs.txt'
data_dir = '/Users/sudregp/data/meg/'
dir_out = '/Users/sudregp/data/results/meg/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

# find closest source to seed
if seed[0] < 0:
    hemis = 0  # LH
else:
    hemis = 1  # RH
# important to do this by source, because not every vertex has a source
fname = data_dir + 'morphed-lcmv-%dto%d-'%(bands[0][0],bands[0][1]) + subjs[0]
stc = mne.read_source_estimate(fname)
# this is what we get when we read in the fsaverage subject
coord = mne.vertex_to_mni(vertices=stc.vertno[hemis],hemis=hemis,subject='fsaverage')
dist = np.sqrt((coord[:,0] - seed[0])**2 + (coord[:,1] - seed[1])**2 + (coord[:,2] - seed[2])**2)
seed_src = np.argmin(dist) + hemis*len(stc.lh_vertno)
print 'Distance to seed: %.2fmm'%np.min(dist)

# for each band, compute subject-based correlation map
for l_freq, h_freq in bands:
    subj_corrs = []
    print 'Band %d to %d Hz'%(l_freq, h_freq)
    cnt=0
    for s in subjs:
        print cnt+1, '/', len(subjs)
        fname = data_dir + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + s
        stc = mne.read_source_estimate(fname)
        nverts = stc.data.shape[0]
        cor = []
        # this loop is faster than computing the entire mirror matrix
        for j in range(nverts):
            # need to scale up the values so they don't result in numerical error when computing correlation
            cor.append(stats.pearsonr(10**16*stc.data[seed_src,:], 10**16*stc.data[j,:])[0])
        cnt+=1
        subj_corrs.append(cor)

    # save maps of pvalues
    res = mne.SourceEstimate(np.asarray(subj_corrs).T,[stc.lh_vertno,stc.rh_vertno],0,1,subject='fsaverage')
    res.save(dir_out + 'corrs-seed%d-%dto%d'%(seed_src,l_freq,h_freq))
