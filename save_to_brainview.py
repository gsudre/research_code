''' Set of functions to plot results into brainview '''

import numpy as np


def write_bv(X, filename):
    ''' Function that takes a matrix of vertices rows by datasets columns, and writes it to a file to be open by brain-view2. '''
    # start by composing the headers
    header = '<header>\n<matrix>\n</matrix>\n</header>\n'

    # for every variable (columns), add a header called var
    if len(X.shape)==1:
        nvars = 1
    else:
        nvars = X.shape[1]
    for v in range(nvars):
        header = header + 'var' + str(v + 1) + ' '

    # write the matrix with the headr from above
    np.savetxt(filename, X, delimiter=" ", header=header.rstrip(), comments='', fmt='%.4f')
