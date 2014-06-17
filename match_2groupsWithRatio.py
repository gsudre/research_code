''' Matches subjects based on sex, then # of scans, and finally age of baseline '''

import numpy as np
import matplotlib.mlab as mlab

# CSV file to read in
csv_file = '/Users/sudregp/tmp/gf1p5t.csv'
# Name of the column to be added to CSV
var = 'matched'

# define the two groups
groups = ['NV', 'ADHD']
# for every individual in the smaller group, choose this many in the bigger group
match_ratio = 2

# Some other variables to limit usable scans
qc_column = 'raw_rating'
use_twins = 1  # set to 0 if only using rows with column twin==0

gf = np.recfromcsv(csv_file)

group_rows = []
group_subjects = []
for group in groups:
    group_rows.append([i for i in range(len(gf)) if gf[i]['dxgroup']==group])
    group_subjects.append(list(np.unique(gf[group_rows[-1]]['id'])))

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
for subj in (group_subjects[0] + group_subjects[1]):
    # use any age restrictions, or QC values, here
    good_scans = [i for i in range(len(gf)) if gf[i]['id'] == subj and
                                               float(gf[i][qc_column]) <= 2 and
                                               (use_twins or not gf[i]['twin']) and
                                               gf[i]['agescan']>0 and
                                               gf[i]['agescan']<21 and
                                               gf[i]['clasp']<=4]
    if (len(good_scans) > 0):
        rows[subj] = good_scans
        age[subj] = gf[rows[subj]]['agescan']
        sex[subj] = gf[rows[subj][0]]['sex']
        num_scans[subj] = len(good_scans)
    else:
        if subj in group_subjects[0]:
            group_subjects[0].remove(subj)
        else:
            group_subjects[1].remove(subj)

# figure out which of the two groups is the smallest
if len(group_subjects[0]) < len(group_subjects[1]):
    sg = 0
    bg = 1
else:
    sg = 1
    bg = 0
print 'Found more %s than %s subjects.'%(groups[bg], groups[sg])

matches = []
rm = []
# try to keep all the subjects in the smaller group, and match the subjects in the other group to it
for subj in group_subjects[sg]:
    num_matched = 0
    subj_matches = []
    while num_matched < match_ratio:
        # find subjects of the same gender first. If none left, discard this subject
        sex_candidates = [s for s, val in sex.iteritems() if val == sex[subj] and s in group_subjects[bg]]
        if len(sex_candidates) >= (match_ratio-num_matched):
            # narrow it down to how many scans the subject has. If no matches, try the next best thing
            target_num_scans = num_scans[subj]
            while True:
                # this needs to be >= because we might need to change target_num_scans if one group doesn't have the subject
                scan_candidates = [s for s, val in num_scans.iteritems() if val >= target_num_scans and s in sex_candidates]
                if len(scan_candidates) > 0:
                    # if we have subjects with the same number of scans, let's focus on those 
                    equal_scans = [s for s, val in num_scans.iteritems() if val == target_num_scans and s in scan_candidates]
                    if len(equal_scans)>0:
                        scan_candidates = equal_scans

                    # chose the subject with closest baseline age scan
                    target_age = np.min(age[subj])
                    candidates_age = [np.min(age[s]) for s in scan_candidates]
                    closest = np.argmin(abs(candidates_age - target_age))
                    match = scan_candidates[closest]
                    subj_matches.append(match)
                    group_subjects[bg].remove(match)
                    num_matched += 1
                    
                    # before we proceed, check whether getting a new subject is mandatory or not
                    prob = match_ratio-num_matched
                    if prob>0 and prob<1:
                        if np.random.random() > prob:
                            num_matched += 1

                    break
                else:
                    if target_num_scans > 1:
                        target_num_scans -= 1  
                    else:
                        rm.append(subj)
                        break
        else:
            break
    if num_matched >= match_ratio:
        print 'Matched %s %d (%d scans, %s) to %s'%(
                groups[sg],subj,len(rows[subj]),gf[rows[subj][0]]['sex'],
                groups[bg]), subj_matches
        [matches.append(s) for s in subj_matches]


# remove all subjects for whom we didn't find a match
print groups[sg], 'subjects without matches:', rm
for subj in rm:
    group_subjects[sg].remove(subj)

# finally, create new variable and output it to a new file
match_bool = np.zeros(len(gf))
for subj in (matches + group_subjects[sg]):
    match_bool[rows[subj]] = 1
match_bool = mlab.rec_append_fields(gf, var, match_bool)
mlab.rec2csv(match_bool, csv_file[:-4] + '_matched_onSex_onNumScan_onBaseAge_ratio1to%.1f.csv'%match_ratio)
