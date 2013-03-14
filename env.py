'''
Simple module to return some path variables that are computer-dependent

Gustavo Sudre, 03/2013
'''

import sys

if sys.platform.find('linux') == 0:
    data = '/data/sudregp/'
    maps = '/home/sudregp/research_code/maps/'
    results = '/data/sudregp/results/'
    tmp = '/scratch/'
else:
    data = '/Users/sudregp/'
    maps = '/Users/sudregp/research_code/maps/'
    results = '/Users/sudregp/results/'
    tmp = '/Users/sudregp/tmp/'
