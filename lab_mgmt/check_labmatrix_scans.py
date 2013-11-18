# Checks labmatrix scan records agains what's in the server

import numpy as np
import glob
import os


# needs to have mask ids in the first column and mrns in the second
res = np.recfromtxt('/Users/sudregp/tmp/Results.txt', delimiter='\t', skip_header=1)
maskid_dirs = glob.glob('/Volumes/neuro/data_by_maskID/*')
maskids = [int(m.split('/')[-1]) for m in maskid_dirs]

# checking that all mask ids in the server are also in labmatrix
for m in maskids:
    found = False
    for r in res:
        found = found or (int(r[0])==m)
        if int(r[0])==m:
            mrn = r[1]

    if not found:
        print m, 'not in Labmatrix'
    else:
        folder = '/Volumes/neuro/data_by_maskID/%04d/'%m
        dataFolder = glob.glob(folder + '/20*')
        txtfile = glob.glob(dataFolder[0] + '/README*.txt')
        fid = open(txtfile[0])  
        text = fid.read()
        pos = text.lower().find(str(mrn))
        if pos < 0: 
            print m, 'in Labmatrix, but wrong MRN'
        fid.close()
''' We know already that mask ids 335, 334, and 435 have the wrong MRNs in the README file, but their people are correct '''

# checking whether all labmatrix scans are in the server
for r in res:
    if not os.path.exists('/Volumes/neuro/data_by_maskID/%04d/'%int(r[0])):
        print r[0], 'not found in the server'