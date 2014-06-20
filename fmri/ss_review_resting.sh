#!/bin/tcsh

# This script is a shortened version of the standard @ss_review_drive,
# but adapted to look at resting data.

cd /mnt/neuro/data_by_maskID/${1}/afni/${1}.rest.withPhysio.results/

# ------------------------------------------------------------
# try to avoid any oblique warnings throughout script
setenv AFNI_NO_OBLIQUE_WARNING YES

# ------------------------------------------------------------
# if the expected "basic" script is here, run it

# if ( -f @ss_review_basic ) then
#    echo ------------------- @ss_review_basic --------------------
#    tcsh -ef @ss_review_basic
#    echo ---------------------------------------------------------

#    prompt_user -pause "                      \
#       review output from @ss_review_basic    \
#       (in terminal window) for anything that \
#       looks unreasonable                     \
#                                              \
#       --- click OK when finished ---         \
#       "
#    echo ""
# else
#    echo ""
#    echo "*** missing @ss_review_basic script ***"
#    echo ""
# endif

# ------------------------------------------------------------
# possibly consider running the @epi_review script here


echo ------------------- outliers and motion --------------------

1dplot -one -censor_RGB green -censor censor_${1}_combined_2.1D  \
       outcount_rall.1D "1D: 123@0.1" &
1dplot -one -censor_RGB green -censor censor_${1}_combined_2.1D  \
       motion_${1}_enorm.1D "1D: 123@0.2" &


echo ----------------- anat/EPI alignment check -----------------

# start afni with anat and volreg datasets only
afni anat_final.${1}+tlrc.HEAD pb03.${1}.r01.volreg+tlrc.HEAD &


echo -------------------- regession warnings --------------------

# if 3dDeconvolve made an error/warnings file, show it
if ( -f 3dDeconvolve.err ) then
   echo ------------- 3dDeconvolve.err -------------
   cat 3dDeconvolve.err
   echo --------------------------------------------
else
   echo --- no 3dDeconvolve.err warnings file ---   
endif

echo ""

# show any timing_tool.py warnings about TENTs        
if ( -f out.TENT_warn.txt ) then
   echo ------------ out.TENT_warn.txt -------------
   cat out.TENT_warn.txt
   echo --------------------------------------------
else
   echo --- no out.TENT_warn.txt warnings file ---  
endif

echo ""

# show any pairwise correlation warnings from X-matrix
echo ----------- correlation warnings -----------
1d_tool.py -show_cormat_warnings -infile X.xmat.1D
echo --------------------------------------------

# if there are any pre-steady state warnings, show them
if ( -f out.pre_ss_warn.txt && ! -z out.pre_ss_warn.txt ) then
   echo --------- pre-steady state warnings --------
   cat out.pre_ss_warn.txt
   echo --------------------------------------------
endif

