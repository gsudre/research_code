import os
home = os.path.expanduser('~')
import numpy as np
from scipy import stats
import nibabel as nb

freq_band = '65-100'
res_dir = home + '/data/meg/ica/'
data_dir = home + '/data/meg/sam_narrow_8mm/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
group_fname = subjs_fname  # home + '/data/meg/nv_subjs.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

init_sources = 20500
init_time = 38500

# determines what ICs need to be flipped so that the final Z-value of the IC has the highest value as positive. This can only be done after the z-maps are done. So, in other words, htis process needs to be done twice.
flip = {'1-4': [2], '4-8': [5, 6, 7, 11, 15], '8-13': [2, 3, 4, 6],
        '13-30': [1, 2, 3, 7, 15, 16, 17], '30-55': [0, 7],
        '65-100': [1, 2, 5, 8, 9, 10]}

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

# Flipping ICs so that the main network blobs are always positive
for c in flip[freq_band]:
    ICs[c, :] = -1 * ICs[c, :]

# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    if s in subj_group:
        print s
        subj_data = ds_data[s]
        idx = np.arange(cnt, cnt + subj_data.shape[1])

        # do per-subject regression
        for c in range(ncomps):
            # assumes a 1-1 map between ICs and concatenated group data!
            d = np.zeros(img.get_data().shape + tuple([5]))  # all linregress
            for v in range(nsources):
                res = np.array(stats.linregress(subj_data[v, :], ICs[c, idx]))
                # invert p-value to 1-p
                res[3] = 1 - res[3]
                d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), :] = res
            fname = res_dir + '%s_%s_alwaysPositive_IC%02d.nii' % (s, freq_band, c)
            nb.save(nb.Nifti1Image(d, img.get_affine()), fname)

        # concatenate data for entire group regression later
        all_data[0:nsources, idx] = subj_data
        cnt += subj_data.shape[1]
all_data = all_data[:nsources, :cnt]

# do group regression
for c in range(ncomps):
    # assumes a 1-1 map between ICs and concatenated group data!
    d = np.zeros(img.get_data().shape + tuple([5]))  # all linregress
    for v in range(nsources):
        res = np.array(stats.linregress(all_data[v, :], ICs[c, :]))
        # invert p-value to 1-p
        res[3] = 1 - res[3]
        d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), :] = res
    fname = res_dir + 'catAllSubjs_%s_alwaysPositive_IC%02d.nii' % (freq_band, c)
    nb.save(nb.Nifti1Image(d, img.get_affine()), fname)
