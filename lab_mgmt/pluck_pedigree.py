''' Script to pluck out from a pedigree file all entries associated with a
list of IDs. '''


import sys
import numpy as np
import numpy.lib.recfunctions


# if len(sys.argv) != 3:
#     raise ValueError('Wrong number of arguments!\n' +
#                      'Usage: python pluck_pedigree.py pedigree_file id_file')
# ped_fname = sys.argv[1]
# id_fname = sys.argv[2]
ped_fname = '/Volumes/Shaw/pedigrees/master/pedigree_20170127.csv'
id_fname = '/Users/sudregp/tmp/oi.txt'
out_fname = '/Users/sudregp/tmp/new_pedigree.csv'

fid = open(id_fname)
ids = [line.rstrip() for line in fid]
fid.close()

data = np.recfromcsv(ped_fname)
# rows to grab
grab = []
# rows to highlight
mark = []
for myid in ids:
    row = np.nonzero(data['id'] == myid)[0]
    if len(row) == 0:
        print '%s not in pedigree file!' % myid
    else:
        mark.append(row[0])
        # if we have found the MRN, grab everybody in the same family
        rows = np.nonzero(data['famid'] == data['famid'][row])[0]
        grab += list(rows)
mark = np.unique(mark)
grab = np.unique(grab)

# create pedigree with only families highlighted here
new_data = np.lib.recfunctions.append_fields(data, 'pheno', data.shape[0]*[0],
                                             dtypes='int', usemask=False,
                                             asrecarray=True)
new_data['pheno'][mark] = 1
new_data = new_data[grab]

np.savetxt(out_fname, new_data, delimiter=",",
           header=','.join(new_data.dtype.names), fmt='%s,%s,%s,%d,%d,%d,%d',
           comments='')
