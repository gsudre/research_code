#!/bin/sh
# Runs the rest of the compCor pipeline
# Note that all these computations need to be performed in +orig because we have to keep the aparc and binary values in masks. We convert it to TLRC in the end

subj=$1
# subj_dir=/mnt/shaw/data_by_maskID/$subj/afni/${subj}.rest.compCor.results
# freesurfer_dir=/mnt/shaw/freesurfer5.3_subjects/$subj
subj_dir=~/data/fmri/$subj/${subj}.rest.compCor.results
freesurfer_dir=~/data/MEG_structural/freesurfer/$subj
old_pwd=`pwd`
# only go through if there is a compCor run
if [ -d $subj_dir ]; then
    cd $subj_dir
    if [ -d $freesurfer_dir ]; then
        # convert aparc labels from Freesurfer to TLRC and resample it to EPI dimensions
        mri_convert ${freesurfer_dir}/mri/aparc+aseg.mgz aparc_aseg.nii.gz
        3dcopy aparc_aseg.nii.gz aparc_aseg+orig
        rm aparc_aseg.nii.gz
        @auto_tlrc -suffix _linear -base HaskinsPeds_NL_template1.0+tlrc -input mprage+orig
        @auto_tlrc -rmode NN -onewarp -apar mprage_linear+tlrc -input aparc_aseg+orig
        3dresample -inset aparc_aseg+tlrc -prefix aparc_aseg.resample+tlrc -master pb03.${subj}.r01.volreg+tlrc -rmode NN 

        # extract ventricles mask
        3dcalc -a aparc_aseg.resample+tlrc -expr 'equals(a,4)+equals(a,43)' -prefix mask_ventricles

        # compute 3 PCs from nuisance mask (CSF+WM) and create regressor
        3dcalc -a mask_WMe_resam+tlrc -b mask_ventricles+tlrc -expr 'or(a,b)' -prefix mask_nuisance
        # select out censored TRs
        keep_trs=`1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded`
        # detrend the signal prior to blurring, only using the good TRs
        3dDetrend -prefix pb03.${subj}.r01.volreg.detrend -polort 3 pb03.${subj}.r01.volreg+tlrc"[$keep_trs]"
        # calculate the first 3 PCs
        3dpc -pcsave 3 -mask mask_nuisance+tlrc -prefix ${subj}.nuisancePC pb03.${subj}.r01.volreg.detrend+tlrc

        # get mean CSF signal regressor
        3dmaskave -q -mask mask_ventricles+tlrc pb03.${subj}.r01.volreg.detrend+tlrc > mean_CSF.1D
        # get mean WM signal regressor (using 3dSeg mask)
        3dmaskave -q -mask mask_WMe_resam+tlrc pb03.${subj}.r01.volreg.detrend+tlrc > mean_WM.1D

        # regress out old X matrix (includes motion parameters), plus PCs, WM, and CSF
        3dTproject -polort 0 -input all_runs.$subj+tlrc"[$keep_trs]" -ort X.xmat.1D -ort ${subj}.nuisancePC_vec.1D -ort mean_WM.1D -ort mean_CSF.1D -prefix errts.${subj}.compCor

    else
        echo $subj has no Freesurfer run
    fi    
else
    echo $subj has no compCor directory
fi
cd $old_pwd
