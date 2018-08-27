import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg

from sklearn.decomposition import PCA, FastICA, NMF, KernelPCA
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import explained_variance_score


import pandas as pd


data = pd.read_csv('/Users/sudregp/data/baseline_prediction/dti_ALL_voxelwise_n263_08152018.csv')

voxels = [cname for cname in data.columns if cname.find('v')==0]
X = data[voxels]
scaler = StandardScaler()
Xs = scaler.fit_transform(X)

# Fit the models

n_components = np.arange(5, 170, 10)  # options for n_components


def compute_scores(X):
    pca = PCA(svd_solver='auto')
    kpca = KernelPCA(fit_inverse_transform=True)
    ica = FastICA()
    nmf = NMF(init='nndsvda')
    pca_scores, ica_scores, nmf_scores, kpca_scores = [], [], [], []
    for n in n_components:
        pca.n_components = n
        ica.n_components = n
        nmf.n_components = n
        kpca.n_components = n
        print(n)

        Xpca = pca.inverse_transform(pca.fit_transform(Xs))
        pca_scores.append(explained_variance_score(Xs, Xpca))
        Xica = ica.inverse_transform(ica.fit_transform(Xs))
        ica_scores.append(explained_variance_score(Xs, Xica))
        Xkpca = kpca.inverse_transform(kpca.fit_transform(Xs))
        kpca_scores.append(explained_variance_score(Xs, Xkpca))
 
        Xnmf = nmf.inverse_transform(nmf.fit_transform(X))
        nmf_scores.append(explained_variance_score(X, Xnmf))

    return pca_scores, ica_scores, nmf_scores, kpca_scores


pca_scores, ica_scores, nmf_scores, kpca_scores = compute_scores(X)
# n_components_pca = n_components[np.argmax(pca_scores)]
# n_components_ica = n_components[np.argmax(ica_scores)]
# n_components_nmf = n_components[np.argmax(nmf_scores)]

# print("best n_components by PCA CV = %d" % n_components_pca)
# print("best n_components by ICA CV = %d" % n_components_ica)
# print("best n_components by Non-negative components CV = %d" % n_components_nmf)

plt.figure()
plt.plot(n_components, pca_scores, 'b', label='PCA scores')
plt.plot(n_components, ica_scores, 'r', label='ICA scores')
plt.plot(n_components, nmf_scores, 'g', label='NMF scores')
plt.plot(n_components, nmf_scores, 'k', label='KernelPCA scores')
# plt.axvline(n_components_pca, color='b',
#             label='PCA CV: %d' % n_components_pca, linestyle='--')
# plt.axvline(n_components_fa, color='r',
#             label='FactorAnalysis CV: %d' % n_components_fa,
#             linestyle='--')
# plt.axvline(n_components_nmf, color='g',
#             label='NMF CV: %d' % n_components_fa,
#             linestyle='--')

plt.xlabel('nb of components')
plt.ylabel('explained variance')
plt.legend(loc='lower right')
plt.title('dimensionality reduction')

plt.show()
