# creates nifti files for each MEG network
import os
import numpy as np
home = os.path.expanduser('~')

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
data_dir = home + '/data/results/meg_Yeo/seeds/net7_rACC/'

# open MEG data
g1_fname = home + '/data/meg/nv_subjs.txt'
g2_fname = home + '/data/meg/persistent_subjs.txt'
g3_fname = home + '/data/meg/remitted_subjs.txt'
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]
g1_subjs = []
g2_subjs = []
g3_subjs = []


def write2afni(vals, fname):
    data = np.genfromtxt(home + '/data/meg/sam_narrow_5mm/voxelsInBrain.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data = data[:, :4]
    # 3dUndump can only create files with one subbrick
    data[:, 3] = vals
    np.savetxt(fname+'.txt', data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat ' + fname + '.txt | 3dUndump -master ' + home + '/data/meg/sam_narrow_5mm/TT_N27_555+tlrc -ijk -datum float -prefix ' + fname + ' -overwrite -')


for band in bands:
    g1_data = []
    g2_data = []
    g3_data = []
    ds_data = np.load(data_dir + '/correlations_%d-%d.npy' % (band[0], band[1]))[()]
    for s, data in ds_data.iteritems():
        if s in g1:
            g1_data.append(data.T)
        elif s in g2:
            g2_data.append(data.T)
        elif s in g3:
            g3_data.append(data.T)
    Xm = np.arctanh(np.array(g1_data)).squeeze()
    Ym = np.arctanh(np.array(g2_data)).squeeze()
    Zm = np.arctanh(np.array(g3_data)).squeeze()
    # Xm = np.array(g1_data).squeeze()
    # Ym = np.array(g2_data).squeeze()
    # Zm = np.array(g3_data).squeeze()
    write2afni(np.mean(Xm, axis=0), data_dir + 'nvs_%d-%d' % (band[0], band[1]))
    write2afni(np.mean(Ym, axis=0), data_dir + 'persistent_%d-%d' % (band[0], band[1]))
    write2afni(np.mean(Zm, axis=0), data_dir + 'remission_%d-%d' % (band[0], band[1]))
    write2afni(np.mean(np.vstack([Xm, Ym, Zm]), axis=0), data_dir + 'all_%d-%d' % (band[0], band[1]))
