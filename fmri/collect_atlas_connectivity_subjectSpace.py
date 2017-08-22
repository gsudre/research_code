# Matches ROIs in subject space to construct connectivity matrices
#
# GS, 08/2017


import numpy as np
import pandas as pd


trimmed = [False, True]
atlases = ['aparc', 'aparc.a2009s']
rois = [range(5, 10+1) + range(13, 15+1) + [17, 20] + range(25, 33+1) + [36] +
         range(47, 80+1) + range(82, 115+1),
        range(5, 10+1) + range(13, 15+1) + [17, 20] + range(25, 33+1) + [36] +
         range(49, 122+1) + range(124, 197)]

fid = open('/Users/sudregp/data/prs/fmri_kids_all.txt', 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
fid = open('/Users/sudregp/data/prs/fmri_adults_all.txt', 'r')
subjs += [line.rstrip() for line in fid]
fid.close()

for trim in trimmed:
    print trim
    for a, atlas in enumerate(atlases):
        data_dir = '/Users/sudregp/data/fmri_prs_ss/%s/' % atlas
        fid = open('/Users/sudregp/data/prs/%s+aseg_REN_all.niml.lt' % atlas)
        roi_labels = {}
        for line in fid:
            if line[0] == '"':
                num, roi = line.rstrip().split(' ')
                roi_labels[int(num.replace('"', ''))] = roi.replace('"', '')
        mats = []
        for sid, s in enumerate(subjs):
            # as long as the first roi is not empty, we should be fine here
            num_trs = 0
            print sid, s
            subj_data = []
            for r in rois[a]:
                fname = data_dir + '/%s/%d.1D' % (s, r)
                roi_data = np.genfromtxt(fname)
                num_trs = max(num_trs, len(roi_data))
                if trim:
                    max_trs = min(123, num_trs)
                    out_fname = '/Users/sudregp/tmp/%s_trimmed.csv' % atlas
                else:
                    max_trs = num_trs
                    out_fname = '/Users/sudregp/tmp/%s.csv' % atlas
                # sometimes the mask doesn't cover the region
                if len(roi_data) == 0:
                    subj_data.append([np.nan] * max_trs)
                else:
                    subj_data.append(roi_data[:max_trs])
            subj_data = np.arctanh(np.corrcoef(np.array(subj_data)))
            idx = np.triu_indices_from(subj_data, k=1)
            mats.append([int(s)] + list(subj_data[idx]))
        corr_mats = np.array(mats)

        cnames = ['%s_TO_%s' % (roi_labels[rois[a][i]], roi_labels[rois[a][j]])
                  for i, j in zip(idx[0], idx[1])]
        data = pd.DataFrame(corr_mats, columns=['maskid'] + cnames)
        
        data.to_csv(out_fname)