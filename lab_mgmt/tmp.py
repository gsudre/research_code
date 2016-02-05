import shutil
import os
import glob

data_dir = '/mnt/v2/CIVET-1.1.10/CIVET5/'
out_file = '/Users/sudregp/Documents/philip/civet5.csv'

# figure out list of subjects
subj_list = glob.glob(data_dir + '/*')
all_data = []
headers = ['index']

# for each subject, create a list of NAs
for subj in subj_list:
    subj_id = int(subj.split('/')[-1])
    print subj_id
    fname = subj + '/segment/nih_chp_%05d_fine_structures.dat'%subj_id
    if os.path.exists(fname):
        subj_data = ['NA' for i in range(255)]
        # replace the ones with proper indexes in the subject file
        fid = open(fname, 'r')
        for line in fid:
            subj_data[int(line.lstrip().split(' ')[0])-1] = line.split(' ')[-1].rstrip()
        fid.close()
        all_data.append(subj_data)
        headers.append(str(subj_id))
    else:
        print '\tNot found!'

# output to text file
fid = open(out_file, 'w')
fid.write(','.join(headers) + '\n')
for i in range(255):
    idx_data = [j[i] for j in all_data]
    fid.write(str(i+1) + ',' + ','.join(idx_data) + '\n')
fid.close()