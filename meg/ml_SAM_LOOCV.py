''' Checks whether there is a group difference in the connectivity '''

import numpy as np
import os
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = [3]*5#range(len(band_names))
g1_fname = home+'/data/meg/nv_subjs.txt'
g2_fname = home+'/data/meg/persistent_subjs.txt'
g3_fname = home+'/data/meg/remitted_subjs.txt'
sx_fname = home+'/data/meg/inatt.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home+'/data/meg/sam/'
cmethod = 5
hemi = -1
comb_bands = False
do_mean=False

# list of lists, indicating which ROIs are grouped together, avoiding non-meaningful connections. Set all2all=True if interested in doing each ROI by itself
selected_labels = []
# selected_labels = [10,9,32,24,23,31,30,39,40] #DMN
# selected_labels = [[32,24],[23],[39]] #DMN-select
# selected_labels = [[8], [39, 40, 7]] # dorsal
# selected_labels = [[39,40,41,42], [44,45,46]] #ventral
# selected_labels = [[39], [44,45,46]] #ventral-select
# selected_labels = [[46,9], [8], [44,45,47], [6], [7, 5]] # cognitive control
# selected_labels = [32,24,25,10,11,47] #affective
selected_labels = [1,10,11,17,18,19,2,20,21,22,23,24,25,3,31,32,37,38,39,4,40,41,42,43,44,45,46,47,5,6,7,8,9] #Hillebrand, 33 only had one voxel
# selected_labels = [37,5,39,6,4,46]


fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
if len(g3_fname)>0:
    fid3 = open(g3_fname, 'r')
    g3 = [line.rstrip() for line in fid3]
else:
    g3 = []

res = np.recfromtxt(sx_fname, delimiter='\t')
sx = {}
for rec in res:
    sx[rec[0]] = rec[1]

areas = np.load(home+'/sam/areas.npy')[()]
res = np.load(home+'/sam/rois.npz')
rois = list(res['rois'])
nlabels=len(rois)

if hemi>=0:
    if len(selected_labels)>0:
        brodmann_val = [areas[l][hemi] for l in selected_labels]
    else:
        if hemi==0:
            brodmann_val = rois[1:-1:2]
        else:
            brodmann_val = rois[0:-1:2]
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 
else:
    if len(selected_labels)>0:
        brodmann_val = [i for l in selected_labels for i in areas[l]]
    else:
        brodmann_val = rois
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 

g1_data = [[] for b in bands]
g2_data = [[] for b in bands]
g3_data = [[] for b in bands]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g1_sx = []
g2_sx = []
il = np.tril_indices(nlabels, k=-1)
for s in subjs:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()]
    if not comb_bands:
        nbands = len(bands)
        for bidx,bval in enumerate(bands):
            data = conn[bval][cmethod][:,:].squeeze()
            data = np.delete(data, delme, axis=0)
            data = np.delete(data, delme, axis=1) 
            if do_mean:
                ul = np.triu_indices(nlabels, k=1)
                data[ul] = data[il]
                data = np.mean(data,axis=0)
            else:
                data = data[il]
            if s in g1:
                g1_data[bidx].append(data)
                if bidx==0:
                    g1_subjs.append(s)
                    # g1_sx.append(sx[s])
            elif s in g2:
                g2_data[bidx].append(data)
                if bidx==0:
                    g2_subjs.append(s)
                    # g2_sx.append(sx[s])
            elif s in g3:
                g3_data[bidx].append(data)
                if bidx==0:
                    g3_subjs.append(s)
    else:
        nbands=1
        subj_data = []
        for bidx,bval in enumerate(bands):
            data = conn[bval][cmethod][:,:].squeeze()
            data = np.delete(data, delme, axis=0)
            data = np.delete(data, delme, axis=1)
            if do_mean:
                ul = np.triu_indices(nlabels, k=1)
                data[ul] = data[il]
                data = np.mean(data,axis=0)
            else:
                data = data[il]
            subj_data.append(data) 
        if s in g1:
            g1_data[0].append(np.array(subj_data).flatten())
            g1_subjs.append(s)
            # g1_sx.append(sx[s])
        elif s in g2:
            g2_data[0].append(np.array(subj_data).flatten())
            g2_subjs.append(s)
            # g2_sx.append(sx[s])
        elif s in g3:
            g3_data[0].append(np.array(subj_data).flatten())
            g3_subjs.append(s)

