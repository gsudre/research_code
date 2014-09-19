#!/bin/sh
# Runs the rest of the compCor pipeline
# Note that all these computations need to be performed in +orig because we have to keep the aparc and binary values in masks. We convert it to TLRC in the end

subj=$1
subj_dir=/mnt/neuro/data_by_maskID/$subj/afni/${subj}.rest.compCor.results
freesurfer_dir=/mnt/neuro/freesurfer_subjects/$subj
old_pwd=`pwd`
# only go through if there is a compCor run
if [ -d $subj_dir ]; then
    cd $subj_dir
    if [ -d $freesurfer_dir ]; then
        # create the CSF mask using Freesurfer
        mri_convert ${freesurfer_dir}/mri/aparc+aseg.mgz anat_aparc+orig.nii.gz
        3dresample -inset anat_aparc+orig.nii.gz -prefix anat_aparc.resample+orig -master pb03.${subj}.r01.volreg+orig -rmode NN 
        # extract ventricles mask
        3dcalc -a anat_aparc.resample+orig -expr 'equals(a,4)+equals(a,43)' -prefix mask_ventricles
        # extract caudate, accumbens, and thalamic mask and dilate it
        3dcalc -a anat_aparc.resample+orig -expr 'equals(a,10)+equals(a,11)+equals(a,26)+equals(a,49)+equals(a,50)+equals(a,58)' -prefix mask_nonventricles 
        3dcalc -a mask_nonventricles+orig -b a+i -c a-i -d a+j -e a-j -f a+k -g a-k -expr 'amongst(1,a,b,c,d,e,f,g)' -prefix mask_nonventricles.dilated
        # make sure there is no GM in CSF mask
        3dcalc -a mask_ventricles+orig -b mask_nonventricles.dilated+orig -expr 'a-step(a*b)' -prefix mask_ventricles.eroded  

        # compute 3 PCs from nuisance mask (CSF+WM) and create regressor
        3dcalc -a mask_WMe_resam+orig -b mask_ventricles.eroded+orig -expr 'or(a,b)' -prefix mask_nuisance
        # select out censored TRs
        keep_trs=`1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded`
        # detrend the signal prior to blurring, only using the good TRs
        3dDetrend -prefix pb03.${subj}.r01.volreg.detrend -polort 3 pb03.${subj}.r01.volreg+orig"[$keep_trs]"
        # calculate the first 3 PCs
        3dpc -pcsave 3 -mask mask_nuisance+orig -prefix ${subj}.nuisancePC pb03.${subj}.r01.volreg.detrend+orig

        # get mean CSF signal regressor
        3dmaskave -q -mask mask_ventricles.eroded+orig pb03.${subj}.r01.volreg+orig"[$keep_trs]" > mean_CSF.1D
        # get mean WM signal regressor (using 3dSeg mask)
        3dmaskave -q -mask mask_WMe_resam+orig pb03.${subj}.r01.volreg+orig"[$keep_trs]" > mean_WM.1D

        # regress out old X matrix (includes motion parameters), plus PCs, WM, and CSF
        3dTproject -polort 0 -input all_runs.$subj+orig"[$keep_trs]" -ort X.xmat.1D -ort ${subj}.nuisancePC_vec.1D -ort mean_WM.1D -ort mean_CSF.1D -prefix errts.${subj}.compCor
        # Take final result to TLRC space
        cat_matvec -ONELINE mprage_ns+tlrc::WARP_DATA -I mprage_al_junk_mat.aff12.1D -I mat.r01.vr.aff12.1D > mat.epi2tlrc.1D
        3dAllineate -base mprage_ns+tlrc -input errts.${subj}.compCor+orig -1Dmatrix_apply mat.epi2tlrc.1D -mast_dxyz 2.5 -prefix errts.${subj}.compCor
    else
        echo $subj has no Freesurfer run
    fi    
else
    echo $subj has no compCor directory
fi
cd $old_pwd
