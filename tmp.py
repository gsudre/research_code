subjs_fname = '/mnt/shaw/MEG_behavioral/roi_analysis/meg_subject_list.txt'
data_dir = '/mnt/shaw/MEG_data/analysis/stop/'
conds = ['STI-correct', 'STI-incorrect']
vols = ['Left_Cerebral_Cortex', 'Right_Cerebral_Cortex', 'Left_Cerebellum_Cortex', 'Right_Cerebellum_Cortex']
types = ['LCMV_base', 'LCMV_blank', 'dSPM_base', 'dSPM_blank', 'DICSepochs_1to4', 'DICSepochs_4to8', 'DICSepochs_8to13', 'DICSepochs_13to30', 'DICSepochs_30to55', 'DICSepochs_65to100', 'DICSevoked_1to4', 'DICSevoked_8to13', 'DICSevoked_13to30', 'DICSevoked_30to55', 'DICSevoked_4to8', 'DICSevoked_65to100']
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

os.system('rm ~/tmp/?.nii ~/tmp/all.nii')
for s in subjs[34:]:
    fwds = [mne.read_forward_solution('%s/%s_task_%s_vol-5-fwd.fif' % (data_dir, s, vol)) for vol in vols]
    for c in conds:
        for t in types:
            for v, vol in enumerate(vols):
                stc = mne.read_source_estimate('%s/source_volumes/%s_%s_%s_%s-vl.stc' % (data_dir, s, c, vol, t))
                stc.save_as_volume('/home/sudregp/tmp/%d.nii' % v, fwds[v]['src'])
            os.system('3dcalc -a ~/tmp/1.nii -b ~/tmp/2.nii -c ~/tmp/3.nii -d ~/tmp/0.nii -prefix ~/tmp/all.nii -expr \'a+b+c+d\'')
            os.system('3drefit -space ORIG -view orig ~/tmp/all.nii')
            os.system('mv ~/tmp/all.nii %s/source_volumes/%s_%s_%s.nii' % (data_dir, s, c, t))
            os.system('rm ~/tmp/?.nii')
