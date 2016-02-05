# compiles the results of Martin's software into a CSV. Replaces his GUI
import os
import numpy as np
home = os.path.expanduser('~')

maskid_fname = home + '/DTIAtlasFiberAnalyzer/maskids_cs.txt'
data_dir = home + '/data/slicer/output_cs/'
props = ['fa','md','ad','rd']
tract = 'Arc_L'
out_dir = data_dir + '/FiberProfiles/%s_resampled/'%tract

fid = open(maskid_fname, 'r')
maskids = [line.rstrip() for line in fid]
fid.close()

for prop in props:
    out_fname = '%s_%s_resampled.csv'%(prop,tract)
    
    # grab the 3rd column for each mask id
    data = []
    header = 'Arc_length vs Data'
    for m in maskids:
        fname = data_dir + '/Cases/%s/%s_%s_resampled_%s.fvp'%(m,m,tract,prop)
        res = np.genfromtxt(fname,delimiter=',',skip_header=5)
        data.append(res[:,2])
        header = header + ',' + m

    # add the first and last columns
    data = [res[:,0]] + data

    fname = data_dir + '/Fibers/%s_resampled_%s.fvp'%(tract, prop)
    res = np.genfromtxt(fname,delimiter=',',skip_header=5)
    data.append(res[:,2])
    header += ',Atlas'

    # check that we have the folder
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    fid = open(out_dir + out_fname, 'w')
    fid.write(header + '\n')
    nrows = len(data[0])
    for i in range(nrows):
        fid.write(','.join(['%.7f'%d[i] for d in data]) + '\n')
    fid.close()