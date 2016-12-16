''' Script to grab the closest matching symptom counts to a pair of MRN and
date. Returns the same input file, added by inatt and HI, the time difference,
and the source of the data.'''


import sys


if len(sys.argv) < 3:
    print 'Need at least 2 arguments!'

# start by checking whether all input files have the necessary columns
if find(sys.argv[1], '.csv') > 0:
    target = read_csv(sys.argv[1])
else:
    target = read_xls(sys.argv[1])

sources = []
for fname in sys.argv[2:]:
    if find(fname, '.csv'):
        sources.append(read_csv(fname))
    else:
        sources.append(read_xls(fname))

# TODO
# medication
