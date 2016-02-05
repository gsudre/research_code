
import os
home = os.path.expanduser('~')
import numpy as np
import sys
from scipy import stats
import nibabel as nb

if len(sys.argv) > 2:
    subj, freq_band = sys.argv[1:]
else:
    subj = 'AKMNQNHX'
    freq_band = '1-4'

cthresh = 15  # works as .05/.05 uncorrected for all bands

res_dir = home + '/data/results/graicar/meg/'
# res_dir = home + '/tmp/'
execfile(home + '/research_code/graicar/load_MEG_data.py')

ICs = np.load(res_dir + subj + '_' + freq_band + '_aligned_cc0.70.npz')['average_ICs']
ncomps = len(ICs)
vox_pos = np.genfromtxt(home + '/data/meg/sam_narrow_8mm/voxelsInBrain888.txt', delimiter=' ')
# restrict to only non-zero weight voxels in the brain
vox_pos = vox_pos[gv, :]
img = nb.load(home + '/data/TT_N27_888.nii')
ngv = len(gv)
all_ics = []
all_zics = []
for i in range(ncomps):
    print 'Scoring IC', i + 1, '/', ncomps
    cnt = 0
    corr_ic = [stats.pearsonr(ICs[i, :], data[s, :])[0] for s in range(ngv)]
    # at this point we have the correlation of the IC with each good voxel (non-zero weight). Let's z-score that for thresholding
    zMat = stats.zscore(corr_ic)
    # figure out if the IC needs to be flipped, and whether it should be kept (non-bimodal). To do that we need to clusterize our values, so a .nii is needed

    # The i,j,k in data/meg/sam_narrow_5mm/voxelsInBrain.txt is the same as the i,j,k in the matrix returned by get_data(), so there is no need for masks.
    d = np.zeros(img.get_data().shape)
    for v in range(ngv):
        d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2])] = zMat[v]
    nb.save(nb.Nifti1Image(d, img.get_affine()), home + '/tmp/junk.nii')

    # clusterize and create mask
    os.system('3dclust -noabs -1dindex 0 -1tindex 0 -2thresh -2 2 -dxyz=1 1.01 %d ~/tmp/junk.nii > ~/tmp/clust_junk.1D' % cthresh)

    # check 3dclust output
    clusters = np.genfromtxt(home + '/tmp/clust_junk.1D')
    if clusters.ndim == 1:
        clusters = clusters[np.newaxis, :]
    nclusters = clusters.shape[0]
    print '\tFound %d clusters' % nclusters
    if nclusters > 0:
        sign = np.unique(np.sign(clusters[:, 10]))
        print '\t Sign: ', sign
        if len(sign) == 1:
            if sign[0] < 1:
                print '\tFlipping IC polarity'
                zMat = -1 * zMat
                corr_ic = -1 * np.array(corr_ic)
            all_ics.append(corr_ic)
            all_zics.append(zMat)
        else:
            print '\tBimodal IC: REJECTING!'
    else:
        print '\tNo significant clusters: REJECTING!'

    # cleaning up to not confuse other ICs
    os.system('rm ~/tmp/clust_junk.1D ~/tmp/junk.nii')

nics = len(all_ics)
print 'Writing %d ICs' % nics
d = np.zeros(img.get_data().shape + tuple([nics]))
dz = np.zeros(img.get_data().shape + tuple([nics]))
all_ics = np.array(all_ics)
all_zics = np.array(all_zics)
for v in range(ngv):
    d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), :] = all_ics[:, v]
    dz[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), :] = all_zics[:, v]
fname = res_dir + subj + '_' + freq_band + '_aligned_cc0.70_rmap.nii'
nb.save(nb.Nifti1Image(d, img.get_affine()), fname)
fname = res_dir + subj + '_' + freq_band + '_aligned_cc0.70_zmap.nii'
nb.save(nb.Nifti1Image(dz, img.get_affine()), fname)
