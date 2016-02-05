import mne
import numpy as np
from scipy import stats

seed = 0
band = [1, 4]
hemi = 'left'
nvs_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
adhds_fname = '/Users/sudregp/data/meg/adhd_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
data_dir = '/Users/sudregp/data/meg/'
dir_out = '/users/sudregp/data/meg/'

nfid = open(nvs_fname, 'r')
afid = open(adhds_fname, 'r')
fid = open(subjs_fname, 'r')
adhds = [line.rstrip() for line in afid]
nvs = [line.rstrip() for line in nfid]
subjs = [line.rstrip() for line in fid]

corrs1 = []
corrs2 = []
fname = dir_out + 'corrs-connectednessSeed%d-%s-%dto%d'%(seed,hemi,band[0],band[1])
stc = mne.read_source_estimate(fname)
# subjects were organized in STC according to their order in usable_subjects.txt
for sidx, subj in enumerate(subjs):
    res = stc.data[:,sidx]
    if subj in nvs:
        corrs1.append(np.arctanh(res))
    else:
        corrs2.append(np.arctanh(res))
nverts = corrs1[0].shape[0]
corrs1 = np.array(corrs1)
corrs2 = np.array(corrs2)
val = [stats.ttest_ind(corrs1[:,i],corrs2[:,i]) for i in range(nverts)]
pvals = [i[1] for i in val]
tstats = [i[0] for i in val]
print 'Voxels < .05 uncorrected:', sum(np.array(pvals)<.05)

p_threshold = 0.01
src = mne.setup_source_space(subject='fsaverage',fname=None,spacing='ico5',surface='inflated')
connectivity = mne.spatial_src_connectivity(src)
n1 = corrs1.shape[0]
n2 = corrs2.shape[0]
corrs1 = corrs1.reshape([n1,1,20484])
corrs2 = corrs2.reshape([n2,1,20484])
f_threshold = stats.distributions.f.ppf(1. - p_threshold / 2., n1 - 1, n2 - 1)
T_obs, clusters, cluster_p_values, H0 = clu = mne.stats.spatio_temporal_cluster_test([corrs1, corrs2], connectivity=connectivity, n_jobs=6, threshold=f_threshold, n_permutations=1000)
good_cluster_inds = np.where(cluster_p_values < 0.05)[0]

c=29
X = np.zeros_like(T_obs)
cluster_ts = T_obs[0,clusters[c][1]]
X[0, clusters[c][1]] = cluster_ts
stc2 = mne.SourceEstimate(X.T, vertices=stc.vertno, tmin=0, tstep=0,subject='fsaverage')
brain = stc2.plot(hemi='both',fmin=min(cluster_ts),fmid=np.mean(cluster_ts),fmax=max(cluster_ts))