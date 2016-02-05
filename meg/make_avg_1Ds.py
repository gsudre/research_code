# Script to make 1D files of averaged ROI activation
# by Gustavo Sudre, November 2014
import numpy as np
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)

data_dir = home + '/data/meg/sam_narrow_5mm/'
bands = [[1, 4]]#, [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
net = 5
net_dir = home + '/data/results/meg_Yeo/net%d'%net

fid = open(net_dir+'/regionsIn%d_15pct.1D'%net, 'r')
rois = [line.rstrip() for line in fid]
fid.close()

for band in bands:
    print 'Loading data...', band
    # ds_data = np.load(data_dir + '/downsampled_evelopes_%d-%d.npy'%(band[0],band[1]))[()]
    vox_pos = np.genfromtxt(data_dir + 'brainTargetsInTLR.txt', skip_header=1)

    for r in rois:
        vox_roi = np.genfromtxt(net_dir + '/voxels_%sin%s.txt'%(r,net))[:,3:]
        good_voxels = np.nonzero(vox_roi[:,-1]==1)[0]
        # for each good voxel (voxel inside the roi), we find the closest (likely the same) voxel in the MEG voxels
        meg_voxels = []
        for gv in good_voxels:
            seed = vox_roi[gv, :]
            dist = np.sqrt((vox_pos[:,0] - seed[0])**2 + (vox_pos[:,1] - seed[1])**2 + (vox_pos[:,2] - seed[2])**2)
            seed_src = np.argmin(dist)
            # print 'Seed src: %d, Distance to seed: %.2fmm'%(seed_src, np.min(dist))
            meg_voxels.append(seed_src)

        # output position of centroid
        vox_centroid = np.nanmean(vox_pos[np.array(meg_voxels),:], axis=0)
        dist = np.sqrt((vox_pos[:,0] - vox_centroid[0])**2 + (vox_pos[:,1] - vox_centroid[1])**2 + (vox_pos[:,2] - vox_centroid[2])**2)
        seed_src = np.argmin(dist)
        print 'Region %s: closest voxel to centroid = %.2f %.2f %.2f'%(r,vox_pos[seed_src,0],vox_pos[seed_src,1],vox_pos[seed_src,2])

        # # for each subject, average activity in those voxels and write the 1D file 
        # print 'Writing 1D for all subjects...'
        # for subj, data in ds_data.iteritems():
        #     mean_data = np.nanmean(data[np.array(meg_voxels),:], axis=0)
        #     fname = net_dir + '/%s_%sin%s_%d-%d.1D'%(subj,r,net,band[0],band[1])
        #     fid = open(fname, 'w')
        #     for d in mean_data:
        #         fid.write('%.4f\n'%d)
        #     fid.close()
