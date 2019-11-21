import pandas as pd
import numpy as np
import sys
import os
from sklearn.feature_selection import f_classif
import nibabel as nb


home = os.path.expanduser('~')

phen_fname = sys.argv[1]
target = sys.argv[2]
output_dir = sys.argv[3]
mask_fname = int(sys.argv[4])

# phen_fname = home + '/data/baseline_prediction/dti_rd_OD0.95_11052019.csv'
# target = 'SX_HI_groupStudy'
# output_dir = home + '/data/tmp/'
# mask_fname = home + '/data/baseline_prediction/mean_272_fa_skeleton_mask.nii.gz'

data = pd.read_csv(phen_fname)

data.rename(columns={target: 'class'}, inplace=True)
data['class'] = data['class'].map({'improvers': 1, 'nonimprovers': 0})
feature_names = [f for f in data.columns if f.find('v_') == 0]

X = data[feature_names].values
y = data['class'].values

F, pval = f_classif(X, y)

mask = nb.load(mask_fname)
idx = mask.get_data() == 1
res = np.zeros(mask.get_data().shape[:3] + tuple([2]))
res[idx, 0] = F
res[idx, 1] = 1-pval

phen = phen_fname.split('/')[-1].replace('.csv', '')
out_fname = '%s/%s_%s.nii.gz' % (output_dir, phen, target)
nb.save(nb.Nifti1Image(res, mask.affine), out_fname)