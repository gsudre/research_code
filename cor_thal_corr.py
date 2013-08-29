import numpy as np
import env
import scipy
from scipy import stats
import mne
import glob

sel = '_3orMore'  # '_3orMore', '2closestTo16', or ''

cortex = np.genfromtxt(env.data + '/structural/cortexR_SA_NV_10to21' + sel + '.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

subcortex = np.genfromtxt(env.data + '/structural/thalamusR_SA_NV_10to21' + sel + '.csv', delimiter=',')
# removing first column and first row, because they're headers
subcortex = scipy.delete(subcortex, 0, 1)
subcortex = scipy.delete(subcortex, 0, 0)
# format it to be subjects x variables
subcortex = subcortex.T

# selecting only a few vertices in the thalamus
# my_sub_vertices = [2310, 1574, 1692, 1262, 1350]
# my_sub_vertices = [1533, 1106, 225, 163, 2420, 2966, 1393, 1666, 1681, 1834, 2067]  # GS made it up by looking at anamoty, refer to Evernote for details
# my_sub_vertices = range(subcortex.shape[1])
my_sub_vertices = []
label_files = glob.glob(env.fsl + '/mni/label/rh.*.label')
for l in label_files:
    v = mne.read_label(l)
    my_sub_vertices.append(v.vertices)

num_subjects = cortex.shape[0]

X = cortex

# Y = subcortex[:, my_sub_vertices]
Y = np.zeros([num_subjects, len(my_sub_vertices)])
for r, roi in enumerate(my_sub_vertices):
    Y[:, r] = scipy.stats.nanmean(subcortex[:, roi], axis=1)

corr = np.empty([X.shape[1], Y.shape[1]])
pvals = np.empty([X.shape[1], Y.shape[1]])
for x in range(X.shape[1]):
    print str(x+1) + '/' + str(X.shape[1])
    for y in range(Y.shape[1]):
        corr[x, y], pvals[x, y] = stats.pearsonr(X[:, x], Y[:, y])


np.savez(env.results + 'structurals_pearson_roi_thalamus_all_cortex' + sel, corr=corr, pvals=pvals, my_sub_vertices=my_sub_vertices)

# make a few pictures
if Y.shape[1] < 10:  # safe-check for not exploding the screen
    import mayavi.mlab as ml
    import surfer

    ml.close(all=True)
    figs = []
    for i, rname in enumerate(label_files):
        f = ml.figure()
        brain = surfer.Brain('mni', 'rh', 'cortex', curv=False, figure=f)
        brain.add_data(-pvals[:, i])
        brain.scale_data_colormap(-.05, -.02, 0, True)
        figs.append(f)
        print i+1, ':', rname.split('/')[-1]
