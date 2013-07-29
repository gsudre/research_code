''' Creates labels baased on the MNI teamplate descriptions that Philip sent me for the subcortical analysis '''
import mne
import numpy as np
import env

fname = '/Users/sudregp/Documents/surfaces/thalamus_right_morpho_labels_test.txt'
hemi = 'rh'

labels = np.genfromtxt(fname)
for label_num in np.unique(labels):
    label_name = env.fsl + 'mni/label/' + hemi + '.' + str(int(label_num))
    label = mne.Label(np.nonzero(labels == label_num)[0], hemi=hemi)
    mne.write_label(label_name, label)
