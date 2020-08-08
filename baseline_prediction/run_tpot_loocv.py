import sys
import os
import multiprocessing
from tpot import TPOTClassifier
import pandas as pd
import numpy as np
from sklearn import preprocessing

home = os.path.expanduser('~')

comp = sys.argv[1]
loo = int(sys.argv[2])

ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '16'))

if __name__ == '__main__':
    multiprocessing.set_start_method('forkserver')
    
    X = pd.read_csv('~/tmp/X_%s.csv' % comp)
    y = pd.read_csv('~/tmp/y_%s.csv' % comp)
    enc = preprocessing.OrdinalEncoder()
    enc.fit(y)
    y2 = enc.transform(y).ravel()
    preds = []
    probs = []
    fout = open('/home/sudregp/tmp/%s_loocv.txt' % comp, 'a')
    
    X_test = np.array(X.iloc[loo, :]).reshape(1, -1)
    y_test = y2[loo]
    idx = [j for j in range(len(y2)) if j != loo]
    X_train = X.iloc[idx, :]
    y_train = y2[idx]

    tpot = TPOTClassifier(verbosity=2, random_state=42, scoring='roc_auc',
                          n_jobs=ncpus, use_dask=False)
    tpot.fit(X_train, y_train)
    preds.append(tpot.predict(X_test)[0])
    probs.append(tpot.predict_proba(X_test)[0])
    fout.write('%d,%d,%d,%.3f,%.3f\n' % (loo, y_test, preds[-1],
                                        probs[-1][0], probs[-1][1]))
    fout.close()

    
    
    
    
    
    
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
        # classifiers
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

        # transformers
        'sklearn.decomposition.FastICA': {
            'tol': np.arange(0.0, 1.01, 0.05)
        },

        'sklearn.cluster.FeatureAgglomeration': {
            'linkage': ['ward', 'complete', 'average'],
            'affinity': ['euclidean', 'l1', 'l2', 'manhattan', 'cosine']
        },

        'sklearn.preprocessing.MaxAbsScaler': {
        },

        'sklearn.preprocessing.MinMaxScaler': {
        },

        'sklearn.preprocessing.Normalizer': {
            'norm': ['l1', 'l2', 'max']
        },

        'sklearn.decomposition.PCA': {
            'svd_solver': ['randomized'],
            'iterated_power': range(1, 11)
        },

        'sklearn.preprocessing.RobustScaler': {
        },

        'sklearn.preprocessing.StandardScaler': {
        },

        # selectors
        'sklearn.feature_selection.SelectPercentile': {
            'percentile': range(1, 100),
            'score_func': {
                'sklearn.feature_selection.f_classif': None
            }
        },
    }

    X = data[feature_names].values

    # # quick estimator for testing
    # tpot = TPOTClassifier(verbosity=2, max_time_mins=2, max_eval_time_mins=0.04, population_size=40, n_jobs=ncpus, use_dask=False)

    tpot = TPOTClassifier(n_jobs=ncpus, random_state=myseed, verbosity=2,
    						config_dict=my_config, use_dask=False,  scoring='roc_auc',
                            template=template)


    # perform the fit in this context manager
    tpot.fit(X[training_indices], target_class[training_indices])

    ### after
    phen = phen_fname.split('/')[-1].replace('.csv', '')
    out_fname = '%s_%s_%s_%d' % (phen, target, template, myseed)
    tpot.export('%s/%s_tpot_pipeline.py' % (output_dir, out_fname))

    train_score = tpot.score(X[training_indices],
                             target_class[training_indices])
    val_score = tpot.score(X[validation_indices],
                           target_class[validation_indices])

    fout = open('%s/classification_results_%s.csv' % (output_dir, phen), 'a')
    fout.write('%s,%f,%f\n' % (out_fname, train_score, val_score))
    fout.close()
