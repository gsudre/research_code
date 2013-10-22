# Plots and saves the vertex-based subcortical correlation
import numpy as np
import os
import pylab as pl

# Note that we need to plot differences because if we just plot one group most
# vertices inside the same ROI will be highly correlated!
g1 = 'remission'
g2 = 'NV'
method = 'delta'  # 'baseline','last','delta'
# we need to decimate the correlation matrix, otherwise it cannot plot it
decim = 5

res1 = np.load('%s/data/results/structural/verts_corr_matchdiff_dsm4_%s.npz'%(os.path.expanduser('~'), g1))
res2 = np.load('%s/data/results/structural/verts_corr_matchdiff_dsm4_%s.npz'%(os.path.expanduser('~'), g2))
cmin=-1.2
cmax=1.2
if method=='baseline':
    mat = res1['allcorrs'][0] - res2['allcorrs'][0]
elif method=='last':
    mat = res1['allcorrs'][1] - res2['allcorrs'][1]
elif method=='delta':
    mat = (res1['allcorrs'][1] - res1['allcorrs'][0]) - (res2['allcorrs'][1] - res2['allcorrs'][0])
    #cmin=-1.5
    #cmax=1.5
else:
    print('Error: do not recognize method.')
    exit()
v = mat.shape[0]
subset = range(0,v,decim)
mat = mat[:,subset]
mat = mat[subset,:]
vlabels = res1['verts'][subset]
# need to code it this way because np.unique screws up the sorting
plot_labels = []
plot_ticks = []
cur_label = ''
for l, label in enumerate(vlabels):
    if cur_label!=label:
        cur_label = label
        plot_labels.append(label)
        plot_ticks.append(l)
fig = pl.figure()
ax1 = pl.imshow(mat, interpolation='nearest');
ax1.set_clim(cmin,cmax)
pl.colorbar(shrink=.5)
pl.title('Diff %s - %s (%s)' % (g1, g2, method))
pl.xticks(plot_ticks, plot_labels,rotation='vertical')
pl.yticks(plot_ticks, plot_labels)
ax = pl.gca()
for item in (ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(10)
#pl.show()
fig.set_size_inches([ 17.45,   9.8 ])
pl.subplots_adjust(left=0, right=1.0, bottom=0.15, top=.95)
pl.savefig('%s/data/results/structural/diff_corr_matchdiff_dsm4_%svs%s_%s.png' %
            (os.path.expanduser('~'), g1, g2, method), dpi=100)
