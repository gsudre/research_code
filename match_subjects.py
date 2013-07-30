''' Matches subjects so we have an equal number of ADHDs and NVs '''

import numpy as np
import pdb
import matplotlib.mlab as mlab


csv_file = '/Users/sudregp/Documents/surfaces/gf_1473.csv'
var = 'MATCH_script'

gf = np.recfromcsv(csv_file)

nv_rows = [i for i in range(len(gf)) if gf[i]['dx'] == '"NV"']
adhd_rows = [i for i in range(len(gf)) if gf[i]['dx'] == '"ADHD"']

adhd_subjects = list(np.unique(gf[adhd_rows]['personx']))
nv_subjects = list(np.unique(gf[nv_rows]['personx']))

# let's create a few dictionaries to make life easier later
age = {}
sex = {}
rows = {}
num_scans = {}
for subj in (adhd_subjects + nv_subjects):
    good_scans = [i for i in range(len(gf)) if gf[i]['personx'] == subj and gf[i]['agescan'] > 10 and gf[i]['agescan'] < 21]
    if len(good_scans) > 0:
        rows[subj] = good_scans
        age[subj] = gf[rows[subj]]['agescan']
        sex[subj] = gf[rows[subj][0]]['sexx']
        num_scans[subj] = len(good_scans)
    else:
        if subj in adhd_subjects:
            adhd_subjects.remove(subj)
        else:
            nv_subjects.remove(subj)

matches = []
rm = []
# we find the nv subject that best matches the adhd one
for subj in adhd_subjects:
    found = False
    # check how many scans she has. only continue if there is > 1 scans
    if num_scans[subj] >= 2:
        # find subjects of the same gender first. If none left, discard this subject
        sex_candidates = [s for s, val in sex.iteritems() if val == sex[subj] and s in nv_subjects]
        if len(sex_candidates) > 0:
            # narrow it down to how many scans the subject has. If no matches, try the next best thing
            target_num_scans = num_scans[subj]
            while True:
                if target_num_scans == 1:
                    # couldn't find a good match for this subject
                    break

                scan_candidates = [s for s, val in num_scans.iteritems() if val == target_num_scans and s in nv_subjects]
                if len(scan_candidates) > 0:
                    found = True
                    # chose the subject with closest median age scan
                    target_age = np.median(age[subj])
                    candidates_age = [np.median(age[s]) for s in scan_candidates]
                    closest = np.argmin(abs(candidates_age - target_age))
                    matches.append(scan_candidates[closest])
                    nv_subjects.remove(scan_candidates[closest])
                    break
                else:
                    target_num_scans -= 1
    if not found:
        rm.append(subj)

for subj in rm:
    adhd_subjects.remove(subj)

# finally, create new variable and output it to a new file
match_bool = np.zeros(len(gf))
for subj in (matches + adhd_subjects):
    match_bool[rows[subj]] = 1
match_bool = mlab.rec_append_fields(gf, var, match_bool)
mlab.rec2csv(match_bool, csv_file[:-4] + '_matched.csv')
