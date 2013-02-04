#!/bin/sh
# transform Elekta MEG .fif files, from sensor space, into a set of estimated sources, using MNE
# to do this, first have to do some fancy footwork with FreeSurfer (to have a detailed 3D model of the cortical surface, based on an MRI image), and 
# 14th November, modified version of Gus's MNE_pipeline.sh 
# assumes a heap of MNE and FreeSurfer paths and variables have been set - these should be in your startup script, but see end for suggested commands

export SUBJECT=$1 # subject ID, as used in freesurfer subjects directory, e.g. /usr1/meg/structural, or /usr1/apps/freesurfer/subjects
export SPACING=$2 # distance on cortex in mm, between sources to estimate 
export MRI=$3 # 3D nifti MRI structural image
#average_file = 'average_fif' # what does this do? seems to work so far without it

# 3.3 Cortical surface reconstruction with FreeSurfer . . . . . . . . .                          20
#./make_brain_surface.sh $SUBJECT $MRI
# recon-all -i $MRI -subjid $SUBJECT | tee "$SUBJECT"_surface.log
recon-all -i $MRI -subjid $SUBJECT -all | tee -a "$SUBJECT"_surface.log

# 3.4 Setting up the anatomical MR images for MRIlab . . . . . . . .                             20
mne_setup_mri

# 3.5 Setting up the source space . . . . . . . . . . . . . . . . . . . . . . . . .              21
# 3.6 Creating the BEM model meshes . . . . . . . . . . . . . . . . . . . . .                    24
#     Setting up the triangulation files . . . . . . . . . . . . . . . . . . . . . . . .         24
# 3.7 Setting up the boundary-element model . . . . . . . . . . . . . . .                        25
#./make_mne_model.sh $SUBJECT $SPACING
mne_setup_source_space --subject $SUBJECT --spacing $SPACING | tee "$SUBJECT"_mne_model.log

# creates the boundary-element model using the Wtershed algorithm
# results are file C-head.fif  and directory watershed. after the linking commands below, we'll also have
# inner_skull.surf  outer_skin.surf  outer_skull.surf
mne_watershed_bem --subject $SUBJECT --atlas | tee -a "$SUBJECT"_mne_model.log
cd  $SUBJECTS_DIR/$SUBJECT/bem
ln -s watershed/"$SUBJECT"_inner_skull_surface inner_skull.surf
ln -s watershed/"$SUBJECT"_outer_skull_surface outer_skull.surf
ln -s watershed/"$SUBJECT"_outer_skin_surface outer_skin.surf
cd ~

# computes the geometry information for BEM
# results are files such as C-20480-bem.fif, C-20480-bem-sol.fif, inner_skull-20480.pnt, and inner_skull-20480.surf
mne_setup_forward_model --homog --subject $SUBJECT --surf --ico 4 | tee -a "$SUBJECT"_mne_model.log

# Create high-density head model for co-registration
mkheadsurf -subjid $SUBJECT -srcvol T1.mgz | tee -a "$SUBJECT"_mne_model.log
mne_surf2bem --surf $SUBJECTS_DIR/$SUBJECT/surf/lh.seghead --id 4 --check --fif $SUBJECTS_DIR/$SUBJECT/bem/"$SUBJECT"-head-dense.fif | tee -a "$SUBJECT"_mne_model.log
cd  $SUBJECTS_DIR/$SUBJECT/bem
mv "$SUBJECT"-head.fif "$SUBJECT"-head-sparse.fif
cp "$SUBJECT"-head-dense.fif "$SUBJECT"-head.fif
cd ~

# this is only if we want to be able to display the BEM model in visualizer.
# mne_analyze looks for this specific file name, so we need to be ready for it.
# However, if the BEM file already has a model for the head, it will be loaded
# instead of the one above, so probably it should not be done by default.
#cd  $SUBJECTS_DIR/$SUBJECT/bem
#ln -s $SUBJECT-*-bem.fif $SUBJECT-bem.fif
#cd ~

# after this, the forward calculation in the MNE software computes signals
# detected by each MEG sensor for three orthogonal dipoles at each source space
# location. use raw data for computations, and then average the forawrd
# solutions with mne_average_forward_solutions if necessary

# Gus's own step: create labels for pre-selected regions
mri_annotation2label --subject $SUBJECT --hemi lh --outdir $SUBJECTS_DIR/$SUBJECT/labels/
mri_annotation2label --subject $SUBJECT --hemi rh --outdir $SUBJECTS_DIR/$SUBJECT/labels/
# renaming from ?h.*.label to *-?h.label
cd $SUBJECTS_DIR/$SUBJECT/labels/
for filename in *.label
do
bar=(`echo $filename | tr '.' ' '`)
newname="${bar[1]}"-"${bar[0]}".label
mv $filename $newname
done
cd ~

# [in here there were some MEG sensor-data preprocessing steps, that I do elsewhere ]

#3.10 Aligning the coordinate frames . . . . . . . . . . . . . . . . . . . . . . .               31
#--> use mne_analyze, use first MEG raw file to get coordinates (before SSS). Look at section 12.11 in the MNE manual.

# # NECESSARY ENVIRONMENT VARIABLES
# # paths can change, of course, but right now, to work on the lobes, you need these:
# 
# # OpenGL libaries, for MNE, FreeSurfer (and Matlab, BTW)
# export LIBGL_ALWAYS_INDIRECT=1
# 
# # MNE
# export MNE_ROOT=/usr1/apps/MNE-2.7.0-3106-Linux-x86_64
# export MATLAB_ROOT=`which matlab`
# . $MNE_ROOT/bin/mne_setup_sh
# PATH=${PATH}:${MNE_ROOT}/bin

# # free surfer paths
# export FREESURFER_HOME=/usr1/apps/freesurfer
# source $FREESURFER_HOME/SetUpFreeSurfer.sh
# export SUBJECTS_DIR=/usr1/meg/structural/


