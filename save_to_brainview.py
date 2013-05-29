''' Function that takes a matrix of vertices rows by datasets columns, and writes it to a file to be open by brain-view2. '''
import numpy as np


def write_bv(X, filename):

    # start by composing the headers
    header = '<header>\n<matrix>\n</matrix>\n</header>\n'

    # for every variable (columns), add a header called var#
    for v in range(X.shape[1]):
        header = header + 'var' + str(v + 1) + ' '

    # write the matrix with the headr from above
    np.savetxt(filename, X, delimiter=" ", header=header, comments='')
