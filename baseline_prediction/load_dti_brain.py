import pandas as pd
import numpy as np
import pylab as pl
import nibabel as nb
import os
import classifier


def get_baseline_scans(df, min_time_diff=0):
    # figure out the baseline scans. For 9 months, min_time_diff = .75
    keep = []
    for mrn in np.unique(df.MRN):
        mrn_ages = df[df.MRN == mrn].age_at_scan
        if len(mrn_ages) > 1 and np.diff(mrn_ages)[0] < min_time_diff:
            print 'ERROR: Scans for %d are not more ' + \
                  'than %.2f apart!' % (mrn, min_time_diff)
            print mrn_ages
        keep.append(np.argmin(mrn_ages))
    df = df.iloc[keep, :].reset_index(drop=True)
    return df


def get_unique_gf(df):
    # returns a gf with one group entry per subject, and only the columns we
    # want
    keep = []
    for mrn in np.unique(df.ID):
        mrn_rows = df[df.ID == mrn]
        # assuming the groups are always constant across MRN entries!
        keep.append(mrn_rows.index[0])
    df = df.iloc[keep, :].reset_index(drop=True)
    rm_cols = [cname for cname in df.columns
               if cname not in group_cols + ['ID']]
    df.drop(rm_cols, axis=1, inplace=True)
    return df

home = os.path.expanduser('~')
# csv_dir = '/Volumes/Shaw/baseline_prediction/'
csv_dir = home + '/data/baseline_prediction/'

# open main file to get list of subjects and their classes
gf = pd.read_csv(csv_dir + 'gf_final_long_aug11.csv')
group_cols = ['group3_HI_quad', 'group3_HI_linear',
              'group3_inatt_linear', 'group3_inatt_quad',
              'group_HI_quad_4gp', 'group_HI_linear_4gp']

dti_data = pd.read_csv(csv_dir + 'dti_tortoiseExported_meanTSA_12092016.csv')
dti_base_data = get_baseline_scans(dti_data)
subj_groups = get_unique_gf(gf)
dti_with_labels = pd.merge(dti_base_data, subj_groups, left_on='MRN',
                           right_on='ID')

# load data for all NIFTI data for all DTI subjects
mask = nb.load(csv_dir + '/dti/mean_fa_skeleton_mask.nii.gz')
idx = mask.get_data() == 1
X = []
for maskid in dti_with_labels['Mask.ID...Scan']:
    img = nb.load(csv_dir + '/dti/%04d_tensor_diffeo_fa.nii.gz' % maskid)
    X.append(img.get_data()[idx])
X = np.array(X)
y = np.array(dti_with_labels[group_cols])
