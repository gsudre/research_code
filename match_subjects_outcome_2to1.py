''' Matches subjects so we have an equal number of remission, persistent, and NVs '''

import numpy as np
import pdb
import matplotlib.mlab as mlab


csv_file = '/Users/sudregp/data/structural/gf_1473_dsm45.csv'
var = 'match_outcome'

gf = np.recfromcsv(csv_file)

nv_rows = [i for i in range(len(gf)) if gf[i]['outcomedsm4']=='"NV"']
rem_rows = [i for i in range(len(gf)) if gf[i]['outcomedsm4'] == '"remission"']
per_rows = [i for i in range(len(gf)) if gf[i]['outcomedsm4'] == '"persistent"']

rem_subjects = list(np.unique(gf[rem_rows]['personx']))
per_subjects = list(np.unique(gf[per_rows]['personx']))
nv_subjects = list(np.unique(gf[nv_rows]['personx']))

# let's create a few dictionaries to make life easier later
age = {}
sex = {}
rows = {}
num_scans = {}
for subj in (per_subjects + rem_subjects + nv_subjects):
    # use any age restrictions, of QC values, here
    good_scans = [i for i in range(len(gf)) if gf[i]['personx'] == subj and
                                                gf[i]['qc_civet']<3.5 and
                                                gf[i]['qc_sub1']=='"PASS"']
    if (len(good_scans) > 0) and (np.min(gf[good_scans]['agescan'])<18) and (np.max(gf[good_scans]['agescan'])>18):
        rows[subj] = good_scans
        age[subj] = gf[rows[subj]]['agescan']
        sex[subj] = gf[rows[subj][0]]['sexx']
        num_scans[subj] = len(good_scans)
    else:
        if subj in per_subjects:
            per_subjects.remove(subj)
        elif subj in rem_subjects:
            rem_subjects.remove(subj)
        else:
            nv_subjects.remove(subj)

nv_matches = []
rem_matches = []
rm = []
# we have less persistent subjects than the others, so let's try to keep all of them, and match the others to it
for subj in per_subjects:
    found = False
    # find subjects of the same gender first. If none left, discard this subject
    nv_sex_candidates = [s for s, val in sex.iteritems() if val == sex[subj] and s in nv_subjects]
    rem_sex_candidates = [s for s, val in sex.iteritems() if val == sex[subj] and s in rem_subjects]
    if len(nv_sex_candidates) > 1 or len(rem_sex_candidates) > 0:
        # narrow it down to how many scans the subject has. If no matches, try the next best thing
        target_num_scans = num_scans[subj]
        while True:
            if target_num_scans == 1:
                # couldn't find a good match for this subject
                break

            # this needs to be >= because we might need to change target_num_scans if one group doesn't have the subject
            nv_scan_candidates = [s for s, val in num_scans.iteritems() if val >= target_num_scans and s in nv_subjects]
            rem_scan_candidates = [s for s, val in num_scans.iteritems() if val >= target_num_scans and s in rem_subjects]
            if len(nv_scan_candidates) > 1 and len(rem_scan_candidates) > 0:
                found = True
                # chose the subject with closest median age scan
                target_age = np.median(age[subj])
                candidates_age = [np.median(age[s]) for s in nv_scan_candidates]
                closest = np.argmin(abs(candidates_age - target_age))
                nv_matches.append(nv_scan_candidates[closest])
                nv_subjects.remove(nv_scan_candidates[closest])
                # find another NV
                nv_scan_candidates.remove(nv_scan_candidates[closest])
                candidates_age = [np.median(age[s]) for s in nv_scan_candidates]
                closest = np.argmin(abs(candidates_age - target_age))
                nv_matches.append(nv_scan_candidates[closest])
                nv_subjects.remove(nv_scan_candidates[closest])
                # do the same for remission
                candidates_age = [np.median(age[s]) for s in rem_scan_candidates]
                closest = np.argmin(abs(candidates_age - target_age))
                rem_matches.append(rem_scan_candidates[closest])
                rem_subjects.remove(rem_scan_candidates[closest])
                break
            else:
                target_num_scans -= 1
    if not found:
        rm.append(subj)

# remove all subjects for whom we didn't find a match
for subj in rm:
    per_subjects.remove(subj)

# finally, create new variable and output it to a new file
match_bool = np.zeros(len(gf))
for subj in (nv_matches + rem_matches + per_subjects):
    match_bool[rows[subj]] = 1
match_bool = mlab.rec_append_fields(gf, var, match_bool)
mlab.rec2csv(match_bool, csv_file[:-4] + '_matched_on18_dsm4_2to1.csv')
