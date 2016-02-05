# creates barplot or scatterplot for meg+fMRI results
import os
from scipy import stats
import numpy as np
home = os.path.expanduser('~')

res_dir = home + '/data/results/meg_fmri_resting/overlap/'
res_fname = 'net6_rSupra_inatt_65to100_a0.05t0.99d5p5000.txt'

if 'inatt' in res_fname or 'hi' in res_fname:
    plot_type='scatterplot'
else:
    plot_type='barplot'

seed = '_'.join(res_fname.split('_')[:2])

# open MEG data
meg_xyz = np.genfromtxt(home + '/data/meg/sam_narrow_5mm/brainTargetsInTLR.txt', skip_header=1)
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
ds_data = np.load(data_dir + '/correlations_%s-%s.npy'%(band[0],band[1]))[()]
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

# calculates good voxels based on a mask
def get_good_data(datasets, xyz, idx): 
    clusters = np.unique(res[:,idx])
    clusters = clusters[clusters>0]
    cluster_voxels = [np.nonzero(res[:,idx]==c)[0] for c in clusters]
    
    # good data has one entry per cluster. Each entry is a list of 3 matrices, one for each group. Each matrix has the mean data in the cluster for each subject
    good_data=[]
    for cv in cluster_voxels:
        cluster_data = [[] for i in range(len(datasets))]
        for v in cv:
            # for each voxel that is good in the cluster, find the best match in the data
            voxel_xyz = res[v, 3:6]
            dist = np.sqrt((xyz[:,0] - voxel_xyz[0])**2 + (xyz[:,1] - voxel_xyz[1])**2 + (xyz[:,2] - voxel_xyz[2])**2)
            best_match = np.argmin(dist)
            # add the value of that voxel to the mix of each subject group
            for i in range(len(datasets)):
                cluster_data[i].append(datasets[i][:, best_match])
        mean_data = [np.nanmean(cd, axis=0) for cd in cluster_data]
        good_data.append(mean_data)
    return good_data

print 'Computing good voxels in MEG...'
good_meg = get_good_data([Xm, Ym, Zm],meg_xyz,7)
print 'Computing good voxels in MEG (overlap)...'
good_meg_overlap = get_good_data([Xm, Ym, Zm],meg_xyz,8)

# now depending on the plotting we need, we'll have different processing
if plot_type=='scatterplot':
    nrows=len(good_meg)
    ncols=2
    c=1
    fig = figure()
    # for each cluster in the fMRI results
    for cl in range(len(good_meg)):
        subplot(nrows,ncols,c)
        y = np.hstack([good_meg[cl][1],good_meg[cl][2]])
        x = np.array(inattm)
        plot(x,y,'.b',ms=10)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        line = slope*x+intercept
        plot(x,line,'b-',linewidth=5)
        title('MEG (r=%.2f, p=%.3f)'%(r_value,p_value))
        xlabel('inattention')
        ylabel('Zcorr')
        ax = gca()
        ax.yaxis.labelpad = -5
        axis('tight')

        subplot(nrows,ncols,c+1)
        y = np.hstack([good_meg_overlap[cl][1],good_meg_overlap[cl][2]])
        x = np.array(inattm)
        # idx = ~np.isnan(y)
        # y = y[idx]
        # x = x[idx]
        plot(x,y,'.r',ms=10)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        line = slope*x+intercept
        plot(x,line,'r-',linewidth=5)
        title('Overlap MEG, %sHz (r=%.2f, p=%.3f)'%(res_fname.split('_')[3],r_value,p_value))
        xlabel('inattention')
        ylabel('Zcorr')
        ax = gca()
        ax.yaxis.labelpad = -5
        axis('tight')
        c+=2
else:
    nrows=1
    ncols=1
    fig = figure()
    # fig = figure(figsize=(14.8,3.8)
    for c in range(len(good_meg)):
        subplot(nrows,ncols,c+1)
        y = [np.mean(good_meg[c][0]), np.mean(good_meg[c][1]), np.mean(good_meg[c][2])]
        std = [np.std(good_meg[c][0])/np.sqrt(Xm.shape[0]), np.std(good_meg[c][1])/np.sqrt(Ym.shape[0]), np.std(good_meg[c][2])/np.sqrt(Zm.shape[0])]
        bar(np.arange(len(y)),y,0.35,color=['g','r','b'],ecolor='k',yerr=std)
        title('MEG, %sHz, cluster %d'%(res_fname.split('_')[3], c+1))