''' Matches subjects so we have an equal number of remission, persistent, and NVs '''

import numpy as np
import pdb
from scipy import stats

def get_diff_matches(subjs, d):
# need to return the row and age difference
    min_diff = {}
    for s in subjs:
        base_ages = age[s][age[s]<split_age]
        fu_ages = age[s][age[s]>split_age]
   	diff_ages = [np.abs(i-j) for i in base_ages for j in fu_ages]
   	age_pairs = [[i, j] for i in base_ages for j in fu_ages]
   	best_diff_idx = np.argmin(np.abs(diff_ages - d))
   	min_diff[s] = [diff_ages[best_diff_idx],
   	                [rows[s][np.nonzero(age[s]==age_pairs[best_diff_idx][0])[0]],
   	                 rows[s][np.nonzero(age[s]==age_pairs[best_diff_idx][1])[0]]],
   	                s,
   	                age_pairs[best_diff_idx][1] - age_pairs[best_diff_idx][0]]
    chosen = min_diff.keys()[0]
    for subj in min_diff.keys():
        if np.min([min_diff[chosen][0],min_diff[subj][0]]) == min_diff[subj][0]:
            chosen = subj
    return min_diff[subj]


csv_file = '/Users/sudregp/data/structural/gf_1473_dsm45.csv'
nv_csv_file = '/Users/sudregp/data/structural/15T_ADD_ADT_OCD_NV_scans_2011_06_27_clean.csv'
split_age = 18
dsm = 5
ratio = 2 # 2 for 2:1 ratio of NVs to other groups, or another number
thresh = .07
gf_fname = csv_file[:-4] + '_matched_on' + str(split_age) + '_dsm' + str(dsm) + '_diff_' + str(ratio) + 'to1.csv'
maskid_fname = '/Users/sudregp/data/structural/maskids_dsm' + str(dsm) + '_' + str(ratio) + 'to1.txt'

gf = np.recfromcsv(csv_file)
gf_nv = np.recfromcsv(nv_csv_file)

nv_rows = [i for i in range(len(gf_nv)) if gf_nv[i]['dx']=='NV' or gf_nv[i]['dx']=='NVS']
rem_rows = [i for i in range(len(gf)) if gf[i]['outcomedsm%d'%dsm] == '"remission"']
per_rows = [i for i in range(len(gf)) if gf[i]['outcomedsm%d'%dsm] == '"persistent"']

rem_subjects = list(np.unique(gf[rem_rows]['personx']))
per_subjects = list(np.unique(gf[per_rows]['personx']))
nv_subjects = list(np.unique(gf_nv[nv_rows]['id']))

# let's create a few dictionaries to make life easier later
age = {}
sex = {}
rows = {}
num_scans = {}
group = []
cur_subjects = list(per_subjects + rem_subjects)
for subj in cur_subjects:
    # use any age restrictions, of QC values, here
    good_scans = [i for i in range(len(gf)) if gf[i]['personx'] == subj and
                                                gf[i]['qc_civet']<3.5 and
                                                gf[i]['qc_sub1']=='"PASS"']
    if (len(good_scans) > 0) and (np.min(gf[good_scans]['agescan'])<split_age) and (np.max(gf[good_scans]['agescan'])>split_age):
        rows[subj] = good_scans
        age[subj] = gf[rows[subj]]['agescan']
        sex[subj] = gf[rows[subj][0]]['sexx']
        num_scans[subj] = len(good_scans)
    else:
        if subj in per_subjects:
            per_subjects.remove(subj)
        elif subj in rem_subjects:
            rem_subjects.remove(subj)

nv_subjects_old = list(nv_subjects)
for subj in nv_subjects_old:
    good_scans = [i for i in range(len(gf_nv)) if gf_nv[i]['id'] == subj and gf_nv[i]['visual_inspect_rank_axial']=='1_good']
    if (len(good_scans) > 0) and (np.min(gf_nv[good_scans]['agescan'])<split_age) and (np.max(gf_nv[good_scans]['agescan'])>split_age):
        rows[subj] = good_scans
        age[subj] = gf_nv[rows[subj]]['agescan']
        sex[subj] = gf_nv[rows[subj][0]]['sex']
        num_scans[subj] = len(good_scans)
    else:
        nv_subjects.remove(subj)