res = []

sens = []
spec = []
f1 = []
acc = []
prec = []
all_weights = []
for b in range(nbands):
    print band_names[bands[b]]
    X = np.vstack([np.array(g3_data[b]), np.array(g2_data[b])])
    y = np.hstack([np.zeros([len(g3_data[b])]),np.ones([len(g2_data[b])])])
    
    from sklearn import preprocessing
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
    from sklearn.grid_search import GridSearchCV

    imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)

    X = preprocessing.scale(X)

    from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score, recall_score, precision_score, accuracy_score
    nfeats = X.shape[1]
    nobs = X.shape[0]
    
    cs = [.1, .25, .5, .75, 1]#np.arange(.1,10,.5)
    cv = LeaveOneOut(nobs)
    inner_cv = LeaveOneOut(nobs-1)
    scores = []
    preds = []
    rand_preds = []
    weights = 0
    for oidx, (train, test) in enumerate(cv):
        print '%d/%d'%(oidx+1,nobs)
        X_train = X[train]
        X_test = X[test]
        y_train = y[train]
        y_test = y[test]
        c_val_scores = []
        for c in cs:
            inner_preds = []
            # clf = SVC(C=1, kernel='linear', class_weight='auto', probability=False)
            clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
            for iidx, (itrain, itest) in enumerate(inner_cv):
                X_inner_train = X_train[itrain]
                X_val = X_train[itest]
                y_inner_train = y_train[itrain]
                y_val = y_train[itest]
                scaler = preprocessing.StandardScaler().fit(X_inner_train)
                X_inner_train = scaler.transform(X_inner_train)
                X_val = scaler.transform(X_val)
                clf.fit(X_inner_train, y_inner_train)
                inner_preds.append(clf.predict(X_val))
            c_val_scores.append(f1_score(y_train, inner_preds, pos_label=1))
        best_c = cs[np.argmax(c_val_scores)]
        # clf = SVC(C=1, kernel='linear', class_weight='auto', probability=False)
        clf = LogisticRegression(C=best_c, penalty="l1", dual=False, class_weight='auto')
        clf.fit(X_train,y_train)
        print 'Best C=%.2f'%(best_c)
        preds.append(clf.predict(X_test))
        weights += np.abs(clf.coef_)
    f1.append(f1_score(y, preds, pos_label=1))
    prec.append(precision_score(y, preds, pos_label=1))
    spec.append(recall_score(y, preds, pos_label=0))
    sens.append(recall_score(y, preds, pos_label=1))
    acc.append((accuracy_score(y, preds)))
    all_weights.append(weights)

nperms=5000
# only compute bal_acc after we have the results for all bands, since it doens't depend on predictions
bal_acc = (np.array(prec)+np.array(spec))/float(2)

def print_scores(f, scores, title, pos_label=1):
    if pos_label is not None:
        rand_scores=[f(y, np.random.permutation(y), pos_label=pos_label) for i in range(nperms)]
    else:
        rand_scores=[f(y, np.random.permutation(y)) for i in range(nperms)]
    pvals = [np.sum(np.array(rand_scores)>=m)/float(nperms) for m in scores]   
    print title, ':', scores
    print title, 'pvals:', pvals

print_scores(f1_score, f1, 'F-score')
print_scores(precision_score, prec, 'Precision')
print_scores(recall_score, sens, 'Sensitivity/recall')
print_scores(recall_score, spec, 'Specificity', pos_label=0)
print_scores(accuracy_score, acc, 'Accuracy', pos_label=None)

rand_score = []
for i in range(nperms):
    rand_preds = np.random.permutation(y)
    rand_score.append((np.array(recall_score(y,rand_preds,pos_label=1))+np.array(recall_score(y,rand_preds,pos_label=0)))/float(2))
pvals = [np.sum(np.array(rand_score)>=m)/float(nperms) for m in bal_acc]
print 'Balanced accuracy:', sens
print 'Balanced accuracy pvals:', pvals

# sens_rand=[recall_score(y, np.random.permutation(y), pos_label=1) for i in range(nperms)]
# pvals = [np.sum(np.array(sens_rand)>=m)/float(nperms) for m in sens]
# print 'Sensitivity:', sens
# print 'Sensitivity pvals:', pvals

