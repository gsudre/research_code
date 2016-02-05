# creates barplot or scatterplot for meg+fMRI results
import os
from scipy import stats
import numpy as np
home = os.path.expanduser('~')

# res_dir = home + '/data/results/fmri_Yeo/seeds/'
# res_fname = 'net6_rSupra/RESID_inatt_a0.05t0.99d5p5000.txt'
res_dir = home + '/data/results/inatt_resting/'
res_fname = 'dmn_rACC_a0.05t0.99d5p5000.txt'

# if 'inatt' in res_fname or 'hi' in res_fname or 'total' in res_fname:
#     plot_type='scatterplot'
# else:
#     plot_type='barplot'
plot_type = 'scatterplot'

seed = res_fname.split('/')[0]

# open fMRI data
g1_fname = home + '/data/fmri/joel_nvs.txt'
g2_fname = home + '/data/fmri/joel_persistent.txt'
g3_fname = home + '/data/fmri/joel_remission.txt'
subjs_fname = home + '/data/fmri/joel_all.txt'
inatt_fname = home + '/data/fmri/inatt.txt'
hi_fname = home + '/data/fmri/hi.txt'
# data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/'
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
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
print 'Loading fMRI data...'
# data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
data = np.genfromtxt(res_dir + '_'.join(res_fname.split('_')[:2]) + '.txt')
fmri_xyz = data[:,3:6]
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
cnt=6
for s in subjs:
    if s in g1:
        g1_data.append(data[:,cnt])
        g1_subjs.append(s)
    elif s in g2:
        g2_data.append(data[:,cnt])
        g2_subjs.append(s)
        g2_inatt.append(inatt[int(s)])
        g2_hi.append(hi[int(s)])
    elif s in g3:
        g3_data.append(data[:,cnt])
        g3_subjs.append(s)
        g3_inatt.append(inatt[int(s)])
        g3_hi.append(hi[int(s)])
    cnt+=1
inattf = g2_inatt + g3_inatt
hif = g2_hi + g3_hi
totalf = [i+j for i, j in zip(inattf,hif)]
Xf = np.arctanh(np.array(g1_data))
Yf = np.arctanh(np.array(g2_data))
Zf = np.arctanh(np.array(g3_data))

# loading the results mask
print 'Loading results mask...'
res = np.genfromtxt(res_dir+res_fname)

# calculates good voxels based on a mask
def get_good_data(datasets, xyz, idx): 
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

print 'Computing good voxels in fMRI...'
good_fmri = get_good_data([Xf, Yf, Zf],fmri_xyz,3)

# now depending on the plotting we need, we'll have different processing
nrows=1
ncols=len(good_fmri)
c=1
fig = figure()
if plot_type=='scatterplot':
    # for each cluster in the fMRI results
    for cl in range(len(good_fmri)):
        subplot(nrows,ncols,c)
        y = np.hstack([good_fmri[cl][1],good_fmri[cl][2]])
        res_fname='inatt'
        if 'inatt' in res_fname:
            t_str = 'inattention'
            x = np.array(inattf)
        elif 'hi' in res_fname:
            t_str = 'HI'
            x = np.array(hif)
        else:
            t_str = 'total'
            x = np.array(totalf)
        if 'WithNVs' in res_fname: 
            y = np.hstack([good_fmri[cl][0],y])
            t_str = t_str + ' with NVs'
            x = np.hstack([np.zeros(len(g1_subjs)), x])
        plot(x,y,'.b',ms=10)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        line = slope*x+intercept
        plot(x,line,'b-',linewidth=5)
        title('fMRI (r=%.2f, p=%.3f)'%(r_value,p_value))
        xlabel(t_str)
        ylabel('Zcorr')
        ax = gca()
        ax.yaxis.labelpad = -5
        axis('tight')
        c+=1

# always make a barplot 
fig = figure()
c=1
for cl in range(len(good_fmri)):
    subplot(nrows,ncols,c)
    y = [np.mean(good_fmri[cl][0]), np.mean(good_fmri[cl][1]), np.mean(good_fmri[cl][2])]
    std = [np.std(good_fmri[cl][0])/np.sqrt(Xf.shape[0]), np.std(good_fmri[cl][1])/np.sqrt(Yf.shape[0]), np.std(good_fmri[cl][2])/np.sqrt(Zf.shape[0])]
    bar(np.arange(len(y)),y,0.35,color=['g','r','b'],ecolor='k',yerr=std)
    title('fMRI, cluster %d'%cl)

    print 'fMRI, cluster %d'%cl + ': nvVSper = %.3f'%stats.ttest_ind(good_fmri[cl][0],good_fmri[cl][1])[1]
    print 'fMRI, cluster %d'%cl + ': nvVSrem = %.3f'%stats.ttest_ind(good_fmri[cl][0],good_fmri[cl][2])[1]
    print 'fMRI, cluster %d'%cl + ': perVSrem = %.3f'%stats.ttest_ind(good_fmri[cl][1],good_fmri[cl][2])[1]

    c+=1