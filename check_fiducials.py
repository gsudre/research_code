''' Checks and corrects the placement of fiducials in HC file. '''

import re
import sys


def grab_fiducial(text, fidu, hc_file):
    # checks measurement position with respect to dewar
    # which is the first measurement information
    m = re.search('measured ' + fidu + ' (.*)\n\tx = (.*)\n\ty = (.*)\n\tz = (.*)', text)
    if m is None:
        print 'Error: did not find measurement info in ' + hc_file
        sys.exit(-1)
    else:
        return float(m.groups()[1]), float(m.groups()[2]), float(m.groups()[3])

ds = sys.argv[1]
hc_file = ds.split('/')[-2][:-3] + '.hc'
fid = open(ds + '/' + hc_file, 'r')
data = fid.read()

x, y, z = grab_fiducial(data, 'nasion', hc_file)
if not (x > 0 and y > 0 and z < 0):
    print 'Error measuring nasion in ' + ds

x, y, z = grab_fiducial(data, 'left ear', hc_file)
if not (x < 0 and y > 0 and z < 0):
    print 'Error measuring left ear in ' + ds

x, y, z = grab_fiducial(data, 'right ear', hc_file)
if not (x > 0 and y < 0 and z < 0):
    print 'Error measuring right ear in ' + ds

fid.close()
