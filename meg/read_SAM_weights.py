# Function to read SAM weights dumped file and saved it with the subject's name
# by Gustavo Sudre, July 2014
import numpy as np
import sys


fname = sys.argv[1]
subj = sys.argv[2]
fid = open(fname,'r')
nchans=0
nweights=0
location = []
for line in fid:
    if line.find('NumChans')==0:
        nchans=int(line.rstrip().split(' ')[-1])
    elif line.find('NumWeights')==0:
        nweights=int(line.rstrip().split(' ')[-1])
        # it comes second, so we can initialize the matrix
        weights = np.zeros([nweights,nchans])
    elif line.find('Location[')==0:
        coord = line.rstrip().split(',')
        x = float(coord[0].split(' ')[-1])
        y = float(coord[1])
        z = float(coord[2].split(' ')[1])
        location.append([x, y, z])
    elif line.find('Weights')==0:
        i = int(line.split('[')[1].split(']')[0])
        j = int(line.split('[')[2].split(']')[0])
        weights[i,j] = float(line.rstrip().split('=')[1])
np.savez(subj+'_weights',weights=weights,location=location)