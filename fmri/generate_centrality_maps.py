import os
import nibabel as nb
import numpy as np
import networkx as nx

home = os.path.expanduser('$SL')

mask_fname = home + '/tmp/gray_matter_mask.nii'
data_fname = home + '/tmp/sub-2206_std.nii.gz'
thresh = .25

mask = nb.load(mask_fname)

# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels_msk = np.sum(gv)

img = nb.load(data_fname)
x, y, z, trs = img.get_data().shape
nvoxels = x * y * z
data = np.reshape(img.get_data(), [nvoxels, trs])[gv, :]

# I couldn't find a way to calculate overall correlation without running out of
# memory, even in the cluster. So, instead I can just create a graph and place
# edges in a per-voxel basis
nvoxels = 5
G = nx.Graph()
G.add_nodes_from(range(nvoxels))
for v in range(nvoxels):
    cc = np.corrcoef(data, data[v])
#         for node in range(nfeats):
#             G.add_node(node)
# have to split matrix so it all fits into memory
# number of rows in one chunk
SPLITROWS = 1000

numrows = data.shape[0]

# subtract means form the input data
data -= np.mean(data, axis=1)[:,None]

# normalize the data
data /= np.sqrt(np.sum(data*data, axis=1))[:,None]

# reserve the resulting table onto HDD
res = np.memmap("/lscratch/"+os.getenv('SLURM_JOBID')+"/mydata.dat", 'float64', mode='w+', shape=(numrows, numrows))

for r in range(0, numrows, SPLITROWS):
    for c in range(0, numrows, SPLITROWS):
        r1 = r + SPLITROWS
        c1 = c + SPLITROWS
        print(r1, c1)
        chunk1 = data[r:r1]
        chunk2 = data[c:c1]
        res[r:r1, c:c1] = np.dot(chunk1, chunk2.T)

cc[cc<=thresh] = 0
cc[cc]