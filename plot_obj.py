from scipy.io import loadmat
from mayavi import mlab
import numpy as np

# TODO:
#  . INCREASE FONT SIZE IN COLORBAR


def picker_callback(picker_obj):
    ''' Function to use the point that was selected in the surface. Copied from http://docs.enthought.com/mayavi/mayavi/auto/example_pick_on_surface.html '''

    picked = picker_obj.actors
    if surf.actor.actor._vtk_obj in [o._vtk_obj for o in picked]:
        # m.mlab_source.points is the points array underlying the vtk
        # dataset. GetPointId return the index in this array.
        x_, y_ = np.lib.index_tricks.unravel_index(picker_obj.point_id,
                                                                s.shape)
        print "Data indices: %i, %i" % (x_, y_)
        # n_x, n_y = s.shape
        # cursor.mlab_source.set(x=x_ - n_x/2.,
        #                        y=y_ - n_y/2.)
        # cursor3d.mlab_source.set(x=x[x_, y_],
                                 # y=y[x_, y_],
                                 # z=z[x_, y_])


def plot_surface(surf_name, data_orig, hemi='rh', cmin=None, cmax=None, colorbar=True, smooth=5):
    ''' Plots data in a 3D brain surface using the current Mayavi's mlab window. surf_name is a string with the name of the surface, data is a vector of the same length of the number of points in the surface. Function performs smoothing by default, and set the color of the brain to gray by default for points we don't have data. '''

    surf = loadmat('/Users/sudregp/Documents/surfaces/IMAGING_TOOLS/' + surf_name + '.mat')

    nbr = surf['nbr_' + hemi].astype(int)

    # making sure we don't change the original data
    data = data_orig.copy()
    num_voxels = len(data)
    # smoothing data to neighboring voxels with zero value. Algorithm described in MNE-manual-2.7, page 208/356.
    for p in range(smooth):
        print 'Smoothing step ' + str(p + 1) + '/' + str(smooth)
        S = np.zeros([num_voxels, num_voxels])
        for j in range(num_voxels):
            my_neighbors = nbr[j, :] - 1
            # remove entries that are -1
            my_neighbors = np.delete(my_neighbors, np.nonzero(my_neighbors == -1))
            # number of immediate neighbors with non zero values
            Nj = np.sum(data[my_neighbors] != 0)
            if Nj > 0:
                pdb.set_trace()
                S[j, my_neighbors] = 1 / float(Nj)
        data = np.dot(S, data)

    pdb.set_trace()
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

    fig = mlab.gcf()
    # fig.on_mouse_pick(picker_callback)
    mlab.colorbar()

    return surf


def populate_matrix(X, num_vertex, idx):
    ''' X is a matrix of vertices x components, num_vertex is the total number of vertices that final matrix should have, and idx is a vector that maps the vertices in X to the positions in the final matrix. Returns a matrix of size num_vertex by X.shape[1], which is created using the elements from X that are placed in the positions in the new matrix guided by the vector idx. the rest of the matrix is filled with zeros.'''

    if len(idx) != X.shape[0]:
        print 'Error: there should be one index per row of X!'
        return

    X2 = np.zeros([num_vertex, X.shape[1]])

    X2[idx, :] = X
    return X2
