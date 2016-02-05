# generates volume forward solutions forcortex and cerebellum
import mne
import sys


if len(sys.argv) > 1:
    subj = sys.argv[1]
else:
    subj = 'ABUTRIKQ'

freesurfer_dir = '/mnt/shaw/MEG_structural/freesurfer/%s/' % subj
data_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed_red/'
fwd_dir = '/mnt/shaw/MEG_data/analysis/stop/'
evoked_fname = data_dir + '%s_stop_parsed_matched_BP1-100_DS300-ave.fif' % subj

src1 = mne.setup_volume_source_space(subj,
                                     mri=freesurfer_dir + '/mri/aseg.mgz',
                                     volume_label='Left-Cerebral-Cortex',
                                     bem=freesurfer_dir +
                                     '/bem/%s-5120-bem.fif' % subj)
src2 = mne.setup_volume_source_space(subj,
                                     mri=freesurfer_dir + '/mri/aseg.mgz',
                                     volume_label='Right-Cerebral-Cortex',
                                     bem=freesurfer_dir +
                                     '/bem/%s-5120-bem.fif' % subj)
src3 = mne.setup_volume_source_space(subj,
                                     mri=freesurfer_dir + '/mri/aseg.mgz',
                                     volume_label='Left-Cerebellum-Cortex',
                                     bem=freesurfer_dir +
                                     '/bem/%s-5120-bem.fif' % subj)
src4 = mne.setup_volume_source_space(subj,
                                     mri=freesurfer_dir + '/mri/aseg.mgz',
                                     volume_label='Right-Cerebellum-Cortex',
                                     bem=freesurfer_dir +
                                     '/bem/%s-5120-bem.fif' % subj)

srcs = src1 + src2 + src3 + src4

evoked = mne.read_evokeds(evoked_fname)
fwd_fname = '%s/%s_task-vol-5-fwd.fif' % (fwd_dir, subj)
trans_fname = '%s/%s-trans.fif' % (fwd_dir, subj)
fwd = mne.make_forward_solution(evoked[0].info, trans_fname, srcs,
                                freesurfer_dir +
                                '/bem/%s-5120-bem-sol.fif' % subj,
                                fname=fwd_fname, meg=True, eeg=False, n_jobs=1)
