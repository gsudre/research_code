# Collects cortical volumes from CIVET output
import re
import os

maskid_fname = '/Users/sudregp/tmp/3tc.txt'
output_fname = '/Users/sudregp/tmp/civet_volumes_3t.csv'
civet_dir = '/mnt/shaw/cortical_civet/ncr_maskids/'

fid = open(maskid_fname, 'r')
maskids = [line.rstrip() for line in fid]
fid.close()

p = re.compile('\S+') # non-white spaces
# old header for nih_chp_%s_lobes.dat'
# header = 'maskid,CSF,GM,WM,1,2,3,4,5,6,7,8,17,30,45,57,59,67,73,76,83,105,210,211,212,213,214,215,216,217,218,219,232,233,243,248'
# header for nih_chp_%s_fine_structures.dat'
header = 'maskid,CSF,GM,WM,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,23,25,26,27,28,29,30,32,33,34,35,36,37,38,39,41,43,45,50,52,53,54,56,57,59,60,61,62,63,64,67,69,70,72,73,74,75,76,80,83,85,88,90,97,98,99,101,102,105,108,110,112,114,118,119,125,128,130,132,133,139,140,145,154,159,164,165,175,196,203,232,233,251,254,255'

fout = open(output_fname,'w')
fout.write(header + '\n')
for m in maskids:
    print m
    found = True
    # grab CSF, GM, WM
    fname = civet_dir + '%s/classify/nih_chp_%s_cls_volumes.dat'%(m,m)
    if os.path.exists(fname):
        fid = open(fname, 'r')
        # grab the last number of each line
        mdata = [float(p.findall(line)[-1]) for line in fid]
        fid.close()

        # grab label data
        fname = civet_dir + '%s/segment/nih_chp_%s_fine_structures.dat'%(m,m)
        if os.path.exists(fname):
            fid = open(fname, 'r')
            # grab the last number of each line. I have already checked and the labels are always the same for all subjects
            mdata = mdata + [float(p.findall(line)[-1]) for line in fid]
            fid.close()

            # only writes to table if both files were found
            fout.write(m + ',')
            fout.write(','.join([str(i) for i in mdata]))
            fout.write('\n')

fout.close()
