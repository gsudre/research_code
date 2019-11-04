from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import sys
import os
import multiprocessing


home = os.path.expanduser('~')

# phen_fname = sys.argv[1]
# target = sys.argv[2]
# features_fname = sys.argv[3]
# output_dir = sys.argv[4]
# myseed = int(sys.argv[5])

phen_fname = home + '/data/baseline_prediction/dti_JHUtracts_ADRDonly_OD0.95.csv'
target = 'SX_HI_groupStudy'
features_fname = home + '/data/baseline_prediction/ad_rd_vars.txt'
output_dir = home + '/data/tmp/'
myseed = 42

ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '2'))

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
    data.rename(columns={target: 'class'}, inplace=True)
    data['class'] = data['class'].map({'improvers': 1, 'nonimprovers': 0})
    print(data['class'].value_counts())

    fid = open(features_fname, 'r')
    feature_names = [line.rstrip() for line in fid]
    fid.close()

    y = data['class'].values
    training_indices, testing_indices = train_test_split(data.index,
                                                            stratify = y, train_size=0.8,
                                                            test_size=0.2,
                                                            random_state=myseed)

    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC
    from sklearn.decomposition import PCA
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.ensemble import RandomForestClassifier
    from scipy.stats import randint as sp_randint

    param_dist = {"clf__max_depth": [3, None],
              "clf__max_features": sp_randint(1, 11),
              "clf__min_samples_split": sp_randint(2, 11),
              "clf__bootstrap": [True, False],
              "clf__criterion": ["gini", "entropy"],
              "clf__n_estimators": [10, 100]}
    
    estimators = [('reduce_dim', PCA()), ('clf', RandomForestClassifier())]
    pipe = Pipeline(estimators)
    n_iter_search = 20
    random_search = RandomizedSearchCV(pipe, param_distributions=param_dist,
                                   n_iter=n_iter_search, cv=5, iid=False)

    X = data[feature_names].values

    random_search.fit(X[training_indices], y[training_indices])

    report(random_search.cv_results_)