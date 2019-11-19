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

# phen_fname = home + '/data/baseline_prediction/dti_rd_OD0.95_11052019.csv'
# target = 'SX_HI_groupStudy'
# output_dir = home + '/data/tmp/'
# myseed = 42

# 16 if running it locally
ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '16'))

# Utility function to report best scores
def report(results, n_top=3):
    for i in range(1, n_top + 1):
        candidates = np.flatnonzero(results['rank_test_score'] == i)
        for candidate in candidates:
            print("Model with rank: {0}".format(i))
            print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
                  results['mean_test_score'][candidate],
                  results['std_test_score'][candidate]))
            print("Parameters: {0}".format(results['params'][candidate]))
            print("")


if __name__ == '__main__':
    # multiprocessing.set_start_method('forkserver')
    data = pd.read_csv(phen_fname)

    # remove columns that are all NaNs
    data.dropna(axis=1, how='all', inplace=True)

    data.rename(columns={target: 'class'}, inplace=True)
    if len(np.unique(data['class'])) == 2:
        data['class'] = data['class'].map({'improvers': 1, 'nonimprovers': 0})
        scoring='roc_auc'
    else:
        scoring='f1_weighted'
    
    print(data['class'].value_counts())

    # it's a feature to be used if it starts with v_
    feature_names = [f for f in data.columns if f.find('v_') == 0]

    if myseed < 0:
        make_random = True
        print('Creating random data!!!')
        myseed = -1 * myseed
    else:
        make_random = False

    y = data['class'].values
    training_indices, testing_indices = train_test_split(data.index,
                                                            stratify = y, train_size=0.65,
                                                            test_size=0.35,
                                                            random_state=myseed)

    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC, LinearSVC
    from sklearn.decomposition import PCA
    from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
    from scipy.stats import randint as sp_randint
    from sklearn.feature_selection import SelectPercentile, f_classif, VarianceThreshold, SelectFpr
    from sklearn.model_selection import StratifiedShuffleSplit
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    from scipy.stats import uniform, randint
    
    estimators = [('clf', XGBClassifier(random_state=myseed,
                                    nthread=ncpus, eval_metric='auc'))]
    pipe = Pipeline(estimators)
    params = {
        "clf__colsample_bytree": uniform(0.5, 0.45),
        "clf__gamma": uniform(0, 0.5),
        "clf__learning_rate": uniform(0.01, 0.2), # default 0.1 
        "clf__max_depth": randint(3, 6), # default 3
        "clf__n_estimators": randint(100, 150), # default 100
        "clf__subsample": uniform(0.6, 0.3),
        'clf__min_child_weight': randint(1,10),
        'clf__scale_pos_weight': [1, (np.sum(y[training_indices]==0) / np.sum(y[training_indices]==1))],
        'clf__reg_lamba': [1e-5, 1e-2, 0.1, 1, 100],
        'clf__reg_alpha': [1e-5, 1e-2, 0.1, 1, 100],
    }
    my_search = RandomizedSearchCV(pipe, param_distributions=params, 
                                   random_state=myseed, n_iter=500, cv=3,
                                   verbose=1, n_jobs=1,
                                   return_train_score=True, iid=False)
    
    X = data[feature_names].values

    # use negative seed to randomize the data
    if make_random:
        X = np.random.uniform(np.min(X), np.max(X), X.shape)

    my_search.fit(X[training_indices], y[training_indices])

    report(my_search.cv_results_, n_top=5)

    # train_score = my_search.score(X[training_indices], y[training_indices])
    candidates = np.flatnonzero(my_search.cv_results_['rank_test_score'] == 1)
    idx = candidates[0]
    train_score = my_search.cv_results_['mean_test_score'][idx]
    train_sd = my_search.cv_results_['std_test_score'][idx]
    val_score = my_search.score(X[testing_indices], y[testing_indices])

    print('Training: %.2f (%.2f)' % (train_score, train_sd))
    print('Testing: %.2f' % val_score)

    from sklearn.dummy import DummyClassifier
    from sklearn.metrics import roc_auc_score, f1_score
    clf = DummyClassifier(strategy='most_frequent', random_state=myseed)
    clf.fit(X[training_indices], y[training_indices])
    preds = clf.predict(X[testing_indices])
    if len(np.unique(data['class'])) == 2:
        score_majority = roc_auc_score(y[testing_indices], preds)
    else:
        score_majority = f1_score(y[testing_indices], preds, average='weighted')
    clf = DummyClassifier(strategy='stratified', random_state=myseed)
    clf.fit(X[training_indices], y[training_indices])
    preds = clf.predict(X[testing_indices])
    if len(np.unique(data['class'])) == 2:
        score_strat = roc_auc_score(y[testing_indices], preds)
    else:
        score_strat = f1_score(y[testing_indices], preds, average='weighted')

    print('Dummy majority: %.2f' % score_majority)
    print('Dummy stratified: %.2f' % score_strat)

    phen = phen_fname.split('/')[-1].replace('.csv', '')
    out_fname = '%s_%s_%d' % (phen, target, myseed)
    if make_random:
        fout = open('%s/classification_results_RND_XGB_65-35_%s.csv' % (output_dir, phen), 'a')
    else:
        fout = open('%s/classification_results_XGB_65-35_%s.csv' % (output_dir, phen), 'a')
    fout.write('%s,%f,%f,%f,%f\n' % (out_fname, train_score, val_score,
                               score_majority, score_strat))
    fout.close()