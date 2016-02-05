# compares the output CSV file from Martin and the one I create. It's very similar to a diff, but his numbers have varying precision, which screws up diff.
import os
import numpy as np
home = os.path.expanduser('~')

prop = 'rd'
tract = 'Fornix'
fname1 = home + '/tmp/%s_%s_resampled.csv'%(prop,tract)
fname2 = home + '/tmp/fake_output/FiberProfiles/%s_resampled/%s_%s_resampled.csv'%(tract,prop,tract)

d1 = np.recfromcsv(fname1)
d2 = np.recfromcsv(fname2)

if np.all(d1==d2):
    print 'Files are the same!'
else:
    print 'DIFFERENT FILES!'