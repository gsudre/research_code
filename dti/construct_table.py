import nibabel as nib
import numpy as np


thresh = .95  # >=
# results have to be in MNI space, same dimensions, 1-p! Also need to make sure it's filled to the FA tract, and not just the skeleton!
res_file = '/Users/sudregp/data/results/tbss/res.nii.gz'
skel_file = '/Applications/fsl/data/standard/FMRIB58_FA-skeleton_1mm.nii.gz'
label_file = '/Applications/fsl/data/atlases/JHU/JHU-ICBM-tracts-maxprob-thr25-1mm.nii.gz'
desc_file = '/Applications/fsl/data/atlases/JHU-tracts.xml'

# open image and skeleton
img = nib.load(label_file)
labels = img.get_data()
img = nib.load(skel_file)
skel = img.get_data()

# read in the names of each labels
fid = open(desc_file, 'r')
tract_names= []
for line in fid:
    # we assume the labels are written in the same increasing order
    if line.find('<label') == 0:
        tract_names.append(line.split('>')[1].split('<')[0])
fid.close()

# read in results file
img = nib.load(res_file)
data = img.get_data()
hdr = img.get_header()

# for each tract, figure out how many labels in the tract are significant
total_voxels = []
good_voxels = []
peak_p = []
peak_mni = []
tmp = []
for i in range(np.max(labels)):
    label_voxels = np.multiply(labels==(i+1), skel>2000)
    total_voxels.append(np.sum(label_voxels))
    good_label_voxels = np.multiply(label_voxels, data>=thresh)
    good_voxels.append(np.sum(good_label_voxels))

    # output the p-value of the most significant voxel and its MNI coordinates
    if good_voxels[-1] > 0:
        mymax = np.max(data[good_label_voxels])
        peak_p.append(1-mymax)
        pos = np.nonzero(data==mymax)
        pos = [pos[0][0], pos[1][0], pos[2][0]]
        tmp.append(pos)
        peak_mni.append([hdr.get_qform()[0,3] - pos[0],
                         pos[1] + hdr.get_qform()[1,3],
                         pos[2] + hdr.get_qform()[2,3]])
    else:
        peak_p.append('-')
        peak_mni.append('-')
        tmp.append('-')
