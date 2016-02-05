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

groups = ['NV', 'persistent', 'remission']
brain = ['striatum', 'gp', 'thalamus', 'cortex']
hemi = ['L', 'R']
time = ['baseline', 'last']
init_verts = 10e5
init_subjs = 100

for group in groups:
    cnt = 0
    print group
    all_corrs = {}
    for t in time:
        all_corrs[t] = {}
        # start by creating big matrix with all data to get mean for each subject over voxels
        # we cannot have two subch big matrices, so we have to do it in this time loop
        raw = np.empty([init_subjs, init_verts],dtype=np.float32)
        raw[:] = np.nan
        for b in brain:
            for h in hemi:
                if t == 'baseline':
                    data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv' % (os.path.expanduser('~'), t, b, h, group))
                else:
                    data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv' % (os.path.expanduser('~'), t, b, h, group))
                num_subjects = data.shape[0]
                num_vertices = data.shape[1]
                raw[0:num_subjects,cnt:(cnt+num_vertices)] = data
                cnt += num_vertices
        # trimming the matric to the correct number of vertices and subjects
        raw = raw[:num_subjects, :cnt]
        subj_mean = stats.nanmean(raw[:,:], axis=1)

        # for each individual brain region, compute its approximated MACACC strength and save
        # in the brainview format
        for b in brain:
            all_corrs[t][b] = {}
            for h in hemi:
                if t == 'baseline':
                    data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv' % (os.path.expanduser('~'), t, b, h, group))
                else:
                    data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv' % (os.path.expanduser('~'), t, b, h, group))
                num_vertices = data.shape[1]
                corr = np.empty(num_vertices)
                for v in range(num_vertices):
                    corr[v] = np.corrcoef(data[:,v], subj_mean)[0,1]
                # save the file for brain-view2
                fname = ('%s/data/results/structural/approxMACACCstrength_%s_%s_%s%s.txt' %
                        (os.path.expanduser('~'), group, t, h, b))
                fid = open(fname,'w')
                fid.write('<header>\n</header>\napproxMACACCstrength_%s\n' % t)
                for v in corr:
                    fid.write('%.4f\n'%v)
                fid.close()
                all_corrs[t][b][h] = np.float16(corr)
    # now we compute the deltas and write them to brain-view
    for b in brain:
        for h in hemi:
            corr = all_corrs['last'][b][h] - all_corrs['baseline'][b][h]
            fname = ('%s/data/results/structural/approxMACACCstrength_%s_delta_%s%s.txt' %
                        (os.path.expanduser('~'), group, h, b))
            fid = open(fname,'w')
            fid.write('<header>\n</header>\napproxMACACCstrength_delta\n')
            for v in corr:
                fid.write('%.4f\n'%v)
            fid.close()
