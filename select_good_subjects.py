import find_good_segments as fgs
import spreadsheet
import numpy as np

subjs = spreadsheet.get_all_subjects()

good_segs = np.zeros([len(subjs)])
for ids, s in enumerate(subjs):
    start, end, num_chans = fgs.find_good_segments(s, threshold=3500e-15)
    good_segs[ids] = end - start
