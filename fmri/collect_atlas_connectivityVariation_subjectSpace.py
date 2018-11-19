# Matches ROIs in subject space to construct connectivity matrices, but returns
# the absolute difference between connectivity in first half to the second half
# of the overall recording
#
# GS, 11/2018


import numpy as np
import pandas as pd
from itertools import combinations
from scipy import stats


trimmed = [False, True]
atlases = ['aparc', 'aparc.a2009s']
rois = [list(range(5, 10+1)) + list(range(13, 15+1)) + [17, 20] + \
        list(range(25, 33+1)) + [36] + list(range(47, 80+1)) + \
        list(range(82, 115+1)),
        list(range(5, 10+1)) + list(range(13, 15+1)) + list([17, 20]) + \
        list(range(25, 33+1)) + [36] + list(range(49, 122+1)) + \
        list(range(124, 197))]

# fid = open('/Users/sudregp/data/prs/fmri_kids_all.txt', 'r')
# subjs = [line.rstrip() for line in fid]
# fid.close()
# fid = open('/Users/sudregp/data/prs/fmri_adults_all.txt', 'r')
# subjs += [line.rstrip() for line in fid]
# fid.close()

fid = open('/Users/sudregp/data/baseline_prediction/rsfmri_3minWithClinical.tsv', 'r')
subjs = [line.rstrip() for line in fid]
fid.close()


for trim in trimmed:
    for a, atlas in enumerate(atlases):
        data_dir = '/Users/sudregp/data/baseline_prediction/rsfmri/%s/' % atlas
        fid = open('/Users/sudregp/data/baseline_prediction/rsfmri/%s+aseg_REN_all.niml.lt' % atlas)
        roi_labels = {}
        for line in fid:
            if line[0] == '"':
                num, roi = line.rstrip().split(' ')
                roi_labels[int(num.replace('"', ''))] = roi.replace('"', '')
        pmats, kmats, smats = [], [], []
        for sid, s in enumerate(subjs):
            # as long as the first roi is not empty, we should be fine here
            num_trs = 0
            subj_data = []
            for r in rois[a]:
                fname = data_dir + '/%s/%d.1D' % (s, r)
                roi_data = np.genfromtxt(fname)
                roi_data = roi_data[roi_data != 0]
                num_trs = max(num_trs, len(roi_data))
                if trim:
                    max_trs = min(123, num_trs)
                    trim_suffix = '_trimmed'
                else:
                    max_trs = num_trs
                    trim_suffix = ''
                # sometimes the mask doesn't cover the region
                if len(roi_data) == 0:
                    subj_data.append([np.nan] * max_trs)
                else:
                    subj_data.append(roi_data[:max_trs])
            print('subject %d, maskid %s, num_trs %d, %s, %s' % (sid + 1, s,
                                                                 num_trs,
                                                                 atlas,
                                                                 trim))
            mid = int(np.floor(max_trs / 2))
            first = np.array(subj_data)[:, :mid]
            second = np.array(subj_data)[:, mid:]
            pdata, kdata, sdata, cnames = [], [] ,[], []
            for comb in combinations(range(first.shape[0]), 2):
                x1 = first[comb[0], :]
                y1 = first[comb[1], :]
                x2 = second[comb[0], :]
                y2 = second[comb[1], :]

                if (np.isnan(x1[0]) or np.isnan(y1[0]) or
                    np.isnan(x2[0]) or np.isnan(x2[0])):
                    kdata.append(np.nan)
                    sdata.append(np.nan)
                    pdata.append(np.nan)
                else:
                    val1, p = stats.kendalltau(x1, y1)
                    val2, p = stats.kendalltau(x2, y2)
                    kdata.append(np.abs(val2-val1))

                    val1, p = stats.spearmanr(x1, y1)
                    val2, p = stats.spearmanr(x2, y2)
                    sdata.append(np.abs(val2-val1))

                    val1, p = stats.pearsonr(x1, y1)
                    val2, p = stats.pearsonr(x2, y2)
                    pdata.append(np.abs(val2-val1))
                cnames.append('%s_TO_%s' % (roi_labels[rois[a][comb[0]]],
                                            roi_labels[rois[a][comb[1]]]))
            kmats.append([int(s)] + kdata)
            smats.append([int(s)] + sdata)
            pmats.append([int(s)] + pdata)

        out_fname = '/Users/sudregp/tmp/kendallAbsDiff_%s%s.csv' % (atlas, trim_suffix)
        data = pd.DataFrame(kmats, columns=['maskid'] + cnames)
        data.to_csv(out_fname)

        out_fname = '/Users/sudregp/tmp/spearmanAbsDiff_%s%s.csv' % (atlas, trim_suffix)
        data = pd.DataFrame(smats, columns=['maskid'] + cnames)
        data.to_csv(out_fname)

        out_fname = '/Users/sudregp/tmp/pearsonAbsDiff_%s%s.csv' % (atlas, trim_suffix)
        data = pd.DataFrame(pmats, columns=['maskid'] + cnames)
        data.to_csv(out_fname)