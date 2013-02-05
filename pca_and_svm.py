"""
Modeled after the face recognition example in the scikit.learn website

"""

from time import time
import pylab as pl
import numpy as np
from mne import fiff

from sklearn.cross_validation import train_test_split
from sklearn.datasets import fetch_lfw_people
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import RandomizedPCA
from sklearn.svm import SVC

filename = '/Users/sudregp/MEG_data/analysis/rest/good_PSDS.npz'
limits = [[1, 4], [4, 7], [8, 14], [14, 30], [30, 56], [64, 82], [82, 106], [124, 150]]

npzfile = np.load(filename)
psds = npzfile['psds']
adhd = npzfile['adhd']
freqs = npzfile['freqs']

ch_names = npzfile['info'][()]['ch_names']
picks = npzfile['picks'][()]
psd_channels = []
p = picks[::-1]
for i in p:
    psd_channels.append(ch_names.pop(i))
# now, select only the ones we want
look_for = ['M.F']
for sel in look_for:
    picks = fiff.pick_channels_regexp(psd_channels, sel)

band_psd = np.zeros([len(adhd), len(limits)])
for idx, bar in enumerate(limits):
    index = np.logical_and(freqs >= bar[0], freqs <= bar[1])
    band_psd[:, idx] = np.mean(np.mean(psds[:, :, index], axis=2), axis=1)


# fot machine learning we use the 2 data directly (as relative pixel
# positions info is ignored by this model)
X = band_psd
n_features = X.shape[1]

# the label to predict is the id of the person
y = adhd

###############################################################################
# Split into a training set and a test set using a stratified k fold

# split into a training and testing set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25)


###############################################################################
# Compute a PCA (eigenfaces) on the face dataset (treated as unlabeled
# dataset): unsupervised feature extraction / dimensionality reduction
n_components = 4

pca = RandomizedPCA(n_components=n_components, whiten=True).fit(X_train)

X_train_pca = pca.transform(X_train)
X_test_pca = pca.transform(X_test)


###############################################################################
# Train a SVM classification model

param_grid = {'C': [1e3, 5e3, 1e4, 5e4, 1e5],
              'gamma': [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.1], }
clf = GridSearchCV(SVC(kernel='rbf', class_weight='auto'), param_grid)
clf = clf.fit(X_train_pca, y_train)

###############################################################################
# Quantitative evaluation of the model quality on the test set

y_pred = clf.predict(X_test_pca)
print classification_report(y_test, y_pred)
print confusion_matrix(y_test, y_pred)
