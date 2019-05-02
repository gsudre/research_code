# Runs mriqc using lscratch. The only parameter is the mask id!

s=$1;
TMPDIR=/lscratch/$SLURM_JOBID; 
mkdir -p $TMPDIR/out; 
mkdir -p $TMPDIR/wrk;
mriqc /scratch/${USER}/NCR_BIDS/ $TMPDIR/out \
    participant --participant_label ${s} -w $TMPDIR/wrk;
mv $TMPDIR/out/subj-${s}* /data/${USER}/mriqc_output/

