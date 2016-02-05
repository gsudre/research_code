''' Transforms a set of longitudinal scans into cross-sectional. When solving ties for the same person, it first removes rows that have data removed, and then keeps the one with the latest mask id. '''

import numpy as np
import csv
fname = '/Users/sudregp/data/solar_paper_v2/dti_mean_phenotype_cleanedWithinTract3sd_adhd.csv'
data = np.recfromcsv(fname)
subjs = data['id']
keep_me = []
for s in np.unique(subjs):
    idx = [i for i in range(data.shape[0]) if data['id'][i] == s]
    # find rows with least amount of blanks
    num_blanks = []
    cnt = 0
    for i in idx:
        for d in data[i]:
            if d == np.NaN:
                cnt += 1
        num_blanks.append(cnt)
    best = np.nonzero(num_blanks == np.min(num_blanks))[0]
    # if there is a tie, choose the row with the biggest mask id
    if len(best) == 1:
        keep_me.append(idx[best[0]])
    else:
        top_maskid = 0
        for b in best:
            top_maskid = max(top_maskid, data['maskid'][idx[b]])
        keep_me.append([i for i in idx if data['maskid'][i] == top_maskid][0])
new_data = [data[i] for i in keep_me]
new_data = [list(data.dtype.names)] + new_data
out_fname = fname[:-4] + '_nodups.csv'
fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(new_data)
fout.close()
