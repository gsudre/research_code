# Computes the DICE similarity between all MEG networks and all fMRI, including Yeo
import glob
import os
home = os.path.expanduser('~')
import numpy as np
import nibabel as nb


zmeg = [2]#[1, 1.5, 2, 2.5, 3]
zfmri = [2]#[1.5, 2, 2.5, 3]
meg_data = home + '/data/meg/ica/'
fmri_ics_fname = home + '/data/fmri/ica/catAllSubjsZeroFilled_aligned_corr0.80_avgICmap_zscore.nii'
mask_fname = home + '/data/fmri/downsampled_444/brain_mask_444.nii'

mask = nb.load(mask_fname)
gv = mask.get_data().astype(bool)
nvoxels = np.sum(gv)

tmp = 0
# for each MEG network
files = glob.glob(meg_data + 'catAllSubjs*alwaysPositive*zscore.nii')
for fname in files:
    print fname
    # upsample it to fMRI grid
    os.system('export AFNI_NIFTI_TYPE_WARN=NO; 3dresample -inset ' + fname + ' -master ' + mask_fname + ' -prefix tmp.nii -overwrite -rmode NN')
    for zm in zmeg:
        print 'zMEG = %.2f' % zm
        # threshold it based on Z score
        img = nb.load('tmp.nii')
        meg_data = img.get_data()[gv]
        meg_idx = np.abs(meg_data) >= zm

        # open each fMRI network
        img = nb.load(fmri_ics_fname)
        fmri_data = img.get_data()[gv, :]
        # threshold it based on zscore
        ics = range(fmri_data.shape[1])
        for zf in zfmri:
            all_dice = []
            for ic in ics:
                fmri_idx = np.abs(fmri_data[:, ic]) >= zf
                # compute overlap
                overlap = np.logical_and(meg_idx, fmri_idx)
                num = 2 * float(np.sum(overlap))
                den = float(np.sum(meg_idx)) + float(np.sum(fmri_idx))
                dice = num / den
                all_dice.append(float(dice))
            best_dice = np.argsort(all_dice)[::-1]
            print 'zFMRI = %.2f; ' % zf + ' | '.join(['fMRI %02d: %.3f' % (ics[i], all_dice[i]) for i in best_dice[:5]])
            if all_dice[22] > tmp:
                tmp = all_dice[22]
                best_net = fname

        # do the same for the Yeo networks
        img = nb.load(home + '/data/fmri/ica/Yeo_liberal_444_combined.nii')
        yeo_data = img.get_data()[gv, :]
        all_dice = []
        ics = range(yeo_data.shape[1])
        for ic in ics:
            fmri_idx = np.abs(yeo_data[:, ic]) == 1
            # compute overlap
            overlap = np.logical_and(meg_idx, fmri_idx)
            num = 2 * float(np.sum(overlap))
            den = float(np.sum(meg_idx)) + float(np.sum(fmri_idx))
            dice = num / den
            all_dice.append(float(dice))
        best_dice = np.argsort(all_dice)[::-1]
        print ' | '.join(['Yeo %02d: %.3f' % (ics[i], all_dice[i]) for i in best_dice[:5]])
        

print '\n\n'

# just to be complete, do the fMRI against Yeo networks as well
img = nb.load(fmri_ics_fname)
fmri_data = img.get_data()[gv, :]
# threshold it based on zscore
ics = range(fmri_data.shape[1])
for ic in ics:
    print 'fMRI IC%02d' % ic
    for zf in zfmri:
        all_dice = []
        fmri_idx = np.abs(fmri_data[:, ic]) >= zf
        nets = range(yeo_data.shape[1])
        for n in nets:
            yeo_idx = np.abs(yeo_data[:, n]) == 1
            # compute overlap
            overlap = np.logical_and(fmri_idx, yeo_idx)
            num = 2 * float(np.sum(overlap))
            den = float(np.sum(yeo_idx)) + float(np.sum(fmri_idx))
            dice = num / den
            all_dice.append(float(dice))
        best_dice = np.argsort(all_dice)[::-1]
        print 'zFMRI = %.2f; ' % zf + ' | '.join(['Yeo %02d: %.3f' % (nets[i], all_dice[i]) for i in best_dice[:5]])
