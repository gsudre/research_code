# Script to convert the DICOMs obtained in our protocol, which need the gradient
# files, to NIFTI format that can be understood by FSL.
#
# Usage: bash convert_ncr_to_nii.sh /path/to/maskid
#
# script expects mr_dirs and gradient file inside /path/to/maskid

module load TORTOISE
module load afni

if [ ! -d $1 ]; then
    echo Could not find directory $1;
    exit 1;
else
    cd $1;
    # quick hack that if there are two cdi files we should use the last one
    gradient_file=`/bin/ls -1 | /bin/grep cdi | tail -1`;
    echo Using $gradient_file for gradients!
    /bin/ls -1 | /bin/grep -v cdi | grep -v txt > mr_dirs.txt;
    echo Found these MR folders:
    cat mr_dirs.txt
    # remove first line and split into different sequences
    PWD=`pwd`;
    maskid=`basename $PWD`;
    if [ $maskid -gt 2053 ]; then
        # the new sequence has only 2 mr folders, but still 60 volumes for kids and 80 for adults!
	if [ -e cdiflist08 ]; then	
        	tail -n +2 $gradient_file | split -l 30 -a 1 -d - grads;
	else
        	tail -n +2 $gradient_file | split -l 40 -a 1 -d - grads;
	fi
    else
	# the old sequence still has 20 volumes per mr folder
        	tail -n +2 $gradient_file | split -l 20 -a 1 -d - grads;
    fi

    # The idea behind doing it per session comes from an email from Irfan, who said
    # that TORTOISE v2 used directory structure, but ImportDICOM (and dcm2nixx) use
    # the DICOM series number written in the header. Somehow the scanner is writing
    # the series number wrong, and then the DICOMs get imported incorrectly. If we do
    # it by scan, like TORTOISE v2 used to do, and provide the correct gradients, it
    # should work fine.
    cnt=0
    nii='-innii'
    bval='-inbval'
    bvec='-inbvec'
    for mr_dir in `cat mr_dirs.txt`; do
        ImportDICOM -i $mr_dir -o s${cnt} -b 1100 -g grads${cnt};
        TORTOISEBmatrixToFSLBVecs s${cnt}_proc/s${cnt}.bmtxt;
        nii=$nii' 's${cnt}_proc/s${cnt}.nii
        bval=$bval' 's${cnt}_proc/s${cnt}.bvals
        bvec=$bvec' 's${cnt}_proc/s${cnt}.bvecs
        let cnt=${cnt}+1;
    done
    fat_proc_convert_dcm_dwis $nii $bval $bvec -prefix dwi_comb -flip_x -no_qc_view
fi
