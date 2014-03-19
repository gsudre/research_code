#!/bin/csh
#This script calculates CBF maps with data acquired with the PseudoContinuous ASL (PCASL) sequence using AFNI commands
#PCASL sequence for NIH Siemens scanners was develped by Yan Zhang and Lalith Talagala

#Lalith Talagala  NMRF/NINDS/NIH 01/28/2013
#02/02/2013 SLT use 3dZcutup code from Z. Saad to calc slice depenent cbf conversion factor
#03/03/2013     use slice time offsets from the BRIK file header to calc slice dep conv factor
#07/16/2013 SLT copy procPASL code to modifiy for PCASL
#		The first volume (index 0) is M0, next 4 volumes (indices 1-4) are discarded.
#		Use volume indices 5 onwards to calculate the pefusion signal
#11/05/2013 SLT save norm diff images also and create nii file of ndiff and cbf images
#12/18/2013 SLT add rejection of outlier difference images 

set version = "12182013" 		

set HELP = "procPCASL(version $version) calculates cbf maps using data from the NIH PCASL(v3 or later) sequence "
set USAGE = "USAGE:procPCASL infile.brik labdur(ms) postlabdly(ms) [redo [outlthres [clean]]]"
set EXAMPLE = "e.g. >procPCASL fred.brik 3000 1200 "

