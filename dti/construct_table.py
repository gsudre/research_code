'''Creates table of tracts and how many good results we have in that tract, including the MNI position and p-value in original result. 

Gustavo Sudre, 02/2014 '''

import nibabel as nib
import numpy as np
import os

modes = ['FA', 'TR', 'AD', 'RD']
nums = ['95', '99', '995', '999']
comparison = '2'
stat = 'nvVSper'
compact = 0  # 0 for 48 labels, 1 for 20 labels
data_dir = '/Users/sudregp/data/results/tbss/'

for mode in modes:
    for num in nums:
        print '=== Working on', mode, num, '==='
        res_file = '%s/%s_%s_%s+FMRIB58.nii.gz' % (data_dir, stat, mode, num)
        orig_res_file = '%s/tbss_10K_%s_%s_tfce_corrp_tstat%s.nii.gz' % (data_dir, stat, mode, comparison)

        if compact:
            out_file = '%s/tract_stats_%s_%s_%s_compact.txt' % (data_dir, stat, mode, num)
            label_file = '/Applications/fsl/data/atlases/JHU/JHU-ICBM-tracts-maxprob-thr25-1mm.nii.gz'
            desc_file = '/Applications/fsl/data/atlases/JHU-tracts-withUnclassified.xml'
        else:
            out_file = '%s/tract_stats_%s_%s_%s.txt' % (data_dir, stat, mode, num)
            label_file = '/Applications/fsl/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz'
            desc_file = '/Applications/fsl/data/atlases/JHU-labels.xml'

        mean_file = '%s/mean_FA.nii.gz' % data_dir
        trans_file = '%s/FMRIB582mean.mat' % data_dir
        thresh = 0.1  # data threshold, >= 
        skel_file = '%s/mean_FA_skeleton_mask+FMRIB58.nii.gz' % data_dir

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
        hdr = img.get_header()

        img = nib.load(orig_res_file)
        orig_data = img.get_data()

        # for each tract, figure out how many labels in the tract are significant
        total_voxels = []
        good_voxels = []
        peak_mni = []
        peak_p = []
        tmp = []
        for i in range(num_tracts):
            label_voxels = np.multiply(labels==i, skel>0)
            total_voxels.append(np.sum(label_voxels))
            good_label_voxels = np.multiply(label_voxels, data>=thresh)
            good_voxels.append(np.sum(good_label_voxels))

            # if there's a voxel in the label, let's report some stuff
            if good_voxels[-1] > 0:
                # figure out the mean X, Y, Z (in voxel space) among all voxels that share the maximum voxel value
                mymax = np.max(data[good_label_voxels]) 
                pos = np.nonzero(data==mymax)
                if len(pos[0])>1:
                    print 'More than one MAX in', tract_names[i]
                pos = [pos[0][0], pos[1][0], pos[2][0]]
                tmp.append(pos)
                # converting voxel space to mm
                mm = os.popen('echo %d %d %d | img2stdcoord -img %s -std %s -' % 
                              (pos[0], pos[1], pos[2], res_file, res_file)).read()
                mm = mm.rstrip().split('  ')
                peak_mni.append([int(p) for p in mm])
                # figure out the maximum value in subject space
                vox = os.popen('echo %d %d %d | img2imgcoord -src %s -dest %s -xfm %s -' % 
                              (pos[0], pos[1], pos[2], res_file, mean_file, trans_file)).read()
                vox = vox.rstrip().split('\n')[1].split('  ')
                vox = [int(round(float(p))) for p in vox]
                peak_p.append('%.1e'%(1 - orig_data[vox[0], vox[1], vox[2]]))
            else:
                peak_mni.append('-')
                peak_p.append('-')
                tmp.append('-')

        fid = open(out_file, 'w')
        fid.write('TRACT\tVOXELS_SIG_DIFFERENT\tMNI_coordinates_of_peak_value\tP-value at peak\n')
        for i in range(num_tracts):
            fid.write('\t'.join([tract_names[i], 
                               '%d / %d (%.2f%%)'%(good_voxels[i], total_voxels[i],
                                                   100.*good_voxels[i]/total_voxels[i]),
                               str(peak_mni[i]), peak_p[i]]))
            fid.write('\n')
        fid.close()