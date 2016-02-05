# creates barplot or scatterplot for meg+fMRI results
import os
from scipy import stats
import numpy as np
home = os.path.expanduser('~')

# res_dir = home + '/data/results/meg_Yeo/seeds/'
# res_fname = 'net7_rACC/RESID_hi_8to13_a0.05t0.99d5p5000.txt'

# if 'inatt' in res_fname or 'hi' in res_fname or 'total' in res_fname:
#     plot_type='scatterplot'
# else:
#     plot_type='barplot'
res_dir = home + '/data/results/inatt_resting/'
res_fname = 'dmn_rACC_1to4_a0.05t0.99d5p5000.txt'
plot_type = 'scatterplot'

seed = res_fname.split('/')[0]

# open MEG data
band = res_fname.split('_')[3].split('to')
g1_fname = home + '/data/meg/nv_subjs.txt'
g2_fname = home + '/data/meg/persistent_subjs.txt'
g3_fname = home + '/data/meg/remitted_subjs.txt'
inatt_fname = home + '/data/meg/inatt.txt'
hi_fname = home + '/data/meg/hi.txt'
data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]
res = np.recfromtxt(inatt_fname, delimiter='\t')
inatt = {}
for rec in res:
    inatt[rec[0]] = rec[1]
res = np.recfromtxt(hi_fname, delimiter='\t')
hi = {}
for rec in res:
    hi[rec[0]] = rec[1]
g1_data = []
g2_data = []
g3_data = []
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []
print 'Loading MEG data...'
# ds_data = np.load(data_dir + '/correlations_%s-%s.npy'%(band[0],band[1]))[()]
ds_data = np.load(res_dir + '/%s.npy'%('_'.join(res_fname.split('_')[:3])))[()]
for s, data in ds_data.iteritems():
    # special case: this voxel is infinite for everybody, so make it nan so it doesn't screw up the averages
    if res_fname=='net7_lACC_nvVSper_30to55_a0.01t0.99d5p5000.txt':
        data[2323,0] = np.nan
    if s in g1:
        g1_data.append(data.T)
        g1_subjs.append(s)
    elif s in g2:
        g2_data.append(data.T)
        g2_subjs.append(s)
        g2_inatt.append(inatt[s])
        g2_hi.append(hi[s])
    elif s in g3:
        g3_data.append(data.T)
        g3_subjs.append(s)
        g3_inatt.append(inatt[s])
        g3_hi.append(hi[s])
inattm = g2_inatt + g3_inatt
him = g2_hi + g3_hi
totalm = [i+j for i,j in zip(inattm,him)]
Xm = np.arctanh(np.array(g1_data)).squeeze()
Ym = np.arctanh(np.array(g2_data)).squeeze()
Zm = np.arctanh(np.array(g3_data)).squeeze()
# for some reason there's always a voxel that's Inf in all subjects. Let's replace it by NaN
inf_voxels = np.unique(np.nonzero(np.isinf(Xm))[1])
if len(inf_voxels)>0:
    print 'Voxels with Inf: %d'%len(inf_voxels)
    for v in inf_voxels:
        Xm[:,v]=np.nan
        Ym[:,v]=np.nan
        Zm[:,v]=np.nan

# loading the results mask
print 'Loading results mask...'
res = np.genfromtxt(res_dir+res_fname)

def get_good_data(datasets, idx): 
    clusters = np.unique(res[:,idx])
    clusters = clusters[clusters>0]
    # store the voxel index of each cluster in a list, one array per cluster
    cluster_voxels = [np.nonzero(res[:,idx]==c)[0] for c in clusters]
    
    # good data has one entry per cluster. Each entry is a list of 3 matrices, one for each group. Each matrix has the mean data in the cluster for each subject
    good_data=[]
    for cv in cluster_voxels:
        cluster_data = [np.nanmean(datasets[i][:,cv],axis=1) for i in range(len(datasets))]
        good_data.append(cluster_data)
    return good_data

print 'Computing good voxels in MEG...'
good_meg = get_good_data([Xm, Ym, Zm], 3)

# now depending on the plotting we need, we'll have different processing
nrows=1
ncols=len(good_meg)
c=1
fig = figure()
if plot_type=='scatterplot':
    # for each cluster in the fMRI results
    for cl in range(len(good_meg)):
        subplot(nrows,ncols,c)
        y = np.hstack([good_meg[cl][1],good_meg[cl][2]])

        res_fname='inatt'
        if 'inatt' in res_fname:
            t_str = 'inattention'
            x = np.array(inattm)
        elif 'hi' in res_fname:
            t_str = 'HI'
            x = np.array(him)
        else:
            t_str = 'total'
            x = np.array(totalm)
        if 'WithNVs' in res_fname: 
            y = np.hstack([good_meg[cl][0],y])
            t_str = t_str + ' with NVs'
            x = np.hstack([np.zeros(len(g1_subjs)), x])
        idx = ~np.isnan(y)
        y = y[idx]
        x=x[idx]
        plot(x,y,'.b',ms=10)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        line = slope*x+intercept
        plot(x,line,'b-',linewidth=5)
        title('MEG (r=%.2f, p=%.3f)'%(r_value,p_value))
        xlabel(t_str)
        ylabel('Zcorr')
        ax = gca()
        ax.yaxis.labelpad = -5
        axis('tight')
        c+=1

# always make a barplot 
fig = figure()
c=1
for cl in range(len(good_meg)):
    subplot(nrows,ncols,c)
    y = [np.nanmean(good_meg[cl][0]), np.nanmean(good_meg[cl][1]), np.nanmean(good_meg[cl][2])]
    std = [np.nanstd(good_meg[cl][0])/np.sqrt(Xm.shape[0]), np.nanstd(good_meg[cl][1])/np.sqrt(Ym.shape[0]), np.nanstd(good_meg[cl][2])/np.sqrt(Zm.shape[0])]
    bar(np.arange(len(y)),y,0.35,color=['g','r','b'],ecolor='k',yerr=std)
    title('MEG, cluster %d'%cl)

    print 'MEG, cluster %d'%cl + ': nvVSper = %.3f'%stats.ttest_ind(good_meg[cl][0][~np.isnan(good_meg[cl][0])],good_meg[cl][1][~np.isnan(good_meg[cl][1])])[1]
    print 'MEG, cluster %d'%cl + ': nvVSrem = %.3f'%stats.ttest_ind(good_meg[cl][0][~np.isnan(good_meg[cl][0])],good_meg[cl][2][~np.isnan(good_meg[cl][2])])[1]
    print 'MEG, cluster %d'%cl + ': perVSrem = %.3f'%stats.ttest_ind(good_meg[cl][1][~np.isnan(good_meg[cl][1])],good_meg[cl][2][~np.isnan(good_meg[cl][2])])[1]

    c+=1