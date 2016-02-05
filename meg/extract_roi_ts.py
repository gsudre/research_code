# exports the time series of a ROI to a CSV file

import mne
from mne.minimum_norm import apply_inverse, read_inverse_operator
import os
import numpy as np

# roi = 'fusiform-lh.label'
# roi = '/mnt/shaw/MR_behavioral/stop_task_analysis/gPPI/left_IFC_stop_mask+tlrc.' (use this if you run the script on sbrbmeg or caterpie)
roi = '/Volumes/Shaw/MR_behavioral/stop_task_analysis/gPPI/right_IFC_stop_mask+tlrc.'
roi = '/mnt/shaw/MR_behavioral/stop_task_analysis/gPPI/right_IFC_stop_mask+tlrc.'
# subjs_fname = '/mnt/shaw/MEG_behavioral/roi_analysis/meg_subject_list.txt'
subjs_fname = '/Volumes/Shaw/MEG_behavioral/roi_analysis/meg_subject_list.txt'
subjs_fname = '/mnt/shaw/MEG_behavioral/roi_analysis/meg_subject_list.txt'
conds = ['STG-correct', 'STI-correct', 'STI-incorrect']  # , 'STB', 'STG-incorrect', 'STI-incorrect']
# out_dir = '/mnt/shaw/MEG_behavioral/roi_analysis/'
out_dir = '/Volumes/Shaw/MEG_behavioral/roi_analysis/'
out_dir = '/mnt/shaw/MEG_behavioral/roi_analysis/'


##### end of variables #####
snr = 3.0
lambda2 = 1.0 / snr ** 2
method = "dSPM"  # use dSPM method (could also be MNE or sLORETA)
min_dist = 5  # only pick sources within these mm

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# prepare the fsaverage subject if we're dealing with AFNI mask
if roi.find('+tlrc') > 0:
    os.system('3dmaskdump -xyz -o mask.txt ' + roi)
    a = np.genfromtxt('mask.txt')
    os.system('rm mask.txt')
    gv = a[a[:, 6] > 0, 3:6]  # separate good voxels in the mask
    # change AFNI results from RAI to LPI
    gv[:, 0] = gv[:, 0] * -1
    gv[:, 1] = gv[:, 1] * -1

    src = mne.setup_source_space(subject='fsaverage', fname=None, spacing='ico5', surface='inflated')
    # get left and right coordinates for all the sources
    coord0 = mne.vertex_to_mni(vertices=src[0]['vertno'], hemis=0, subject='fsaverage')
    coord1 = mne.vertex_to_mni(vertices=src[1]['vertno'], hemis=1, subject='fsaverage')
    coord = np.vstack([coord0, coord1])
    # store the index of the sources within min_dist of the mask voxels
    b = []
    for i in range(gv.shape[0]):
        dist = np.sqrt((coord[:, 0] - gv[i, 0]) ** 2 + (coord[:, 1] - gv[i, 1]) ** 2 + (coord[:, 2] - gv[i, 2]) ** 2)
        if min(dist) <= min_dist:
            b.append(np.argmin(dist))
    # create a stc with 1s for the near sources
    d = np.zeros([coord.shape[0], 1])
    d[b] = 1
    stc = mne.SourceEstimate(d, vertices=[src[0]['vertno'], src[1]['vertno']],
                             tmin=0, tstep=1, subject='fsaverage')
    # convert the stc to a label so we can morph it per subject later
    avg_label = mne.stc_to_label(stc, src=src, smooth=5, connected=False)
    if len(avg_label) > 2:
        raise ValueError('Found more than one label!')

data = [[] for c in conds]
for s in subjs:
    # check if it's AFNI or freesurfer label
    if roi.find('label') > 0:
        label_dir = '/Volumes/Shaw/MEG_structural/freesurfer/%s/labels/' % s
        label = mne.read_label(label_dir + roi)
        roi_pretty = roi.split('.')[0]
    else:
        roi_pretty = roi.split('/')[-1].split('+')[0]
	# right labels are normally in the second index
	if avg_label[0] is not None:
        	label = avg_label[0].morph(subject_to=s)
	else:
        	label = avg_label[1].morph(subject_to=s)

    evoked_fname = '/Volumes/Shaw/MEG_data/analysis/stop/evoked/%s_stop_BP1-35_DS120-ave.fif' % s
    inv_fname = '/Volumes/Shaw/MEG_data/analysis/stop/%s_task-5-meg-inv.fif' % s
    inverse_operator = read_inverse_operator(inv_fname)

    for i, c in enumerate(conds):
        # calculate source estimates for the whole brain
        evoked = mne.read_evokeds(evoked_fname, condition=c)
        stc = apply_inverse(evoked, inverse_operator, lambda2, method,
                            pick_ori=None)
        ts = mne.extract_label_time_course(stc, label, inverse_operator['src'])
        data[i].append(ts)

# export one CSV file for each condition
for i, c in enumerate(conds):
    fname = out_dir + '%s_%s_%s.csv' % (c, roi_pretty, method)
    fid = open(fname, 'w')
    fid.write('time,' + ','.join(['%.3f' % t for t in evoked.times]) + '\n')
    for j, d in enumerate(data[i]):
        fid.write('%s,' % subjs[j] + ','.join(['%e' % t for t in d[0]]) + '\n')
    fid.close()
