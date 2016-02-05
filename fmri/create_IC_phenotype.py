# Creates phenotype files for each IC based on the NIFTI files
import nibabel as nb
import numpy as np
import os


# get base phenotype file
home = os.path.expanduser('~')
phen_dir = home + '/data/solar_paper_v2/'
phen_fname = 'fmri_familySibs2min.csv'
mask_dir = home + '/data/fmri_example11_all/'
ica_dir = home + '/data/fmri_example11_all/dual_elbow/'
keys = ['ID', 'sex', 'scanner', 'age', 'maskid', 'famid',
        'inatt', 'HI']

phen = np.recfromtxt(phen_dir + phen_fname, delimiter=',', names=True)
mask = nb.load(mask_dir + '/brain_mask_555.nii')
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)

# for each subject in ped
for r, rec in enumerate(phen):
    print 'Line %d / %d' % (r + 1, len(phen))
    fname = '%s/dr_stage2_%04d_Z.nii.gz' % (ica_dir, int(rec['maskid']))
    img = nb.load(fname)
    subj_data = img.get_data()
    img_dims = subj_data.shape
    nics = img_dims[-1]
    subj_data = subj_data.reshape([subj_data.size / nics, -1])
    for ic in range(nics):
        fname = phen_dir + 'phen_IC%02d.csv' % ic
        # if it's the first record, create the files with the headers
        if r == 0:
            fid = open(fname, 'w')
            fid.write(','.join(keys) + ',')
            fid.write(','.join(['v%d' % i for i in range(nvoxels)]) + '\n')
            fid.close()
        ic_data = subj_data[gv, ic]
        fid = open(fname, 'a')
        fid.write(','.join([str(rec[key]) for key in keys]) + ',')
        fid.write(','.join(['%.4f' % d for d in ic_data]) + '\n')
        fid.close()
