import os
home = os.path.expanduser('~')
import numpy as np
from scipy import stats
import nibabel as nb

freq_band = '65-100'
ic = 0
res_dir = home + '/data/meg/ica/'
data_dir = home + '/data/meg/sam_narrow_8mm/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
group_fname = home + '/data/meg/nv_subjs.txt'
group_fname = home + '/data/meg/persistent_subjs.txt'
# group_fname = home + '/data/meg/remitted_subjs.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

init_sources = 20500
init_time = 38500

# create huge array so we can add all the data and then resize it appropriately
print 'Creating big static matrix...'
all_data = np.empty([init_sources, init_time])
all_data[:] = np.nan
cnt = 0

# open the saved files with the downsampled data
print 'Loading data...', freq_band
ds_data = np.load(data_dir + '/downsampled_envelopes_' + freq_band + '.npy')[()]

ICs = np.load(res_dir + 'catAllSubjs_' + freq_band + '_aligned_corr0.80.npz')['average_ICs']
ncomps = len(ICs)
vox_pos = np.genfromtxt(home + '/data/meg/sam_narrow_8mm/voxelsInBrain888.txt', delimiter=' ')
img = nb.load(home + '/data/TT_N27_888.nii')

print 'Concatenating subjects...'
fid = open(group_fname, 'r')
subj_group = [line.rstrip() for line in fid]
fid.close()
nsources = ds_data.values()[0].shape[0]
for s in subjs:
    subj_data = ds_data[s]
    idx = np.arange(cnt, cnt + subj_data.shape[1])
    if s in subj_group:
        all_data[0:nsources, idx] = subj_data
        cnt += subj_data.shape[1]
    else:
        ICs = np.delete(ICs, idx, axis=1)
all_data = all_data[:nsources, :cnt]

d = np.zeros(img.get_data().shape + tuple([6]))  # all linregress + zscore of r
all_rs = []
for v in range(nsources):
    res = np.array(stats.linregress(all_data[v, :], ICs[ic, :]))
    # invert p-value to 1-p
    res[3] = 1 - res[3]
    d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), :5] = res
    all_rs.append(res[2])
all_rs = np.array(all_rs)
gv = ~np.isnan(all_rs)
all_rs[gv] = stats.zscore(all_rs[gv])
all_rs[~gv] = 0
for v in range(nsources):
    d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 5] = all_rs[v]
g_name = group_fname.split('/')[-1].split('.')[0]
fname = res_dir + g_name + '_%s_IC%02d.nii' % (freq_band, ic)
nb.save(nb.Nifti1Image(d, img.get_affine()), fname)
