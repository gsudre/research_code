import os
import nibabel as nb
import numpy as np
import networkx as nx

home = os.path.expanduser('~')


def corr2_coeff(A,B):
    # Rowwise mean of input arrays & subtract from input arrays themeselves
    A_mA = A - A.mean(1)[:,None]
    B_mB = B - B.mean(1)[:,None]

    # Sum of squares across rows
    ssA = (A_mA**2).sum(1);
    ssB = (B_mB**2).sum(1);

    # Finally get corr coeff
    return np.dot(A_mA,B_mB.T)/np.sqrt(np.dot(ssA[:,None],ssB[None]))


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

G = nx.Graph()
G.add_nodes_from(range(nvoxels_msk))

vox_chunk = 1000
cnt = 0
while cnt < nvoxels:
    print(cnt)
    mymax = min(cnt + vox_chunk, nvoxels_msk)
    cc = corr2_coeff(data, data[cnt:mymax, :])
    gc = cc>.25
    gc_idx = np.nonzero(gc)
    my_edges = []
    for i, j in zip(*gc_idx):
        my_edges.append((i, j + cnt, {'weight': cc[i, j]})) 
    G.add_edges_from(my_edges)
    cnt += vox_chunk