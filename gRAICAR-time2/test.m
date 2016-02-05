% % diary('/home/sudregp/data/rsfmri/graicar.log')
% addpath(genpath('~/research_code/gRAICAR-time/'))
% settings.outdir     = '~/tmp/melodic/output';
% settings.subjlist   = '~/tmp/melodic/subjs.list';
% settings.taskname   = 'rsFMRI';
% settings.ncores     = 1;
% settings.maskpath     = '~/tmp/melodic/mask_group_big.nii';
% settings.useRAICAR  = 1;
% settings.savemovie  = 1;
% settings.webreport  = 1;
% settings.displayThreshold = 1.5000;
% settings.compPerPage= 10;
% settings.icapath   = '~/tmp/melodic/AKMNQNHX/melodic_IC.nii.gz';
% settings.fmripath   = '~/tmp/melodic/AKMNQNmelodic_IC.nii.gz';
% settings.workdir = '~/tmp/melodic';
% gRAICAR_run(settings,1)
% % diary('off')

addpath(genpath('~/research_code/gRAICAR-time2/'))
settings.outdir     = '~/tmp/graicar_time_tests/output';
settings.subjlist   = '~/tmp/graicar_time_tests/subjs.list';
settings.taskname   = 'rsFMRI';
settings.ncores     = 1;
settings.maskpath     = '~/tmp/graicar_time_tests/brain_mask.nii';
settings.useRAICAR  = 1;
settings.savemovie  = 1;
settings.webreport  = 1;
settings.displayThreshold = 1.5000;
settings.compPerPage= 10;
settings.fmripath   = '~/tmp/graicar_time_tests/AKMNQNHX/data.nii';
settings.workdir = '~/tmp/graicar_time_tests';
gRAICAR_run(settings,1)