import numpy as np
import os
import scipy
import matplotlib.mlab as mlab
import pdb
from scipy import stats
import pdb as pb


def load_structural(fname):
    data = np.genfromtxt(fname, delimiter=',')
    # removing first column and first row, because they're headers
    data = scipy.delete(data, 0, 1)
    data = scipy.delete(data, 0, 0)
    # format it to be subjects x variables
    data = data.T
    return data


group = 'NV' #, 'NV', 'persistent', 'remission'
brain = ['gp','thalamus'] #['striatum', 'gp', 'thalamus']
hemi = ['L']
time = ['base', 'last']
init_verts = 10e5
init_subjs = 100

all_data = []
all_corrs = []
for t in time:
    # create huge array so we can add all the data and thenresize it appropriately
    raw = np.empty([init_subjs, init_verts],dtype=np.float16)
    raw[:] = np.nan
    # verts will be a list of strings, with the name of the ROI the vertex belongs to
    verts = []
    cnt = 0
    for b in brain:
        print 'Working on ' + b
        for h in hemi:
            data = load_structural('%s/data/structural/%s_%s%s_%s_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_2to1.csv' % (os.path.expanduser('~'), t, b, h, group))
            num_subjects = data.shape[0]
            num_verts = data.shape[1]
            raw[0:num_subjects,cnt:(cnt+num_verts)] = data
            cnt += num_verts
    # trimming the matric to the correct number of vertices and subjects
    print 'Resizing matrices'
    num_vertices = cnt
    raw = raw[:num_subjects, :num_vertices]

    print 'Computing correlations'
    # when we exclude the cortex, we can compute all at once
    corrs = np.float16(np.corrcoef(raw,rowvar=0))
    np.savez('%s/data/results/structural/verts_%sCorr_gpLthamalusLmatchdiff_dsm5_2to1_%s'%
            (os.path.expanduser('~'), t, group), corrs=corrs, verts=verts)
    all_data.append(raw)
