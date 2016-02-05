''' Read in CPT data and exports it in a better format '''
import numpy as np


fname = '/Users/sudregp/philip/CPT Responses.111215.txt'
fid = open(fname, 'r')

''' The structure is 3 lines of subject info, then 6 lines of letters,
then 6 lines of reaction times '''
subjects, letters, rts = [], [], []
cnt = 1
subj, letter, rt = [], [], []
for line in fid:
    if cnt < 4:
        subj += line.rstrip().split(',')
        cnt += 1
    elif cnt < 10:
        letter += line.rstrip().split(',')
        cnt += 1
    else:
        rt += line.rstrip().split(',')
        if cnt == 15:  # last subject data line
            subjects.append(subj)
            letters.append(letter)
            rts.append(rt)
            cnt = 1
            subj, letter, rt = [], [], []
        else:
            cnt += 1
fid.close()

# spitting out results file
out_fname = '/Users/sudregp/philip/test.csv'
fid = open(out_fname, 'w')
for s in range(len(subjects)):
    # only write letters that are not X and have RT > 100
    write_me = []
    for l in range(len(letters[s])):
        if letters[s][l] != 'X' and len(rts[s][l]) > 0 \
           and float(rts[s][l]) > 100 and len(letters[s][l]) > 0:
            write_me.append(l)
    if len(write_me) > 0:  # only if we have data to write
        date = subjects[s][7]
        lname = subjects[s][1].replace(' ', '')
        fname = subjects[s][0].replace(' ', '')
        fid.write('%s_%s_%s_letters,' % (lname, fname, date))
        fid.write(','.join([letters[s][l] for l in write_me]))
        fid.write('\n')
        fid.write('%s_%s_%s_RTs,' % (lname, fname, date))
        fid.write(','.join([rts[s][l] for l in write_me]))
        fid.write('\n')
fid.close()
