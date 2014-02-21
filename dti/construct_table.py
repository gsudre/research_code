'''Creates table of tracts and how many good results we have in that tract, including the MNI position and p-value in original result. 

Gustavo Sudre, 02/2014 '''

import nibabel as nib
import numpy as np
import os

# these are changed often
modes = ['TR', 'AD', 'RD']
nums = ['95', '99', '995', '999']
comparison = '2'
stat = 'nvVSper'
clusters = ['vox','tfce']

# these will likely not change
data_thresh = .5  # data threshold, >= 
skel_thresh = .5  # skeleton threshold, >=
data_dir = '/Users/sudregp/data/results/tbss/'
mean_file = '%s/mean_FA.nii.gz' % data_dir
trans_file = '%s/FMRIB582mean.mat' % data_dir
skel_file = '%s/mean_FA_skeleton_mask+FMRIB58.nii.gz' % data_dir


def get_voxel_stats(data, voxels, res_file, orig_data):
    # figure out the mean X, Y, Z (in voxel space) among all voxels that share the maximum voxel value
    mymax = np.max(data[voxels]) 
    pos = np.nonzero(data==mymax)
    pos = [pos[0][0], pos[1][0], pos[2][0]]
    # converting voxel space to mm
    mm = os.popen('echo %d %d %d | img2stdcoord -img %s -std %s -' % 
                  (pos[0], pos[1], pos[2], res_file, res_file)).read()
    mm = mm.rstrip().split('  ')
    peak_mni = [int(p) for p in mm]
    # figure out the maximum value in subject space
    vox = os.popen('echo %d %d %d | img2imgcoord -src %s -dest %s -xfm %s -' % 
                  (pos[0], pos[1], pos[2], res_file, mean_file, trans_file)).read()
    vox = vox.rstrip().split('\n')[1].split('  ')
    vox = [int(round(float(p))) for p in vox]
    peak_p = '%.1e'%(1 - orig_data[vox[0], vox[1], vox[2]])
    return peak_mni, peak_p


def get_row(data, voxels, orig_data):
    total_voxels = np.sum(voxels)
    num_good_voxels = np.sum(np.multiply(voxels, data>=data_thresh))
    # if there's a voxel in the label, let's report some stuff
    if num_good_voxels > 0:
        mni, p = get_voxel_stats(data, voxels, res_file, orig_data)
    else:
        p = '-'
        mni = '-'
    return total_voxels, num_good_voxels, mni, p


def get_image_stats(label_file, desc_file, res_file):
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
    num_tracts = len(tract_names)

    # read in results file
    img = nib.load(res_file)
    data = img.get_data()

    img = nib.load(orig_res_file)
    orig_data = img.get_data()

    # for each tract, figure out how many labels in the tract are significant
    total_voxels = []
    good_voxels = []
    peak_mni = []
    peak_p = []
    for i in range(num_tracts):
        label_voxels = np.multiply(labels==i, skel>=skel_thresh)
        total, good, mni, p = get_row(data, label_voxels, orig_data)
        total_voxels.append(total)
        good_voxels.append(good)
        peak_mni.append(mni)
        peak_p.append(p)
    # end with whole brain stats
    tract_names.append('Whole FA skeleton')
    label_voxels = skel>=skel_thresh
    total, good, mni, p = get_row(data, label_voxels, orig_data)
    total_voxels.append(total)
    good_voxels.append(good)
    peak_mni.append(mni)
    peak_p.append(p)
    return tract_names, total_voxels, good_voxels, peak_mni, peak_p


def write_rows(fid, rows):
    num_tracts = len(rows[0])
    for i in range(num_tracts):
        fid.write('\t'.join([rows[0][i], 
                       '%d / %d (%.2f%%)'%(rows[2][i], rows[1][i],
                                           100.*rows[2][i]/rows[1][i]),
                       str(rows[3][i]), rows[4][i]]))
        fid.write('\n')


for mode in modes:
    for num in nums:
        for cluster in clusters:
            # we are only interested in the corrected version of TFCE
            if cluster=='tfce':
                mc = ['corr']
            else:
                mc = ['corr', '']
            for correct in mc:
                print '=== Working on', mode, num, cluster, correct, '==='
                res_file = '%s/%s_%s_%s_%s_%sp+FMRIB58.nii.gz' % (data_dir, 
                                                                  stat, 
                                                                  mode, num,
                                                                  cluster, correct)
                orig_res_file = '%s/tbss_10K_%s_%s_%s_%sp_tstat%s.nii.gz' % (data_dir, stat, mode, cluster, correct, comparison)
                out_file = '%s/tract_stats_%s_%s_%s_%s_%sp.txt' % (data_dir, stat, mode, num, cluster, correct)

                if os.path.exists(res_file):
                    fid = open(out_file, 'w')
                    fid.write('TRACT\tVOXELS_SIG_DIFFERENT\tMNI_coordinates_of_peak_value\tP-value at peak\n')
                    # start with the 20 (compact) tracts
                    rows = get_image_stats('/Applications/fsl/data/atlases/JHU/JHU-ICBM-tracts-maxprob-thr25-1mm.nii.gz',
                                           '/Applications/fsl/data/atlases/JHU-tracts-withUnclassified.xml',
                                           res_file)
                    write_rows(fid, rows)
                    # then go for the 48 tracts
                    fid.write('\n\n\n')
                    rows = get_image_stats('/Applications/fsl/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz',
                                           '/Applications/fsl/data/atlases/JHU-labels.xml',
                                           res_file)
                    write_rows(fid, rows)
                    fid.close()
                else:
                    print 'File', res_file, 'does not exist.'