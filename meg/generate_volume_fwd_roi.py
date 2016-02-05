# generates volume forward solutions forcortex and cerebellum
import mne
import sys


if len(sys.argv) > 1:
    subj = sys.argv[1]
    roi = sys.argv[2]
else:
    subj = 'BIPRUXZS'
    roi = 'Left-Cerebellum-Cortex'

freesurfer_dir = '/mnt/shaw/MEG_structural/freesurfer/%s/' % subj
data_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed_red/'
fwd_dir = '/mnt/shaw/MEG_data/analysis/stop/'
evoked_fname = data_dir + '%s_stop_parsed_matched_BP1-100_DS300-ave.fif' % subj

src = mne.setup_volume_source_space(subj,
                                    mri=freesurfer_dir + '/mri/aseg.mgz',
                                    volume_label=roi,
                                    bem=freesurfer_dir +
                                    '/bem/%s-5120-bem.fif' % subj)

evoked = mne.read_evokeds(evoked_fname)
fwd_fname = '%s/%s_task_%s_vol-5-fwd.fif' % (fwd_dir, subj,
                                             roi.replace('-', '_'))
trans_fname = '%s/%s-trans.fif' % (fwd_dir, subj)
fwd = mne.make_forward_solution(evoked[0].info, trans_fname, src,
                                freesurfer_dir +
                                '/bem/%s-5120-bem-sol.fif' % subj,
                                fname=fwd_fname, meg=True, eeg=False, n_jobs=1)
