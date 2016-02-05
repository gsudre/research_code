# exports the time series of a ROI to a CSV file

import mne
from mne.time_frequency import compute_epochs_csd
from mne.beamformer import dics_source_power
import os
import sys
import numpy as np
home = os.path.expanduser('~')


if len(sys.argv) > 1:
    band = [int(i) for i in sys.argv[1].split('-')]
    roi = sys.argv[2]
    cond = sys.argv[3]
else:
    band = [1, 4]  # [1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]
    roi = '/mnt/shaw/MR_behavioral/stop_task_analysis/gPPI/right_sma_stop_mask+tlrc.'
    cond = 'STG-correct'  # 'STG-correct', 'STI-correct', 'STI-incorrect']  # , 'STB', 'STG-incorrect', 'STI-incorrect']

out_dir = home + '/data/meg/stop/results/'
subjs_fname = home + '/data/meg/meg_subject_list.txt'

##### end of variables #####

btmin = -.5
btmax = -.0001
tmin = .500
tmax = 1
min_dist = 5  # only pick sources within these mm

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# prepare the fsaverage subject if we're dealing with AFNI mask
if roi.find('+tlrc') > 0:
    mask_fname = '/lscratch/' + os.environ['SLURM_JOBID'] + '/mask.txt'
    os.system('3dmaskdump -xyz -o ' + mask_fname + ' ' + roi)
    a = np.genfromtxt(mask_fname)
    os.system('rm ' + mask_fname)
    gv = a[a[:, 6] > 0, 3:6]  # separate good voxels in the mask
    # change AFNI results from RAI to LPI
    gv[:, 0] = gv[:, 0] * -1
    gv[:, 1] = gv[:, 1] * -1

    src = mne.setup_source_space(subject='fsaverage_mne', fname=None, spacing='ico5', surface='inflated', n_jobs=2)
    # get left and right coordinates for all the sources
    coord0 = mne.vertex_to_mni(vertices=src[0]['vertno'], hemis=0, subject='fsaverage_mne')
    coord1 = mne.vertex_to_mni(vertices=src[1]['vertno'], hemis=1, subject='fsaverage_mne')
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
                             tmin=0, tstep=1, subject='fsaverage_mne')
    # convert the stc to a label so we can morph it per subject later
    avg_label = mne.stc_to_label(stc, src=src, smooth=True, connected=False)
    if len(avg_label) > 2:
        raise ValueError('Found more than one label!')

data = []
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

    epochs_fname = home + '/data/meg/stop/parsed/%s_stop_parsed_matched_clean_BP1-100_DS300-epo.fif.gz' % s
    epochs = mne.read_epochs(epochs_fname, proj=True)
    fwd_fname = home + '/data/meg/stop/%s_task-5-fwd.fif' % s
    fwd = mne.read_forward_solution(fwd_fname, surf_ori=True)

    # calculate source power estimates for the whole brain
    # quick hack in tmax ot make it the same length as btmax
    data_csds = compute_epochs_csd(epochs[cond], mode='multitaper',
                                   tmin=tmin, tmax=tmax + btmax,
                                   fmin=band[0], fmax=band[1],
                                   fsum=False)
    noise_csds = compute_epochs_csd(epochs[cond], mode='multitaper',
                                    tmin=btmin, tmax=btmax,
                                    fmin=band[0], fmax=band[1],
                                    fsum=False)
    stc = dics_source_power(epochs.info, fwd, noise_csds, data_csds)
    ts = mne.extract_label_time_course(stc, label, fwd['src'])
    data.append(ts)

# export one CSV file
fname = out_dir + '%s_%s_%02dto%02d_tmin%.2f.csv' % (cond, roi_pretty, band[0],
                                                     band[1], tmin)
fid = open(fname, 'w')
fid.write('subj,power\n')
for j, d in enumerate(data):
    fid.write('%s,' % subjs[j] + ','.join(['%e' % t for t in d[0]]) + '\n')
fid.close()
