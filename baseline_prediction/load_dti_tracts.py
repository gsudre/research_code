import pandas as pd
import numpy as np
import pylab as pl
import os
from sklearn import decomposition, preprocessing
from sklearn import feature_selection, metrics
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedShuffleSplit
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier


def get_baseline_scans(df, min_time_diff=0):
    # figure out the baseline scans. For 9 months, min_time_diff = .75
    keep = []
    for mrn in np.unique(df.MRN):
        mrn_ages = df[df.MRN == mrn].age_at_scan
        if len(mrn_ages) > 1 and np.diff(mrn_ages)[0] < min_time_diff:
            print 'ERROR: Scans for %d are not more ' + \
                  'than %.2f apart!' % (mrn, min_time_diff)
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
# csv_dir = '/Volumes/Shaw/baseline_prediction/'
csv_dir = home + '/data/baseline_prediction/'

# open main file to get list of subjects and their classes
gf = pd.read_csv(csv_dir + 'gf_final_long_aug11.csv')
group_cols = ['HI_linear_4groups_recoded', 'HI_quad_3groups_recoded',
              'inatt_quad_3groups_recoded', 'inatt_linear_3groups_recoded',
              'HI_linear_3groups_recoded']

dti_data = pd.read_csv(csv_dir + 'dti_tortoiseExported_meanTSA_12092016.csv')
dti_columns = ['%s_%s_%s' % (i, j, k) for i in ['FA', 'AD', 'RD']
               for j in ['left', 'right']
               for k in ['cst', 'ifo', 'ilf', 'slf', 'unc']] + \
               ['%s_cc' % i for i in ['FA', 'AD', 'RD']]

dti_base_data = get_baseline_scans(dti_data)
subj_groups = get_unique_gf(gf)
dti_with_labels = pd.merge(dti_base_data, subj_groups, left_on='MRN',
                           right_on='ID')

X = np.array(dti_with_labels[dti_columns])
y = np.array(dti_with_labels[group_cols])


def classify(X, y, verbose=False, nfolds=2, dim_red=None,
             n_components=[5, 10, 20], scale=True, fs=None,
             njobs=1,
             LR_C=[.01, .1, 1, 10, 100], LR_class_weight=[None, 'balanced'],
             SVC_C=[.01, .1, 1, 10, 100], SVC_class_weight=[None, 'balanced'],
             SVC_kernels=['rbf', 'linear', 'poly'],
             n_estimators=[10, 20, 30], max_features=['auto', 'log2', None],
             **kwargs):

    # spit out to the screen the function parameters, for logging
    if verbose:
        import inspect
        frame = inspect.currentframe()
        args, _, _, values = inspect.getargvalues(frame)
        print 'function name "%s"' % inspect.getframeinfo(frame)[2]
        for i in args[2:]:
            print "    %s = %s" % (i, values[i])

    # prepare configuration for cross validation test harness
    num_instances = len(X)
    seed = 8

    # prepare models
    models = []
    # all these support multiclass:
    # http://scikit-learn.org/stable/modules/multiclass.html
    models.append(('LR', LogisticRegression(multi_class='multinomial',
                                            solver='newton-cg'),
                   {"C": LR_C,
                    "class_weight": LR_class_weight}))
    models.append(('LDA', LinearDiscriminantAnalysis(), {}))
    models.append(('RndFor', RandomForestClassifier(),
                   {'n_estimators': n_estimators,
                    'max_features': max_features}))
    models.append(('NB', GaussianNB(), {}))
    models.append(('SVC', SVC(),
                   {"C": SVC_C,
                    "class_weight": SVC_class_weight,
                    'kernel': SVC_kernels}))
    models.append(('Most frequent', DummyClassifier(strategy='most_frequent'),
                   {}))
    models.append(('Stratified', DummyClassifier(strategy='stratified'), {}))

    # spit out to the screen the parameters to be tried in each classifier
    if verbose:
        print 'Trying these parameters:'
        for m in models:
            print m[0], ':', m[2]

    # evaluate each model in turn
    results = []
    names = []
    scoring = 'accuracy'
    for name, model, params in models:
        # need to create the CV objects inside the loop because they get used
        # and not get reset!
        inner_cv = StratifiedShuffleSplit(n_splits=nfolds, test_size=.1,
                                          random_state=seed)
        outer_cv = StratifiedShuffleSplit(n_splits=nfolds, test_size=.1,
                                          random_state=seed)
    #     # do this if no shuffling is wanted
    #     inner_cv = StratifiedKFold(n_splits=num_folds, random_state=seed)
    #     outer_cv = StratifiedKFold(n_splits=num_folds, random_state=seed)
        steps = [('clf', model)]
        pipe_params = {}
        for key, val in params.iteritems():
            key_name = 'clf__%s' % key
            pipe_params[key_name] = val
        if fs == 'l1':
            lsvc = LinearSVC(C=0.1, penalty="l1", dual=False)
            fs = feature_selection.SelectFromModel(lsvc)
        elif fs == 'rfe':
            fs = feature_selection.RFE(estimator=model)
            pipe_params['feat_sel__n_features_to_select'] = n_components
        steps = [('feat_sel', fs)] + steps
        if dim_red is not None:
            if dim_red == 'pca':
                dr = decomposition.PCA()
                pipe_params['dim_red__n_components'] = n_components
            elif dim_red == 'ica':
                dr = decomposition.FastICA()
                pipe_params['dim_red__n_components'] = n_components
            steps = [('dim_red', dr)] + steps
        if scale:
            steps = [('scale', preprocessing.RobustScaler())] + steps

        pipe = Pipeline(steps)
        cv_results = []
        cnt = 0
        for train_idx, test_idx in outer_cv.split(X, y):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            opt_model = GridSearchCV(estimator=pipe, param_grid=pipe_params,
                                     verbose=0, n_jobs=njobs, cv=inner_cv)
            opt_model.fit(X_train, y_train)
            if verbose:
                if len(params.keys()) > 0:
                    print 'Best paramaters for', name, \
                          ' (%d/%d):' % (cnt + 1, outer_cv.n_splits)
                    print opt_model.best_params_
            predictions = opt_model.predict(X_test)
            cv_results.append(metrics.accuracy_score(y_test, predictions))
            cnt += 1
        results.append(cv_results)
        names.append(name)
    if verbose:
        print '\n======'
        for model, res in zip(models, results):
            msg = "%s: %f (%f)" % (model[0], np.mean(res), np.std(res))
            print(msg)
        print 'Chance: %f' % (1 / float(len(np.unique(y))))
        print '======\n'
    return results, models
