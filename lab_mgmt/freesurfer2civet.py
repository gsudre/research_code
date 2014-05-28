''' Assigns a Freesurfer label to every vertex in the CIVET cortical output '''

civet_fname = '/Users/sudregp/Documents/surfaces/IMAGING_TOOLS/cortex.mat'
labels_dir = '/Users/sudregp/data/fsaverage_labels/destrieux/'
output_dir = '/Users/sudregp/tmp/c/'

import scipy.io
mat = scipy.io.loadmat(civet_fname)

import glob
import numpy as np
for h in ['lh', 'rh']:
    coord = mat['coord_' + h]

    # open every label file and store its information, so we can avoid file IO later
    label_data = []
    label_names = []
    label_fnames = glob.glob(labels_dir + h + '*.label')
    for l in label_fnames:
        label_names.append(l.split('.')[-2])
        data = np.genfromtxt(l, skip_header=2, delimiter=' ')
        label_data.append(data[:,[2,4,6]])

    # for CIVET every point, find which label contains the closest point to it
    point_label = []
    for p in range(coord.shape[1]):
        print '%d / %d'%(p+1,coord.shape[1])
        min_dist = np.inf
        cur_label = -1
        for lidx, lname in enumerate(label_names):
            data = label_data[lidx]
            dist = np.sqrt((data[:,0] - coord[0,p])**2 + (data[:,1] - coord[1,p])**2 + (data[:,2] - coord[2,p])**2)
            closest_point = np.min(dist)
            # if the current label has a point closer to the current CIVET point, then it becomes the current label
            if closest_point < min_dist:
                min_dist = closest_point
                cur_label = lidx+1
        point_label.append(cur_label)

    # spit out the label map and a vertstats file
    fid = open(output_dir + h + '_map_ds.txt', 'w')
    for l in range(len(label_names)):
        fid.write('%d %s\n'%(l+1,label_names[l]))
    fid.close()
    fid = open(output_dir + h + '_freesurfer2civet_labels_ds.txt', 'w')
    fid.write('<header>\n</header>\nlabel\n')
    for i in point_label:
        fid.write('%d\n'%(i))
    fid.close()


