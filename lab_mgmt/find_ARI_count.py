import numpy as np

fname = '/Users/sudregp/tmp/Results_dan_ARIs_clean.txt'
data = np.recfromtxt(fname, delimiter='\t')

NVs_with_two_ARIs = 0
ADHDs_with_two_ARIs = 0
good_subjs = []
subjs = [row[0] for row in data[1:]]
subjs = np.unique(subjs)
for subj in subjs:
    has_P = False
    has_S = False
    for row in range(len(data)):
        if data[row][0]==subj and data[row][1].upper()=='P':
            has_P = True
            subj_row = row
        if data[row][0]==subj and data[row][1].upper()=='S':
            has_S = True
    if has_P and has_S:
        good_subjs.append(subj)
        if data[subj_row][2].upper()=='ADHD':
            ADHDs_with_two_ARIs += 1
        else:
            NVs_with_two_ARIs += 1
print 'Subjects with 2 ARIs: %d/%d'%(NVs_with_two_ARIs+ADHDs_with_two_ARIs,len(subjs))
print 'NV: %d'%NVs_with_two_ARIs
print 'ADHD: %d'%ADHDs_with_two_ARIs
for s in good_subjs:
    print s