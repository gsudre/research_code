#!/bin/bash
#
# Wrapper to run MRIQC locally

# set up directory structure
mkdir /lscratch/${SLURM_JOBID}/BIDS
mkdir /lscratch/${SLURM_JOBID}/mriqc_output
mkdir /lscratch/${SLURM_JOBID}/mriqc_work

# copy the files we'll need
cp -r /scratch/sudregp/BIDS/*json /scratch/sudregp/BIDS/$1 /lscratch/${SLURM_JOBID}/BIDS/
cp -r /data/sudregp/singularity /lscratch/${SLURM_JOBID}/

module load singularity
export SINGULARITY_CACHEDIR=/lscratch/${SLURM_JOBID}/singularity/;
singularity exec -B /lscratch/${SLURM_JOBID}:/mnt docker://poldracklab/mriqc:latest mriqc /mnt/BIDS /mnt/mriqc_output participant --no-sub -w /mnt/mriqc_work -m T1w --participant_label $1

# collecting results
cp -r /lscratch/${SLURM_JOBID}/mriqc_output/* /scratch/sudregp/mriqc_output/
