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
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier
    from scipy.stats import uniform, randint

    params = {"clf__l1_ratio": np.arange(.1, 1, .1),
              'clf__class_weight': [None, 'balanced'],
            #   'selector__alpha': [.01, .05, .1, 1],
              }
    max_iter=100#10000

    params = {
        "clf__colsample_bytree": uniform(0.5, 0.45),
        "clf__gamma": uniform(0, 0.5),
        "clf__learning_rate": uniform(0.01, 0.2), # default 0.1 
        "clf__max_depth": randint(3, 6), # default 3
        "clf__n_estimators": randint(100, 150), # default 100
        "clf__subsample": uniform(0.6, 0.3),
        'clf__min_child_weight': randint(1,10),
        'clf__scale_pos_weight': [1, float(len(l0_rows)) / len(l1_rows)],
        'clf__reg_lamba': [1e-5, 1e-2, 0.1, 1, 100],
        'clf__reg_alpha': [1e-5, 1e-2, 0.1, 1, 100],
    }
    
    # estimators = [('some_variace', VarianceThreshold(threshold=0)),
    #               ('unit_variance', StandardScaler()),
    #             #   ('reduce_dim', PCA()),
    #                 # ('selector', SelectFpr(f_classif)),
    #             #   ('reduce_dim', PCA()),
    #               ('clf', LogisticRegression(penalty='elasticnet',
    #               solver='saga', max_iter=max_iter))]
    
    cnt = 1
    correct = 0
    for l1 in l1_rows:
        for l0 in l0_rows:
            print('training model %d of %d' % (cnt,
                                               len(l1_rows) * len(l0_rows)))
            test_idx = [l0, l1]
            train_idx = np.setdiff1d(range(data.shape[0]), test_idx)
            
            estimators = [('clf', XGBClassifier(random_state=myseed,
                                        nthread=ncpus, eval_metric='auc'))]
            pipe = Pipeline(estimators)
            
            # ss = StratifiedShuffleSplit(n_splits=100, test_size=0.2,
            #                             random_state=myseed)
            # my_search = GridSearchCV(pipe, cv=ss, iid=False, param_grid=params,
            #                             refit=True, verbose=1,
            #                             scoring=scoring, n_jobs=ncpus)
            
            my_search = RandomizedSearchCV(pipe, param_distributions=params, 
                                   random_state=myseed, n_iter=50, cv=3,
                                   verbose=1, n_jobs=1,
                                   return_train_score=True, iid=False,
                                   scoring=scoring)

            my_search.fit(X[train_idx], y[train_idx])
            preds = my_search.predict_proba(X[test_idx])

            # if the prob of the first test sample being l0 is bigger than
            # the second test sample (true l1), we're good
            if preds[0][0] > preds[1][0]:
                correct += 1
            cnt += 1

            print('Accuracy: %.2f' % (float(correct)/cnt*100))
