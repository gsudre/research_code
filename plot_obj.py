from scipy.io import loadmat
from mayavi import mlab
import numpy as np


def plot_surface(surf_name, data, hemi='rh', cmin=None, cmax=None, colorbar=True, smooth=5):
    ''' Plots data in a 3D brain surface using the current Mayavi's mlab window. surf_name is a string with the name of the surface, data is a vector of the same length of the number of points in the surface. Function performs smoothing by default, and set the color of the brain to gray by default for points we don't have data. '''

    surf = loadmat('/Users/sudregp/Documents/surfaces/IMAGING_TOOLS/' + surf_name + '.mat')

    nbr = surf['nbr_' + hemi].astype(int)
    num_voxels = len(data)
    # smoothing data to neighboring voxels with zero value. Algorithm described in MNE-manual-2.7, page 208/356.
    for p in range(smooth):
        S = np.zeros([num_voxels, num_voxels])
        for j in range(num_voxels):
            my_neighbors = nbr[j, :] - 1
            # remove entries that are -1
            my_neighbors = np.delete(my_neighbors, np.nonzero(my_neighbors == -1))
            # number of immediate neighbors with non zero values
            Nj = np.sum(data[my_neighbors] != 0)
            if Nj > 0:
                S[j, my_neighbors] = 1 / float(Nj)
        data = np.dot(S, data)

    # replacing all values that are still 0 by something that is not in the data range.
    data[data == 0] = np.inf

    if cmin is None:
        cmin = np.min(data)
    if cmax is None:
        # check whether we have empty points in the brain. If we do, it has Inf value. If not, the max is the actual maximum of the data
        if len(np.nonzero(np.isinf(data) == True)[0]) == 0:
            cmax = np.max(data)
            add_grey = False
        else:
            cmax = np.unique(np.sort(data))[-2]
            add_grey = True
    else:
        # if cmax was specified, let the person deal with it
        add_grey = False

    surf = mlab.triangular_mesh(surf['coord_' + hemi][0, :], surf['coord_' + hemi][1, :], surf['coord_' + hemi][2, :], surf['tri_' + hemi] - 1, scalars=data, vmax=cmax, vmin=cmin)

    if add_grey:
        # add grey color to scale, and make everything that's infinity that color
        surf.module_manager.scalar_lut_manager.number_of_colors += 1
        lut = surf.module_manager.scalar_lut_manager.lut.table.to_array()
        grey_row = [192, 192, 192, 255]
        # sets the max value in the data range to be gray
        lut = np.vstack((lut, grey_row))
        surf.module_manager.scalar_lut_manager.lut.table = lut

    mlab.colorbar()


def populate_matrix(X, num_vertex, idx):
    ''' X is a matrix of vertices x components, num_vertex is the total number of vertices that final matrix should have, and idx is a vector that maps the vertices in X to the positions in the final matrix. Returns a matrix of size num_vertex by X.shape[1], which is created using the elements from X that are placed in the positions in the new matrix guided by the vector idx. the rest of the matrix is filled with zeros.'''

    if len(idx) != X.shape[0]:
        print 'Error: there should be one index per row of X!'
        return

    X2 = np.zeros([num_vertex, X.shape[1]])

    X2[idx, :] = X
    return X2
