# script that crawls through several *trialOrder.txt files looking for the best match to a set of events of a subject
import os
import glob
home = os.path.expanduser('~')

data_dir = '/mnt/neuro/MEG_data/analysis/stop/parsed/'
behavior_dir = '/mnt/neuro/MEG_behavioral/all_behavioral_junk/'

subj = 'BSDZFFWU'

######## END of VARIABLES #########

fname = data_dir+'/%s_event_order.txt'%subj
fid = open(fname, 'r')
events = [line.rstrip() for line in fid]
fid.close()

order_files = glob.glob(behavior_dir + '*.txt')
num_matched = []
for fname in order_files:
    # these files haven't been converted to table yet. So, we'll need to read the trial order straight from the .txt
    behavior = []
    fid = open(fname, 'r')
    for line in fid:
        if line.find('Procedure: StGTrial')>=0:
            behavior.append('STG')
        elif line.find('Procedure: StITrial')>=0:
            behavior.append('STI')
        elif line.find('Procedure: StBTrial')>=0:
            behavior.append('STB')
    fid.close()

    # check how many events match starting from the first one
    cnt = 0
    match = True
    while cnt<min(len(behavior),len(events)) and match:
        match = behavior[cnt]==events[cnt]
        cnt += 1
    num_matched.append(cnt)
best_match = max(num_matched)
print subj
print 'Best matched: %s (%d)'%(order_files[num_matched.index(best_match)], best_match)
