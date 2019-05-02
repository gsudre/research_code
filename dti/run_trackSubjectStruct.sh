# Wrapper to run trackSubjectStruct all in /lscratch after CIT's freakout on the
# usage of fsl_sub.
# Usage: bash ~/research_code/dti/run_trackSubjectStruct maskid

scan=$1

dataDir=/data/NCR_SBRB/dti_fdt
execPath=/data/NCR_SBRB/software/autoPtx
structures=$execPath/structureList
track=$execPath/trackSubjectStruct

# copy all data we'll need first
cd /lscratch/${SLURM_JOBID}/
mkdir preproc;
cp -r $dataDir/preproc/${scan}* preproc/;

while read structstring; do
    struct=`echo $structstring | awk '{print $1}'`
    nseed=`echo $structstring | awk '{print $2}'`
#    echo $struct;
    $track $scan $struct $nseed 2>&1 > /dev/null &
done < $structures

# wait until all jobs are done
wait

# copy all results back
if [ ! -d $dataDir/tracts ]; then
    mkdir $dataDir/tracts;
fi
cp -r tracts/${scan} $dataDir/tracts/;
