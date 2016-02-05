''' Generates correlations to connectedness-derived seed for all good subjects. '''

execfile('/Users/sudregp/research_code/meg/ttest_connectedness.py')

import mne
import numpy as np
from scipy import stats

pval_thresh = .05
nverts_thresh = 600
b=3

src = mne.setup_source_space(subject='fsaverage',fname=None,spacing='ico5',surface='inflated')

# X will have the pvalues in 0
X = 1-np.array(all_stats[b][1])[:,None]  # p-values
X[X <= 1-pval_thresh] = 0
pval_stc = mne.SourceEstimate(X, vertices=stc.vertno, tmin=0, tstep=1,subject='fsaverage')
lh_labels, rh_labels = mne.stc_to_label(pval_stc, src=src, smooth=5, connected=True)
# was having problems ot mix p-values and correlations in stc, so let's keep them separated
X = np.empty([pval_stc.data.shape[0], 2])
X[:, 0] = all_stats[b][2][0]
X[:, 1] = all_stats[b][2][1]
corr_stc = mne.SourceEstimate(X, vertices=stc.vertno, tmin=0, tstep=1,subject='fsaverage')

my_txt = ['left','right']
for idx, labels in enumerate([lh_labels, rh_labels]):
    print 'Found %d seeds in %s hemisphere'%(len(labels), my_txt[idx])
    good_seeds = [label for label in labels if len(label.vertices)>nverts_thresh]
    num_sources = [pval_stc.in_label(label).data.shape[0] for label in good_seeds]
    print '%d of those are big enough'%(len(good_seeds))
    for s in range(len(good_seeds)):
        print 'Seed %d: %d sources, mean 1: %.2f, mean 2: %.2f'%(s+1, num_sources[s], 
            np.mean(corr_stc.in_label(good_seeds[s]).data[:,0]),
            np.mean(corr_stc.in_label(good_seeds[s]).data[:,1]))

raw_input('\nPress any key to continue computing maps, or Ctrl+C to quit...')

for idx, labels in enumerate([lh_labels, rh_labels]):
    good_seeds = [label for label in labels if len(label.vertices)>nverts_thresh]
    for sidx, seed_label in enumerate(good_seeds):
        print 'Computing correlation maps for seed', sidx+1

        subj_corrs = []
        for s, subj in enumerate(subjs):  # usable subjects, from ttest script
            print '%d / %d'%(s+1,len(subjs))
            fname = data_dir + 'morphed-lcmv-%dto%d-'%(bands[b][0],bands[b][1]) + subj
            subj_stc = mne.read_source_estimate(fname)
            nverts = subj_stc.data.shape[0]
            seed_signal = np.mean(subj_stc.in_label(seed_label).data,axis=0).T
            cor = []
            # this loop is faster than computing the entire mirror matrix
            for j in range(nverts):
                # need to scale up the values so they don't result in numerical error when computing correlation
                cor.append(stats.pearsonr(10**16*seed_signal, 10**16*subj_stc.data[j,:])[0])
            subj_corrs.append(cor)

        # save maps of pvalues
        res = mne.SourceEstimate(np.asarray(subj_corrs).T,[stc.lh_vertno,stc.rh_vertno],0,1,subject='fsaverage')
        res.save(dir_out + 'corrs-connectednessSeed%d-%s-%dto%d'%(sidx,my_txt[idx],bands[b][0],bands[b][1]))