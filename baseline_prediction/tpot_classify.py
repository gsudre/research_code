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
features_fname = sys.argv[3]
output_dir = sys.argv[4]
myseed = int(sys.argv[5])

# phen_fname = home + '/data/baseline_prediction/dti_JHUtracts_ADRDonly_OD0.95.csv'
# target = 'SX_HI_groupStudy'
# features_fname = home + '/data/baseline_prediction/ad_rd_vars.txt'
# output_dir = home + '/data/tmp/'
# myseed = 42

# setting up DASK
ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '2'))

if __name__ == '__main__':
    multiprocessing.set_start_method('forkserver')
    data = pd.read_csv(phen_fname)
    data.rename(columns={target: 'class'}, inplace=True)
    data['class'] = data['class'].map({'improvers': 1, 'nonimprovers': -1})
    print(data['class'].value_counts())

    fid = open(features_fname, 'r')
    feature_names = [line.rstrip() for line in fid]
    fid.close()

    target_class = data['class'].values
    training_indices, validation_indices = train_test_split(data.index,
                                                            stratify = target_class, train_size=0.8,
                                                            test_size=0.2,
                                                            random_state=myseed)

    # removing some warnings by hard coding parameters in the dictionary
    my_config = config.classifier_config_dict
    my_config['sklearn.linear_model.LogisticRegression']['solver'] = 'lbfgs'
    preproc = [v for v in my_config.keys() if v.find('preprocessing') > 0]
    for p in preproc:
        my_config[p]['validate'] = [False]

    X = data[feature_names].values

    # # quick estimator for testing
    # tpot = TPOTClassifier(verbosity=2, max_time_mins=2, max_eval_time_mins=0.04, population_size=40, n_jobs=ncpus, use_dask=False)

    tpot = TPOTClassifier(n_jobs=ncpus, random_state=myseed, verbosity=2,
    						config_dict=my_config, use_dask=False,  scoring='roc_auc')


    # perform the fit in this context manager
    tpot.fit(X[training_indices], target_class[training_indices])

    ### after
    out_fname = '%s_%s_%d' % (phen_fname.split('/')[-1].replace('.csv', ''),
                              target, myseed)
    tpot.export('%s/%s_tpot_pipeline.py' % (output_dir, out_fname))

    train_score = tpot.score(X[training_indices],
                        data.loc[training_indices, 'class'].values)

    val_score = tpot.score(X[validation_indices],
                        data.loc[validation_indices, 'class'].values)
    fout = open('%s/classification_results.csv' % output_dir, 'a')
    fout.write('%s,%f,%f\n' % (out_fname, train_score, val_score))
    fout.close()
