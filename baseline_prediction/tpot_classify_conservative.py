from tpot import TPOTClassifier, config
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import sys
import os
import multiprocessing


home = os.path.expanduser('~')

phen_fname = sys.argv[1]
target = sys.argv[2]
output_dir = sys.argv[3]
myseed = int(sys.argv[4])

# phen_fname = home + '/data/baseline_prediction/dti_JHUtracts_ADRDonly_OD0.95.csv'
# target = 'SX_HI_groupStudy'
# features_fname = home + '/data/baseline_prediction/ad_rd_vars.txt'
# output_dir = home + '/data/tmp/'
# myseed = 42

ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '16'))

if __name__ == '__main__':
    multiprocessing.set_start_method('forkserver')
    data = pd.read_csv(phen_fname)
    data.rename(columns={target: 'class'}, inplace=True)
    data['class'] = data['class'].map({'improvers': 1, 'nonimprovers': 0})
    print(data['class'].value_counts())

    feature_names = [f for f in data.columns if f.find('v_') == 0]

    target_class = data['class'].values
    training_indices, validation_indices = train_test_split(data.index,
                                                            stratify = target_class, train_size=0.65,
                                                            test_size=0.35,
                                                            random_state=myseed)

    # removing some warnings by hard coding parameters in the dictionary
    my_config = {     
        'sklearn.svm.LinearSVC': {
            'penalty': ["l1", "l2"],
            'loss': ["hinge", "squared_hinge"],
            'dual': [True, False],
            'tol': [1e-5, 1e-4, 1e-3, 1e-2, 1e-1],
            'C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20., 25.],
            'class_weight': [None, 'balanced']
        },

        'sklearn.linear_model.LogisticRegression': {
            'penalty': ["l1", "l2"],
            'C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20., 25.],
            'dual': [True, False],
            'solver': 'bfgs',
            'class_weight': [None, 'balanced']
        },
    }

    X = data[feature_names].values

    # # quick estimator for testing
    # tpot = TPOTClassifier(verbosity=2, max_time_mins=2, max_eval_time_mins=0.04, population_size=40, n_jobs=ncpus, use_dask=False)

    tpot = TPOTClassifier(n_jobs=ncpus, random_state=myseed, verbosity=2,
    						config_dict=my_config, use_dask=False,  scoring='roc_auc')


    # perform the fit in this context manager
    tpot.fit(X[training_indices], target_class[training_indices])

    ### after
    phen = phen_fname.split('/')[-1].replace('.csv', '')
    out_fname = '%s_%s_%d' % (phen, target, myseed)
    tpot.export('%s/%s_tpot_pipeline.py' % (output_dir, out_fname))

    train_score = tpot.score(X[training_indices],
                             target_class[training_indices])
    val_score = tpot.score(X[validation_indices],
                           target_class[validation_indices])

    fout = open('%s/classification_results_%s.csv' % (output_dir, phen), 'a')
    fout.write('%s,%f,%f\n' % (out_fname, train_score, val_score))
    fout.close()
