# Converts the big correlation matrices into MACACC strength
import numpy as np
import os
import pylab as pl
import scipy

thalamus_labels = [['Pulvinar', [8]], ['Lateral Posterior', [6]],
                    ['Lateral Dorsal', [5]], ['VP', [11]], ['VL', [10]],
                    ['VA', [9]], ['Anterior nuclei', [3]], ['Medial Dorsal', [7]],
                    ['Central nuclei', [4]]]
striatum_labels = [['Tail Caudate', [104.176]], ['Head Caudate', [102.118]],
                    ['Nucleus Accumbens', [100.059]], ['Post Putamen', [105]],
                    ['Ant Putamen', [100.882]]]
gp_labels = [['Posterior', [12]], ['Anterior', [11.0118, 4.98824]]]
cortex_labels = [['Occipital', [132, 38, 63, 97, 175, 112, 251, 98, 154, 37, 54, 69]],
                ['Parietal', [88, 60, 41, 32, 110, 52, 41, 159, 56, 74]],
                ['Temporal', [145, 130, 140, 26, 165, 99, 139, 125, 61, 64, 164, 62, 119, 196, 118, 18]],
                ['PostCentral', [74, 110]], ['Precentral', [5, 80]],
                ['Frontal', [10, 2, 75, 5, 6, 1, 7, 70, 50, 15, 80, 90, 85, 27]],
                ['Cingulate', [7, 27]]]

def load_rois(fname, brain):
    roi_vertices = []
    roi_labels = []
    labels = np.genfromtxt(fname)
    if brain=='thalamus':
        rois = thalamus_labels
    elif brain=='striatum':
        rois = striatum_labels
    elif brain=='gp':
        rois = gp_labels
    elif brain=='cortex':
        rois = cortex_labels
    else:
        rois = []
    for r in rois:
        roi_labels.append(r[0])
        vert_list = [np.nonzero(labels == i)[0] for i in r[1]]
        # merge all vertices into one big array
        verts = []
        for v in vert_list:
           verts = np.concatenate((verts, v))
        roi_vertices.append(verts.astype(np.int32))
    return roi_labels, roi_vertices


def load_structural(fname):
    data = np.genfromtxt(fname, delimiter=',')
    # removing first column and first row, because they're headers
    data = scipy.delete(data, 0, 1)
    data = scipy.delete(data, 0, 0)
    # format it to be subjects x variables
    data = data.T
    return data


fromR = ['thalamus']
toR = ['thalamus']

groups = ['NV', 'persistent', 'remission']
hemi = ['L', 'R']
time = ['base', 'last']
init_verts = 10e5
init_subjs = 100

for group in groups:
    print '===', group, '==='
    ms = []
    desc = []
    for fr in fromR:
        print 'Working on ' + fr
        for h in hemi:
            print h
            # just so we can compute differences later
            all_raw_data = []
            all_seed_data = []
            for t in time:
                seed_data = load_structural('%s/data/structural/%s_%s%s_%s_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_2to1.csv' % (os.path.expanduser('~'), t, fr, h, group))
                # create huge array so we can add all the data and thenresize it appropriately
                raw = np.empty([init_subjs, init_verts],dtype=np.float16)
                raw[:] = np.nan
                cnt = 0
                for tr in toR:
                    for h2 in hemi:
                        data = load_structural('%s/data/structural/%s_%s%s_%s_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_2to1.csv' % (os.path.expanduser('~'), t, tr, h2, group))
                        nsubjects = data.shape[0]
                        nverts = data.shape[1]
                        raw[0:nsubjects,cnt:(cnt+nverts)] = data
                        cnt += nverts

                # trimming the matric to the correct number of vertices and subjects
                print 'Resizing matrices'
                nverts = cnt
                raw = raw[:nsubjects, :nverts]

                print 'Computing correlations'
                # corrs stores the correlation with seed1 itself, then with seed2, then seed3, etc, such that
                # the first non seed vertex is at nseedverts
                m = np.hstack([seed_data,raw])
                corrs = np.corrcoef(m, rowvar=0)
                nseedverts = seed_data.shape[1]
                ms.append(np.mean(corrs[:nseedverts, nseedverts:],axis=1))
                desc.append(t + '_' + h)

                all_raw_data.append(raw)
                all_seed_data.append(seed_data)
            print 'Computing correlations'
            m = np.hstack([all_seed_data[1]-all_seed_data[0], all_raw_data[1]-all_raw_data[0]])
            corrs = np.corrcoef(m, rowvar=0)
            ms.append(np.mean(corrs[:nseedverts, nseedverts:],axis=1))
            desc.append('delta_' + h)
        np.savez('%s/data/results/structural/verts_MS_from%s_to%s_matchdiff_dsm5_2to1_%s'%
                (os.path.expanduser('~'), fr, '-'.join(toR), group), ms=ms, desc=desc)
