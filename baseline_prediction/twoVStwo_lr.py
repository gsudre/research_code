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
npairs = int(sys.argv[5])

# phen_fname = home + '/data/baseline_prediction/dti_rd_OD0.95_11052019.csv'
# target = 'SX_HI_groupStudy'
# output_dir = home + '/data/tmp/'
# myseed = 42
# npairs = 5

scoring = 'roc_auc'

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

    data[target] = data[target].map({'improvers': 1, 'nonimprovers': 0})

    # get all label1 observation
    l0_rows = np.flatnonzero(data[target]==np.unique(data[target])[0])
    l1_rows = np.setdiff1d(range(data.shape[0]), l0_rows)

    # it's a feature to be used if it starts with v_
    feature_names = [f for f in data.columns if f.find('v_') == 0]

    X = data[feature_names].values
    y = data[target].values

    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC, LinearSVC
    from sklearn.decomposition import PCA
    from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
    from scipy.stats import randint as sp_randint
    from sklearn.feature_selection import SelectPercentile, f_classif, VarianceThreshold, SelectFpr
    from sklearn.model_selection import StratifiedShuffleSplit
    from sklearn.linear_model import LogisticRegression 
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    from scipy.stats import uniform, randint

    params = {'clf__penalty': ["l2"],
            # 'clf__penalty': ["l1", "l2"],
            #   'clf__C': [1e-4, 1e-3, 1e-2, 1e-1, 0.5, 1., 5., 10., 15., 20.,
            #   25.],
                'clf__C': [1e-5, 1e-4, 1e-3, 1e-2],
              'clf__class_weight': [None, 'balanced'],
            #   'selector__alpha': [.01, .05, .1, 1],
            'selector__alpha': [.001, .005, .01, .05],
              }
    
    cnt = 1
    correct = 0
    pairs = [[l0, l1] for l0 in l0_rows for l1 in l1_rows]
    run_pairs = np.random.permutation(len(pairs))[:npairs]

    for i in run_pairs:
        l0, l1 = pairs[i]
        print('training model %d of %d' % (cnt, npairs))
        test_idx = [l0, l1]
        train_idx = np.setdiff1d(range(data.shape[0]), test_idx)
        
        estimators = [('unit_variance', StandardScaler()),
                        ('selector', SelectFpr(f_classif)),
                        ('clf', LogisticRegression(solver='liblinear'))]

        pipe = Pipeline(estimators)
        
        my_search = GridSearchCV(pipe, cv=5, iid=False, param_grid=params,
                                    refit=True, verbose=1,
                                    scoring=scoring, n_jobs=ncpus)

        my_search.fit(X[train_idx], y[train_idx])

        report(my_search.cv_results_, n_top=1)

        preds = my_search.predict_proba(X[test_idx])

        # if the prob of the first test sample being l0 is bigger than
        # the second test sample (true l1), we're good
        if preds[0][0] > preds[1][0]:
            correct += 1

        print('Accuracy: %.2f' % (float(correct)/cnt*100))

        cnt += 1
