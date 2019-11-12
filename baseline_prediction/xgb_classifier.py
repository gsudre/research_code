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
                                                            stratify = y, train_size=0.8,
                                                            test_size=0.2,
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
    
    params = {#'clf__n_estimators': [100, 200, 500],
    #           'clf__max_depth': [4,5,6,7,8],
    #           'clf__learning_rate':[.001, .01, .1, .3, .5, .7, .9],
              'selector__alpha': [.01, .03, .05, .07, .1, 1]}
    
    estimators = [('some_variace', VarianceThreshold(threshold=0)),
                  ('unit_variance', StandardScaler()),
                    ('selector', SelectFpr(f_classif)),
                  ('clf', XGBClassifier(random_state=myseed,
                                        nthread=ncpus))]
    pipe = Pipeline(estimators)
    ss = StratifiedShuffleSplit(n_splits=100, test_size=0.2, random_state=myseed)
    my_search = GridSearchCV(pipe, cv=ss, iid=False, param_grid=params,
                                   refit=True, verbose=1, scoring=scoring, n_jobs=1)

    X = data[feature_names].values

    # use negative seed to randomize the data
    if make_random:
        X = np.random.uniform(np.min(X), np.max(X), X.shape)

    my_search.fit(X[training_indices], y[training_indices])

    report(my_search.cv_results_, n_top=10)

    train_score = my_search.score(X[training_indices], y[training_indices])
    val_score = my_search.score(X[testing_indices], y[testing_indices])

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
        fout = open('%s/classification_results_RND_RF_%s.csv' % (output_dir, phen), 'a')
    else:
        fout = open('%s/classification_results_RF_%s.csv' % (output_dir, phen), 'a')
    fout.write('%s,%f,%f,%f,%f\n' % (out_fname, train_score, val_score,
                               score_majority, score_strat))
    fout.close()