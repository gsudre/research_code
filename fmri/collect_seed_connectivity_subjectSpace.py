# Similar to the collect_atlas function, but here we focus on a single seed,
# which can be a combination of ROIs.
#
# GS, 04/2018

#
import numpy as np
import pandas as pd


trimmed = [False, True]
seed = [48, 68, 71, 83, 103, 106]  # L and R rostralanteriorcingulate, posteriorcingulate and caudalanteriorcingulate
all_rois = [range(5, 10+1) + range(13, 15+1) + [17, 20] + range(25, 33+1) + [36] +
         range(47, 80+1) + range(82, 115+1)]
rois = [r for r in all_rois[0] if r not in seed]

fid = open('/Users/sudregp/data/prs/maskids_503.txt', 'r')
subjs = [line.rstrip() for line in fid]
fid.close()


for trim in trimmed:
    print trim
    data_dir = '/Users/sudregp/data/fmri_prs_ss/aparc/'
    fid = open('/Users/sudregp/data/prs/aparc+aseg_REN_all.niml.lt')
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
        seed_data = []
        for r in seed:
            fname = data_dir + '/%s/%d.1D' % (s, r)
            roi_data = np.genfromtxt(fname)
            num_trs = max(num_trs, len(roi_data))
            if trim:
                max_trs = min(123, num_trs)
                out_fname = '/Users/sudregp/tmp/seed_trimmed.csv'
            else:
                max_trs = num_trs
                out_fname = '/Users/sudregp/tmp/seed.csv' 
            seed_data.append(roi_data[:max_trs])
        seed_data = np.sum(seed_data, axis=0)
        subj_data = []
        for r in rois:
            fname = data_dir + '/%s/%d.1D' % (s, r)
            roi_data = np.genfromtxt(fname)
            num_trs = max(num_trs, len(roi_data))
            subj_data.append(np.arctanh(np.corrcoef(seed_data[:max_trs], roi_data[:max_trs])[0, 1]))
        mats.append([int(s)] + list(subj_data))
    corr_mats = np.array(mats)

    cnames = ['%s' % roi_labels[i] for i in rois]
    data = pd.DataFrame(corr_mats, columns=['maskid'] + cnames)
    
    data.to_csv(out_fname, index=False)
