import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn import manifold
import numpy as np


data = pd.read_csv('/Users/sudregp/data/baseline_prediction/dti_ALL_voxelwise_n263_08152018.csv')

voxels = [cname for cname in data.columns[:500] if cname.find('v')==0]
X = data[voxels]
scaler = StandardScaler()
Xs = scaler.fit_transform(X)

# Fit the models

n_components = np.arange(5, 25, 5)  # options for n_components
n_neighbors = X.shape[0] - 1

methods = ['standard', 'hessian', 'modified', 'ltsa']
labels = ['LLE', 'Hessian LLE', 'Modified LLE', 'LTSA']

scores = {}
for i, method in enumerate(methods):
    scores[method] = []
    print("%s" % (method))
    for n in n_components:
        Y = manifold.LocallyLinearEmbedding(n_neighbors, n,
                                            eigen_solver='dense',
                                            method=method).fit(Xs)
        scores[method].append(Y.reconstruction_error_)

method = 'isomap'
scores[method] = []
print("%s" % (method))
for n in n_components:
    Y = manifold.Isomap(n_neighbors, n).fit(Xs)
    scores[method].append(Y.reconstruction_error())

# method = 'mds'
# scores[method] = []
# print("%s" % (method))
# for n in n_components:
#     Y = manifold.MDS(n_neighbors, n).fit(Xs)
#     scores[method].append(Y.reconstruction_error())

method = 'spectral'
scores[method] = []
print("%s" % (method))
for n in n_components:
    Y = manifold.SpectralEmbedding(n_components=n).fit(Xs)
    scores[method].append(Y.reconstruction_error())

method = 'tsne'
scores[method] = []
print("%s" % (method))
for n in n_components:
    Y = manifold.TSNE(n_components = n).fit(Xs)
    scores[method].append(Y.reconstruction_error())

# t0 = time()
# Y = manifold..fit_transform(X)
# t1 = time()
# print("Isomap: %.2g sec" % (t1 - t0))
# ax = fig.add_subplot(257)
# plt.scatter(Y[:, 0], Y[:, 1], c=color, cmap=plt.cm.Spectral)
# plt.title("Isomap (%.2g sec)" % (t1 - t0))
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())
# plt.axis('tight')


# t0 = time()
# mds = manifold.MDS(n_components, max_iter=100, n_init=1)
# Y = mds.fit_transform(X)
# t1 = time()
# print("MDS: %.2g sec" % (t1 - t0))
# ax = fig.add_subplot(258)
# plt.scatter(Y[:, 0], Y[:, 1], c=color, cmap=plt.cm.Spectral)
# plt.title("MDS (%.2g sec)" % (t1 - t0))
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())
# plt.axis('tight')


# t0 = time()
# se = manifold.SpectralEmbedding(n_components=n_components,
#                                 n_neighbors=n_neighbors)
# Y = se.fit_transform(X)
# t1 = time()
# print("SpectralEmbedding: %.2g sec" % (t1 - t0))
# ax = fig.add_subplot(259)
# plt.scatter(Y[:, 0], Y[:, 1], c=color, cmap=plt.cm.Spectral)
# plt.title("SpectralEmbedding (%.2g sec)" % (t1 - t0))
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())
# plt.axis('tight')

# t0 = time()
# tsne = manifold.TSNE(n_components=n_components, init='pca', random_state=0)
# Y = tsne.fit_transform(X)
# t1 = time()
# print("t-SNE: %.2g sec" % (t1 - t0))
# ax = fig.add_subplot(2, 5, 10)
# plt.scatter(Y[:, 0], Y[:, 1], c=color, cmap=plt.cm.Spectral)
# plt.title("t-SNE (%.2g sec)" % (t1 - t0))
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())
# plt.axis('tight')

# plt.show()
