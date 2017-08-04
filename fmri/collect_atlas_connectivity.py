# Matches ROIs from Haskins and DesaiKM atlases to construct connectivity
# matrices across templates
#
# GS, 08/2017

#%%
import numpy as np
import pandas as pd


fid = open('/Users/sudregp/data/prs/Haskins_atlas_code_trimmed.txt')
haskins = {}
for line in fid:
    h, roi, num = line.split(':')
    haskins[roi] = int(num.rstrip())

fid = open('/Users/sudregp/data/prs/desai_atlas_code.txt')
desai = {}
for line in fid:
    h, roi, num = line.split(':')
    desai[roi] = int(num.rstrip())

# use Haskins as base because it has less ROIs
atlas_map = {}
for key, val in haskins.iteritems():
    if key in desai.keys():
        atlas_map[key] = [val, desai[key]]
    else:
        print 'Cannot find %s in desai atlas' % key

data_dir = '/Users/sudregp/data/fmri_prs/'
fid = open('/Users/sudregp/data/prs/fmri_kids_all.txt', 'r')
kids = [line.rstrip() for line in fid][:10]
fid.close()
fid = open('/Users/sudregp/data/prs/fmri_adults_all.txt', 'r')
adults = [line.rstrip() for line in fid][:10]
fid.close()

rois = atlas_map.keys()
mats = []
for s in kids + adults:
    print s
    atlas_id = int(s in adults)
    subj_data = []
    for r in rois:
        fname = data_dir + '/%s/%d.1D' % (s, atlas_map[r][atlas_id])
        roi_data = np.genfromtxt(fname)
        subj_data.append(roi_data)
    subj_data = np.arctanh(np.corrcoef(np.array(subj_data)))
    idx = np.triu_indices_from(subj_data, k=1)
    mats.append([int(s)] + list(subj_data[idx]))
corr_mats = np.array(mats)

cnames = ['%s_TO_%s' % (rois[i], rois[j]) for i, j in zip(idx[0], idx[1])]
data = pd.DataFrame(corr_mats, columns=['maskid'] + cnames)
data.to_csv('test.csv')

#%%


# df.rename(columns={'age^2': 'age2', 'mvmt^2': 'mvmt2'}, inplace=True)

# ntests = corr_mats.shape[1]
# res_mats = np.zeros_like(corr_mats)
# res_mats[:] = np.nan
# for v in range(1, ntests):
#     good_subjs = np.nonzero(~np.isnan(df['conn%d' % v]))[0]
#     est = smf.ols(formula='conn%d ~ age + sex + mvmt + mvmt2' % v, data=df.iloc[good_subjs]).fit()
#     res_mats[good_subjs, v - 1] = est.resid

# out = {'corr_mats': corr_mats, 'res_mats': res_mats}
# io.savemat(data_dir + 'corrs.mat', out)