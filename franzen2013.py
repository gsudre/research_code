import numpy as np
from scipy import stats
import pdb
import spreadsheet
import env

def get_net_conn(pli, roi1, roi2):
    num_subj = pli.shape[0]
    conn = np.zeros([num_subj, len(roi1) * len(roi2)])
    cnt = 0
    for r1 in roi1:
        for r2 in roi2:
            conn[:, cnt] = pli[:, r1, r2]
            cnt += 1
    # average over connections so that we have one value per subject
    conn = stats.nanmean(conn, axis=-1)
    # make sure to not return nan values
    conn = np.delete(conn, np.nonzero(np.isnan(conn) == True))
    return conn


def compare_regions(nv, adhd, band, roi1, roi2):
    nv_conn = get_net_conn(nv[:, band, :, :], roi1, roi2)
    adhd_conn = get_net_conn(adhd[:, band, :, :], roi1, roi2)
    # pdb.set_trace()
    t, p = stats.ttest_ind(nv_conn, adhd_conn)
    return p


execfile('/Users/sudregp/research_code/combine_good_plis.py')

all_adhd = list(res['good_adhds'])
affected = spreadsheet.get_affected_subjects()
affected = set(affected).intersection(set(all_adhd))
adhd, labels = combine_data(list(affected), res['labels'], plis)

pcc = [50, 46, 51, 47]
ripl = [15, 63]
lipl = [14, 62]
mpfc = [28, 52, 29, 53]

print 'PCC - LIPL, theta: ' + str(compare_regions(nv, adhd, 1, pcc, lipl))

print 'PCC - RIPL, theta: ' + str(compare_regions(nv, adhd, 1, pcc, ripl))

print 'RIPL - LIPL, theta: ' + str(compare_regions(nv, adhd, 1, ripl, lipl))

print 'PCC - mPFC, delta: ' + str(compare_regions(nv, adhd, 0, pcc, mpfc))

print 'PCC - RIPL, delta: ' + str(compare_regions(nv, adhd, 0, pcc, ripl))

print 'LIPL - RIPL, delta: ' + str(compare_regions(nv, adhd, 0, lipl, ripl))
