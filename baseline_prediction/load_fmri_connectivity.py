import pandas as pd
import numpy as np
import os
from sklearn import decomposition, preprocessing
from sklearn import feature_selection, metrics
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier


def get_baseline_scans(df, min_time_diff=0):
    # figure out the baseline scans. For 9 months, min_time_diff = .75
    keep = []
    for mrn in np.unique(df.MRN):
        mrn_ages = df[df.MRN == mrn].age_at_scan
        if len(mrn_ages) > 1 and np.diff(np.sort(mrn_ages))[0] < min_time_diff:
            print 'ERROR: Scans for %d are not more ' % mrn + \
                  'than %.2f apart!' % min_time_diff
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
csv_dir = home + '/data/baseline_prediction/'
data_dir = home + '/data/baseline_prediction/fmri/rois_spheres/'

# open main file to get list of subjects and their classes
gf = pd.read_csv(csv_dir + 'gf_final_long_aug11.csv')
group_cols = ['HI_linear_4groups_recoded', 'HI_quad_3groups_recoded',
              'inatt_quad_3groups_recoded', 'inatt_linear_3groups_recoded',
              'HI_linear_3groups_recoded']

# open dataset and see which subjects have that type of data
fmri_scans = pd.read_csv(csv_dir + 'fmri/good_scans_filtered.csv')
fmri_base_scans = get_baseline_scans(fmri_scans, min_time_diff=.75)

# mats = []
# for m, s in zip(fmri_base_scans.MRN, fmri_base_scans.mask_id):
#     print s
#     fname = data_dir + '%04d_maskAve.1D' % s
#     roi_data = np.genfromtxt(fname)
#     subj_data = np.arctanh(np.corrcoef(roi_data.T))
#     idx = np.triu_indices_from(subj_data, k=1)
#     mats.append([m] + list(subj_data[idx]))
# corr_mats = np.array(mats, dtype='float32')

corr_mats = np.load(data_dir + '/spheres_corr.npz')[()]

data = pd.DataFrame(corr_mats,
                    columns=['MRN'] +
                    ['conn%d' % i for i in range(1, corr_mats.shape[1])])
fmri_columns = data.columns[1:]

subj_groups = get_unique_gf(gf)
fmri_with_labels = pd.merge(data, subj_groups, left_on='MRN', right_on='ID')

X = np.array(fmri_with_labels[fmri_columns])
y = np.array(fmri_with_labels[group_cols])
