'''
Simple module to return some path variables that are computer-dependent

Gustavo Sudre, 03/2013
'''


def load(file):
    import numpy
    fid = numpy.load(file)
    res = {}
    for key, val in fid.iteritems():
        res[key] = val[()]
    return res

import sys

if sys.platform.find('linux') == 0:
    data = '/data/sudregp/'
    maps = '/home/sudregp/research_code/maps/'
    results = '/data/sudregp/results/'
    tmp = '/data/sudregp/tmp/'
else:
    data = '/Volumes/neuro/'
    maps = '/Users/sudregp/research_code/maps/'
    results = '/Users/sudregp/results/'
    tmp = '/Users/sudregp/tmp/'
