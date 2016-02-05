# Script to create NIFTI files with MEG data for later be used in MELODIC and gRAICAR
# by Gustavo Sudre, April 2015
import numpy as np
import mne
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg
from scipy import stats

def write2afni(vals, fname):
    template_dir = home+'/data/meg/sam_narrow_5mm/'
    data = np.genfromtxt(template_dir + '/voxelsInBrain.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data = np.hstack([data[:, :3], vals[:,np.newaxis]])
    np.savetxt(fname, data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat '+fname+ ' | 3dUndump -master '+template_dir+'/TT_N27_555+tlrc -ijk -datum float -prefix '+fname+' -overwrite -')


def export_afni_maps(maps, fname):
    nmaps = maps.shape[1]
    tmp_fname = '/tmp/tmp'
    cat_str = '' 
    for i in range(nmaps):
        write2afni(maps[:,i], tmp_fname+'_'+str(i))
        cat_str += tmp_fname+'_'+str(i)+'+tlrc '
    os.system('3dTcat -overwrite -prefix '+fname+' '+cat_str)


band = [13, 30]  #[[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
window_length=13.65  #s
fifs_dir = home + '/data/meg/rest/' #'/mnt/neuro/MEG_data/fifs/rest/'
sam_dir = home + '/data/meg/sam_narrow_5mm/'
out_dir = home + '/tmp/melodic/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()    
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]  

for s in subjs[:10]:
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif'%s
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=band[0],h_freq=band[1],picks=picks)
    weights = np.load(sam_dir + s + '_%d-%d_weights.npz'%(band[0],band[1]))['weights']
    data, time = raw[picks, :]
    # instead of getting the hilbert of the source space (costly), do the Hilbert first and compute the envelope later
    raw.apply_hilbert(picks, envelope=False)
    events = fg.get_good_events(markers[s], time, window_length)
    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    # it will go faster to concatenate everything now, downsample it, and then multiply the weights
    epoch_data = epochs.get_data()
    epoch_data = epoch_data.swapaxes(1,0)
    nchans, nreps, npoints = epoch_data.shape
    sensor_data = epoch_data.reshape([nchans, nreps*npoints])
    sensor_data = sensor_data[:, np.arange(0,nreps*npoints,int(raw.info['sfreq'])/2)]
    # get the abs() of Hilbert transform (Hilbert envelope)
    sol = abs(np.dot(weights, sensor_data))

    subj_data = stats.mstats.zscore(sol, axis=1)
    subj_data[np.isnan(subj_data)] = 0

    fname = out_dir + '%s_%dto%d.nii'%(s,band[0],band[1])
    export_afni_maps(subj_data, fname)
