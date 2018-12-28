  # Just a wrapper to run ubeer_align in a swarm, and put the different
  # alignment options in the same folder.
  #
  # Usage: bash make_alignment_options.sh 0000 /scratch/sudregp/rsfmri
  #
  # GS, 12/2018
  
  s=$1;
  net_dir=$2;

  mkdir ${net_dir}/resting_alignment/
  cd ${net_dir}/${s}/${s}.rest.subjectSpace.results;
  uber_align_test.py -no_gui -save_script align.test  \
     -uvar anat ${s}_SurfVol_ns+orig                      \
     -uvar epi  vr_base_min_outlier+orig                     \
     -uvar epi_base 0                                 \
     -uvar anat_has_skull no                  \
     -uvar align_centers yes                          \
     -uvar giant_move yes
  ./align.test;
  cd align.results;
  for f in `ls anat*HEAD`; do
      \@snapshot_volreg $f epi+orig ${s}_${f};
      mv *jpg ${net_dir}/resting_alignment/;
  done;