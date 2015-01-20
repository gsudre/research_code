''' Matches subjects based on sex, then # of scans, and finally age of baseline '''

import numpy as np
import matplotlib.mlab as mlab

# CSV file to read in
csv_file = '/Users/sudregp/tmp/gf_1p5.csv'
# Name of the column to be added to CSV
var = 'matched'
# Some other variables to limit usable scans
rating_limit = 7  # qc ratings < this are included
qc_column = 'raw_rating'
min_age = 0
max_age = 100
use_twins = 0  # set to 0 if only using rows with column twin==0

gf = np.recfromcsv(csv_file)

nv_rows = [i for i in range(len(gf)) if gf[i]['dxgroup']=='NV']
adhd_rows = [i for i in range(len(gf)) if gf[i]['dxgroup']=='ADHD']

nv_subjects = list(np.unique(gf[nv_rows]['id']))
adhd_subjects = list(np.unique(gf[adhd_rows]['id']))

# First we clean up the QC column to make sure it only has numbers and NaNs
for row in range(len(gf)):
    try:
        gf[row][qc_column] = float(gf[row][qc_column])
    except ValueError:
        gf[row][qc_column] = np.nan

# let's create a few dictionaries to make life easier later
age = {}
sex = {}
rows = {}
num_scans = {}
# figuring out what are the good scans for each subject
for subj in (adhd_subjects + nv_subjects):
    # use any age restrictions, or QC values, here
    good_scans = [i for i in range(len(gf)) if gf[i]['id'] == subj and
                                               float(gf[i][qc_column]) < 4 and
                                               (use_twins or not gf[i]['twin']) and
                                               gf[i]['agescan']>min_age and
                                               gf[i]['agescan']<max_age and
                                               gf[i]['race']=='W']
    if (len(good_scans) > 0):
        rows[subj] = good_scans
        age[subj] = gf[rows[subj]]['agescan']
        sex[subj] = gf[rows[subj][0]]['sex']
        num_scans[subj] = len(good_scans)
    else:
        if subj in adhd_subjects:
            adhd_subjects.remove(subj)
        else:
            nv_subjects.remove(subj)

nv_matches = []
rm = []
# we have less adhd subjects than nvs, so let's try to keep all of them, and match the others to it
for subj in adhd_subjects:
    found = False
    # find subjects of the same gender first. If none left, discard this subject
    nv_sex_candidates = [s for s, val in sex.iteritems() if val == sex[subj] and s in nv_subjects]
    if len(nv_sex_candidates) > 0:
        # narrow it down to how many scans the subject has. If no matches, try the next best thing
        target_num_scans = num_scans[subj]
        while True:
            # this needs to be >= because we might need to change target_num_scans if one group doesn't have the subject
            nv_scan_candidates = [s for s, val in num_scans.iteritems() if val >= target_num_scans and s in nv_sex_candidates]
            if len(nv_scan_candidates) > 0:
                found = True
                # if we have subjects with the same number of scans, let's focus on those 
                equal_scans = [s for s, val in num_scans.iteritems() if val == target_num_scans and s in nv_scan_candidates]
                if len(equal_scans)>0:
                    nv_scan_candidates = equal_scans

                # chose the subject with closest baseline age scan
                target_age = np.min(age[subj])
                candidates_age = [np.min(age[s]) for s in nv_scan_candidates]
                closest = np.argmin(abs(candidates_age - target_age))
                nv_match = nv_scan_candidates[closest]
                nv_matches.append(nv_match)
                nv_subjects.remove(nv_match)
                print 'Matched ADHD %d (%d scans, %s) to NV %d (%d scans, %s).'%(subj,len(rows[subj]),gf[rows[subj][0]]['sex'],
                    nv_match,len(rows[nv_match]),gf[rows[nv_match][0]]['sex'])
                break
            else:
                target_num_scans -= 1
    if not found:
        rm.append(subj)

# remove all subjects for whom we didn't find a match
print 'ADHD subjects without matches:', rm
for subj in rm:
    adhd_subjects.remove(subj)

# finally, create new variable and output it to a new file
match_bool = np.zeros(len(gf))
for subj in (nv_matches + adhd_subjects):
    match_bool[rows[subj]] = 1
match_bool = mlab.rec_append_fields(gf, var, match_bool)
mlab.rec2csv(match_bool, csv_file[:-4] + '_matched_onSex_onNumScan_onBaseAge.csv')