if ($#argv < 3) then
        echo "$HELP"
        echo "$USAGE"
        echo "$EXAMPLE"
        exit 1
endif


set infile = $1
if !(-e $infile) then 
	echo "-procPCASL: Exiting, cannot find" {$infile}
	exit 1
endif

#setup the current directory
if ($infile:t == $infile:h) then #if only a filename given 
    set wkdir = $PWD
else
   set wkdir = $infile:h
endif

#set logfile = '/dev/null'       #logfile
set date = `date +%Y%m%d`
set time = `date +%H%M%S`
set logfile = {$wkdir}{/logfile_}{$date}{_}{$time}
date > $logfile
echo -procPCASL: version = $version | tee -a $logfile

echo Processing $infile:t | tee -a $logfile 

set lambda = 0.90 
set alpha = 0.85 # Dai et al MRM 60:1488 (2008)
set t1a = 1.65	#blood t1 at 3T in sec Lu et al., MRM 52:679 (2004)
echo lambda = $lambda, alpha = $alpha, T1a = $t1a | tee -a $logfile

set labdur = `1deval -expr "$2/1000.0" -num 1`	#labeling duration converted to sec
set postlabdly = `1deval -expr "$3/1000.0" -num 1` 	#post labeling delay for slice 1 converted to sec
echo LabelDur = $labdur, PostLabelDly = $postlabdly | tee -a $logfile

set redo = 0
set outlthres = 0.05 #diff volumes with greater than this frac of outlier pixs will be removed
set clean  = 1 
if ($#argv == 4) then 
    set redo = $4
endif
if ($#argv == 5) then 
    set redo = $4
    set outlthres = $5
endif
if ($#argv == 6) then 
    set redo = $4
    set outlthres = $5
    set clean = $6
endif
echo Outlier detection threshold = $outlthres| tee -a $logfile

#get nvols, tr, and ns
set tnums = `3dAttribute -name TAXIS_NUMS $infile >>& $logfile; grep TAXIS_NUMS $logfile` 
set vols = $tnums[3]
set tflts = `3dAttribute -name TAXIS_FLOATS $infile >>& $logfile; grep TAXIS_FLOATS $logfile`  
set tr = $tflts[4]							#TR in sec
set dsdimens = `3dAttribute -name DATASET_DIMENSIONS $infile >>& $logfile; grep DATASET_DIMENSIONS $logfile` 
set ns = $dsdimens[5]							#num slices
#echo $vols $tr $ns
echo TR = $tr, NumVols = $vols, Nslices = $ns | tee -a $logfile

#make the ti2array and save a .1D file
#if (-e ti2array.1D) then #remove the existing one 
#	rm ti2array.1D
#endif
#set ti2inc = `1deval -expr "($tr - $ti2)/$ns" -num 1`
#1deval -expr 'a' -del $ti2inc -start $ti2 -num $ns > ti2array.1D 
#1deval -expr "$ti2" -num $ns > ti2array.1D

set slicetimes_temp = `3dAttribute -name TAXIS_OFFSETS $infile >>& $logfile; grep TAXIS_OFFSETS $logfile`
set slicetimes = ($slicetimes_temp[3-])
if ($#slicetimes == 0) then
	echo No slice acquisition times in header | tee -a $logfile
else
	echo slicetimes = $slicetimes | tee -a $logfile
endif

#setup the current directory
if ($infile:t == $infile:h) then #if only a filename given 

    set wkdir = $PWD
else
   set wkdir = $infile:h
endif
set infilename = $infile:t
#echo $wkdir 

#create outputfile prefix
set infilen = $infilename:r:s/+orig//  #remove orig from the filename part
set infilem = {$wkdir}{/}{$infilen}  #add path to modified infile name

set diffssuf = '_diffs' 		#difference image time series
set outdiffsp = {$infilem}{$diffssuf}
set ndiffsuf = '_ndiff'		#normalized avg difference images suffix
set outndiffp = {$infilem}{$ndiffsuf}
set cbfsuf = '_cbf'
set outfilep = {$infilem}{$cbfsuf}
#echo $outfilep


#if  ( (! (-e {$outfilep}{.nii})) || (! (-e {$outfilep}{+orig.BRIK})) || $redo ) then

    #remove old outputs
    rm -f {$outfilep}{.nii} {$outfilep}{+orig.*} {$outdiffsp}{+orig.*} {$outndiffp}{.nii} {$outndiffp}{+orig.*} pcasl* >>& $logfile

    # extract the first volume as M0
    3dcalc -a {$infile}{'[0]'} -expr 'a' -prefix pcaslM0images  >>& $logfile


    #Skull strip M0 image if needed
    set nskloutp = {$infilem}{_v0_nskl}
    #echo $nskloutp
    if !(-e {$nskloutp}{+orig.BRIK}) then
	   echo -n skull stripping..be patient..
    	@ nslpad = 16 - $ns
    
    	if ($nslpad < 0) then
		  set nslpad = 0
    	endif

    	3dZeropad -S $nslpad -I $nslpad -prefix pcaslM0images_padded pcaslM0images+orig.BRIK >>& $logfile
    	3dSkullStrip -prefix pcaslM0images_padded_nskl -input pcaslM0images_padded+orig >>& $logfile
    	@ nnslpad = -1 * $nslpad
    	# echo $nnslpad
    	3dZeropad -S $nnslpad -I $nnslpad -prefix $nskloutp pcaslM0images_padded_nskl+orig.BRIK >>& $logfile
    	rm -f pcaslM0images_padded+orig.* pcaslM0images_padded_nskl+orig.* >>& $logfile
    endif

    #Create binary mask if needed
    set binmaskoutp =  {$infilem}{_v0_binmsk}
    if !(-e {$binmaskoutp}{+orig.BRIK.gz}) then
	3dcalc -a {$nskloutp}{+orig.BRIK} -expr 'step(a)' -prefix $binmaskoutp >>& $logfile
    endif

    #omit first 5 volumes (M0 and 4 more) and extract odd and even images
    3dcalc -a {$infile}{'[5..$(2)]'} -exp 'a' -prefix pcaslOddimages >>& $logfile
    3dcalc -a {$infile}{'[6..$(2)]'} -exp 'a' -prefix pcaslEvenimages >>& $logfile

    #calculate difference images
   # 3dcalc -a pcaslOddimages+orig -b pcaslEvenimages+orig -expr 'a-b' -prefix pcaslDiffimages  >>& $logfile    #diff time series
    3dcalc -a pcaslOddimages+orig -b pcaslEvenimages+orig -expr 'a-b' -prefix $outdiffsp  >>& $logfile    #diff time series

    #detect outliers in the diff images before averaging
  #  (3dToutcount -mask {$binmaskoutp}{+orig.BRIK} -fraction pcaslDiffimages+orig.BRIK > pcasloutlcount.1D) >>& $logfile
    (3dToutcount -mask {$binmaskoutp}{+orig.BRIK} -fraction -save pcasloutlQimages {$outdiffsp}{+orig.BRIK} > pcasloutlcount.1D) >>& $logfile
    set nlines = `wc -l pcasloutlcount.1D`; set nlines = $nlines[1]
    (1dplot -DAFNI_1DPLOT_BOXSIZE=0.01 -box -xlabel 'Image Number' -ylabel 'Fraction of Outlier Pixels' -one pcasloutlcount.1D 1D:$nlines@$outlthres >>& $logfile) &


    1deval -a pcasloutlcount.1D -expr 'ispositive('$outlthres' - a)' > pcasloutlcount_binmask.1D
    set goodvols = `1d_tool.py -infile pcasloutlcount_binmask.1D -show_trs_uncensored encoded` 
    set outlvols = `1d_tool.py -infile pcasloutlcount_binmask.1D -show_trs_censored encoded` 
    set numoutlvols = `1d_tool.py -infile pcasloutlcount_binmask.1D -show_censor_count` 
   
    #average difference images
    if ($goodvols == "") then
	echo "**No good volumes**, use them all anyway" | tee -a $logfile
    	# 3dTstat -prefix pcaslAvgdiffimages pcaslDiffimages+orig >>& $logfile            #average diff time series
	3dTstat -prefix pcaslAvgdiffimages {$outdiffsp}{+orig.BRIK} >>& $logfile            #average diff time series

    else
        echo "Num. outlier volumes = $numoutlvols[7], Outlier vol#s: $outlvols ;Good vol#s: $goodvols" | tee -a $logfile
       # 3dTstat -prefix pcaslAvgdiffimages pcaslDiffimages+orig.BRIK"[$goodvols]" >>& $logfile            #average diff time series
       3dTstat -prefix pcaslAvgdiffimages {$outdiffsp}{+orig.BRIK}"[$goodvols]" >>& $logfile            #average diff time series
       # 3dcalc -a {$outdiffsp}{+orig.BRIK}"[$goodvols]" -expr 'a' -prefix temp
    endif
 

    #Calculate normalized difference
    #3dcalc -a pcaslAvgdiffimages+orig -b pcaslM0images+orig -c {$nskloutp}{+orig.BRIK} -expr '(a/b)*step(c)' -float -prefix pcaslNormdiffimages  >>& $logfile
    3dcalc -a pcaslAvgdiffimages+orig -b pcaslM0images+orig -c {$nskloutp}{+orig.BRIK} -expr '(a/b)*step(c)' -float -prefix $outndiffp  >>& $logfile


    #PCASL eqn assuming tag remains in the vasculature
    # cbf  = 6000*(lambda/(2*alpha*t1a))*(exp(postlabdly/t1a)*(1.0/(1.0-exp(-labdur/t1a))) * (deltaS/S0) 
    # lambda in ml/g, t1a in seconds, cbf is in ml/(min.100g)

    set fixedfact = `1deval -expr "6000.0 * $lambda/(2.0*$alpha*$t1a*(1.0- exp(-$labdur/$t1a)))" -num 1` 

    if ($#slicetimes == 0) then
	echo -n Applying the the same CBF conversion factor for all slices | tee -a $logfile
   	# 3dcalc -a pcaslNormdiffimages+orig -expr "a * $fixedfact * exp($postlabdly/$t1a)" -prefix $outfilep >>& $logfile
  	3dcalc -a {$outndiffp}{+orig.BRIK} -expr "a * $fixedfact * exp($postlabdly/$t1a)" -prefix $outfilep >>& $logfile
    else
     	echo -n Applying slice dependent CBF conversion factor | tee -a $logfile
    	set slc = 0
    	while ($slc < $ns) 
   		set cnt = `ccalc -i $slc + 1`
   		# 3dZcutup -overwrite  -keep $slc $slc -prefix ttt pcaslNormdiffimages+orig >>& $logfile
   		3dZcutup -overwrite  -keep $slc $slc -prefix ttt {$outndiffp}{+orig.BRIK} >>& $logfile
   		set ppp = `printf %02d $slc`

        	set slpostlabdly = `1deval -expr "$postlabdly + $slicetimes[$cnt]" -num 1` 
		set convfact = `1deval -expr "$fixedfact * exp($slpostlabdly/$t1a)" -num 1`
   		3dcalc -a ttt+orig -expr "a * $convfact" -prefix ttt.$ppp >>& $logfile
 
        	@ slc ++
        	echo -n .
    	end
    	3dZcat -overwrite -prefix $outfilep ttt.??+orig.HEAD >>& /dev/null
    	rm -f ttt*
    endif 
    echo .

    #create nii files of ndiff and cbf images
    3dAFNItoNIFTI -float -prefix $outndiffp {$outndiffp}{+orig.BRIK} >>& $logfile
    3dAFNItoNIFTI -float -prefix $outfilep {$outfilep}{+orig.BRIK} >>& $logfile

    #clean up
    if ($clean) then
    	rm -f pcasl*
    endif


    set error = `grep -c ERROR $logfile`
    if ($error == 0) then
     	set message = `echo -procPCASL: Done with processing, created {$outfilep}{+orig.BRIK}` 
    else
	set message = `echo -procPCASL: Errors encountered during processing. Check $logfile` 
    endif 
    echo $message | tee -a $logfile

# else

#     echo -procPCASL: Processed files exist
# endif

exit 0


  
