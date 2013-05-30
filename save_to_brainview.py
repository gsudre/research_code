''' Set of functions to plot results into brainview '''

import numpy as np


def write_bv(X, filename):
    ''' Function that takes a matrix of vertices rows by datasets columns, and writes it to a file to be open by brain-view2. '''
    # start by composing the headers
    header = '<header>\n<matrix>\n</matrix>\n</header>\n'

    # for every variable (columns), add a header called var#
    for v in range(X.shape[1]):
        header = header + 'var' + str(v + 1) + ' '

    # write the matrix with the headr from above
    np.savetxt(filename, X, delimiter=" ", header=header.rstrip(), comments='', fmt='%.4f')


def populate_matrix(X, num_vertex, idx, default=0):
    ''' Returns a matrix of size num_vertex by X.shape[1], which is created using the elements from X that are placed in the positions in the new matrix gudied by the vector idx. default defines the starting value of the matrix. '''

    if len(idx) != X.shape[0]:
        print 'Error: there should be one index per row of X!'
        return

    X2 = np.zeros([num_vertex, X.shape[1]])
    if default != 0:
        X2[:] = default

    X2[idx, :] = X
    return X2