rem_matches = []
per_diffs = []
rem_diffs = []
rm = []
good_rows = []
sym_exported_ages = []
subjects = []
num_males = 0
# we have less persistent subjects than the others, so let's try to keep all of them, and match the others to it
#np.random.shuffle(per_subjects)
for subj in per_subjects:
    found = False
    # find subjects of the same gender first. If none left, discard this subject
    rem_sex_candidates = [s for s, val in sex.iteritems() if val == sex[subj] and s in rem_subjects]
    if len(rem_sex_candidates) > 0:
        # find out how many possible pairs of baseline and follow up scans we have
        base_ages = age[subj][age[subj]<split_age]
        fu_ages = age[subj][age[subj]>split_age]
        diff_ages = [[np.abs(i-j), [rows[subj][np.nonzero(age[subj]==i)[0]], rows[subj][np.nonzero(age[subj]==j)[0]]]] for i in base_ages for j in fu_ages]

        # find the closest subject in each group to each of the possible pairs
        rem_diff_age_match = []
        for d in diff_ages:
            rem_diff_age_match.append(get_diff_matches(rem_sex_candidates, d[0]))

        # choose the pair of deltas with most similar subjects
        best_delta = 0
        for d in range(len(diff_ages)):
            if rem_diff_age_match[d][0] < rem_diff_age_match[best_delta][0]:
                best_delta = d

        # because our pool of remission subjects is smaller we use it to find the best delta
        # mark the rows corresponding to those scans
        good_rows.append(rem_diff_age_match[best_delta][1] + diff_ages[best_delta][1])
        # save it for use later with NVs
        per_diffs.append(diff_ages[best_delta][0])
        rem_diffs.append(rem_diff_age_match[best_delta][3])
        group.append('remission')
        group.append('remission')
        group.append('persistent')
        group.append('persistent')

        # remove those subjects from the pool
        rem_subjects.remove(rem_diff_age_match[best_delta][2])
        rem_matches.append(rem_diff_age_match[best_delta][2])

        # adding the ages to be later exported into gf
        sym_exported_ages.append(gf[rem_diff_age_match[best_delta][1][0]]['agescan'])
        sym_exported_ages.append(gf[rem_diff_age_match[best_delta][1][1]]['agescan'])
        sym_exported_ages.append(gf[diff_ages[best_delta][1][0]]['agescan'])
        sym_exported_ages.append(gf[diff_ages[best_delta][1][1]]['agescan'])
        subjects.append(rem_diff_age_match[best_delta][2])
        subjects.append(rem_diff_age_match[best_delta][2])
        subjects.append(subj)
        subjects.append(subj)

        if sex[subj]=='"M"':
            num_males+=1
    else:
        rm.append(subj)

# remove all subjects for whom we didn't find a match
for subj in rm:
    per_subjects.remove(subj)

# for the NVs, we pick random NVs and ages until we get no difference in age between
# them and the other groups
num_tries = 50000
cnt = 0
pval = 0
while cnt < num_tries and pval<thresh:
    print cnt
    nv_pool = list(nv_subjects)
    nv_matches = []
    nv_ages = []
    nv_exported_ages = []
    nv_exported_subjects = []
    nv_rows = []
    for i in range(ratio*num_males):
        ridx = np.random.randint(len(nv_pool))
        while sex[nv_pool[ridx]] != 'M':
            ridx = np.random.randint(0, len(nv_pool))
        # found a male subject
        subj = nv_pool[ridx]
        nv_pool.remove(subj)
        nv_matches.append(subj)
        # choose a random baseline and FU age
        base_ages = age[subj][age[subj]<split_age]
        rbase = base_ages[np.random.randint(len(base_ages))]
        fu_ages = age[subj][age[subj]>split_age]
        rfu = fu_ages[np.random.randint(len(fu_ages))]
        nv_ages.append(rfu - rbase)
        nv_rows.append([rows[subj][np.nonzero(age[subj]==rbase)[0]], rows[subj][np.nonzero(age[subj]==rfu)[0]]])
        nv_exported_ages.append(rbase)
        nv_exported_ages.append(rfu)
        nv_exported_subjects.append(subj)
        nv_exported_subjects.append(subj)
    num_females_left = sum(np.array([sex[s] for s in nv_pool])=='F')
    females_needed = ratio*(len(per_subjects)-num_males)
    if num_females_left < females_needed:
        print 'ERROR: not enough females left!'
        cnt = num_tries
    else:
        # do the same for females
        for i in range(females_needed):
            ridx = np.random.randint(len(nv_pool))
            while sex[nv_pool[ridx]] != 'F':
                ridx = np.random.randint(0, len(nv_pool))
            subj = nv_pool[ridx]
            nv_pool.remove(subj)
            nv_matches.append(subj)
            base_ages = age[subj][age[subj]<split_age]
            rbase = base_ages[np.random.randint(len(base_ages))]
            fu_ages = age[subj][age[subj]>split_age]
            rfu = fu_ages[np.random.randint(len(fu_ages))]
            nv_ages.append(rfu - rbase)
            nv_rows.append([rows[subj][np.nonzero(age[subj]==rbase)[0]], rows[subj][np.nonzero(age[subj]==rfu)[0]]])
            nv_exported_ages.append(rbase)
            nv_exported_ages.append(rfu)
            nv_exported_subjects.append(subj)
            nv_exported_subjects.append(subj)
        # check if we fulfill our requirement
        pval = np.min([stats.ttest_ind(nv_ages,per_diffs)[1], stats.ttest_ind(nv_ages,rem_diffs)[1]])
        #pval = stats.ttest_ind(nv_ages,per_diffs)[1]
        cnt+=1
if cnt==num_tries:
    print 'Cannot find good NV set, giving up!'
else:
    print 'Age differences, ttest between groups:'
    print 'NV vs persistent:', stats.ttest_ind(nv_ages,per_diffs)[1]
    print 'NV vs remission:', stats.ttest_ind(nv_ages,rem_diffs)[1]
    print 'persistent vs remission:', stats.ttest_ind(rem_diffs,per_diffs)[1]
    # now we need to write up a new gf file. MaskIDs will be needed to retrieve the data
    nv_maskids = [gf_nv[i]['maskid'] for j in nv_rows for i in j]
    sym_maskids = [int(gf[j]['maskid'].split('/')[-1].split('_')[2]) for i in good_rows for j in i]
    mask_ids = sym_maskids + nv_maskids

    # in the gf, we need maskid, subject, group, and age
    subjects = subjects + nv_exported_subjects
    for i in range(2*len(nv_matches)):
        group.append('NV')
    ages2export = sym_exported_ages + nv_exported_ages

    fid = open(gf_fname, 'w')
    fid.write('maskid,subject,group,age\n')
    for i in range(len(mask_ids)):
        fid.write('%05d,%d,%s,%02.02f\n' % (mask_ids[i], subjects[i],
            group[i], ages2export[i]))
    fid.close()
