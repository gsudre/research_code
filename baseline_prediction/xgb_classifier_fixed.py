from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import sys
import os
import multiprocessing


home = os.path.expanduser('~')

train_fname = sys.argv[1]
test_fname = sys.argv[2]
target = sys.argv[3]
output_dir = sys.argv[4]
myseed = int(sys.argv[5])

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
    train_data = pd.read_csv(train_fname)
    test_data = pd.read_csv(test_fname)

    # remove columns that are all NaNs
    train_data.dropna(axis=1, how='all', inplace=True)
    test_data.dropna(axis=1, how='all', inplace=True)

    train_data.rename(columns={target: 'class'}, inplace=True)
    test_data.rename(columns={target: 'class'}, inplace=True)
    if len(np.unique(data['class'])) == 2:
        train_data['class'] = train_data['class'].map({'improvers': 1, 'nonimprovers': 0})
        test_data['class'] = test_data['class'].map({'improvers': 1, 'nonimprovers': 0})
        scoring='roc_auc'
    else:
        scoring='f1_weighted'


    # it's a feature to be used if it starts with v_
    feature_names = [f for f in train_data.columns if f.find('v_') == 0]

    if myseed < 0:
        make_random = True
        print('Creating random data!!!')
        myseed = -1 * myseed
    else:
        make_random = False

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

    Xtrain = train_data[feature_names].values
    Xtest = test_data[feature_names].values
    ytrain = train_data['class'].values
    ytest = test_data['class'].values
    # use negative seed to randomize the data
    if make_random:
        Xtrain = np.random.uniform(np.min(Xtrain), np.max(Xtrain), Xtrain.shape)
        Xtest = np.random.uniform(np.min(Xtest), np.max(Xtest), Xtest.shape)

    my_search.fit(Xtrain, ytrain)

    report(my_search.cv_results_, n_top=10)

    train_score = my_search.score(Xtrain, ytrain)
    val_score = my_search.score(Xtest, ytest)

    print('Testing: %.2f' % val_score)

    from sklearn.dummy import DummyClassifier
    from sklearn.metrics import roc_auc_score, f1_score
    clf = DummyClassifier(strategy='most_frequent', random_state=myseed)
    clf.fit(Xtrain, ytrain)
    preds = clf.predict(Xtest)
    if len(np.unique(data['class'])) == 2:
        score_majority = roc_auc_score(ytest, preds)
    else:
        score_majority = f1_score(ytest, preds, average='weighted')
    clf = DummyClassifier(strategy='stratified', random_state=myseed)
    clf.fit(Xtrain, ytrain)
    preds = clf.predict(Xtest)
    if len(np.unique(data['class'])) == 2:
        score_strat = roc_auc_score(ytest, preds)
    else:
        score_strat = f1_score(ytest, preds, average='weighted')

    print('Dummy majority: %.2f' % score_majority)
    print('Dummy stratified: %.2f' % score_strat)

    phen = phen_fname.split('/')[-1].replace('.csv', '')
    out_fname = '%s_%s_%d' % (phen, target, myseed)
    if make_random:
        fout = open('%s/classification_results_RND_XGB_%s.csv' % (output_dir, phen), 'a')
    else:
        fout = open('%s/classification_results_XGB_%s.csv' % (output_dir, phen), 'a')
    fout.write('%s,%f,%f,%f,%f\n' % (out_fname, train_score, val_score,
                               score_majority, score_strat))
    fout.close()