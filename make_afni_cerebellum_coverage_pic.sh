#!/bin/bash
#
# set some environment variables
#
AFNI_NOSPLASH=YES;
AFNI_SPLASH_MELT=NO;
#
# make directory for output images
#
mkdir -p ~/tmp/snapshots
#
sub=$1;
cd /mnt/shaw/data_by_maskID/${sub}/afni;
ddd=${sub}.rest.subjectSpace.results;
# loop over the afni_proc.py results directories
#
epi=pb03.${sub}.r01.volreg+orig;
anat=${sub}_SurfVol+orig;
# name for output image file
jnam=$sub

# drive AFNI to get the images we want
afni -noplugins -no_detach                               \
        -com "OPEN_WINDOW sagittalimage opacity=6"          \
        -com "OPEN_WINDOW axialimage opacity=6"             \
        -com "OPEN_WINDOW coronalimage opacity=6"           \
        -com "SWITCH_OVERLAY $epi"                           \
        -com "SEE_OVERLAY +"                                \
	-com "SET_FUNC_AUTORANGE +" \
	-com "SET_IJK 75 170 60" \
        -com "SAVE_JPEG sagittalimage sag1.jpg"     \
        -com "SAVE_JPEG coronalimage  cor1.jpg"     \
        -com "SAVE_JPEG axialimage    axi1.jpg"     \
	-com "SET_IJK 83 170 63" \
        -com "SAVE_JPEG sagittalimage sag2.jpg"     \
        -com "SAVE_JPEG coronalimage  cor2.jpg"     \
        -com "SAVE_JPEG axialimage    axi2.jpg"     \
	-com "SET_IJK 79 170 66" \
        -com "SAVE_JPEG sagittalimage sag3.jpg"     \
        -com "SAVE_JPEG coronalimage  cor3.jpg"     \
        -com "SAVE_JPEG axialimage    axi3.jpg"     \
	-com "SET_IJK 95 170 70" \
        -com "SAVE_JPEG sagittalimage sag4.jpg"     \
        -com "SAVE_JPEG coronalimage  cor4.jpg"     \
        -com "SAVE_JPEG axialimage    axi4.jpg"     \
	-com "SET_IJK 105 170 80" \
        -com "SAVE_JPEG sagittalimage sag5.jpg"     \
        -com "SAVE_JPEG coronalimage  cor5.jpg"     \
        -com "SAVE_JPEG axialimage    axi5.jpg"     \
	-com "SET_IJK 125 170 90" \
        -com "SAVE_JPEG sagittalimage sag6.jpg"     \
        -com "SAVE_JPEG coronalimage  cor6.jpg"     \
        -com "SAVE_JPEG axialimage    axi6.jpg"     \
	-com "SET_IJK 145 170 100" \
        -com "SAVE_JPEG sagittalimage sag7.jpg"     \
        -com "SAVE_JPEG coronalimage  cor7.jpg"     \
        -com "SAVE_JPEG axialimage    axi7.jpg"     \
	-com "SET_IJK 155 170 110" \
        -com "SAVE_JPEG sagittalimage sag8.jpg"     \
        -com "SAVE_JPEG coronalimage  cor8.jpg"     \
        -com "SAVE_JPEG axialimage    axi8.jpg"     \
	-com "SET_IJK 175 170 120" \
        -com "SAVE_JPEG sagittalimage sag9.jpg"     \
        -com "SAVE_JPEG coronalimage  cor9.jpg"     \
        -com "SAVE_JPEG axialimage    axi9.jpg"     \
	-com "QUIT" \
    -dset $ddd/$anat $ddd/$epi'[0]'

# convert the JPEG outputs to PNM for NetPBM manipulations
sags='';
cors='';
for i in {1..9}; do
	djpeg sag${i}.jpg > sag${i}.pnm;
	djpeg cor${i}.jpg > cor${i}.pnm;
	djpeg axi${i}.jpg > axi${i}.pnm;
	sags=$sags' 'sag${i}.pnm;
	cors=$cors' 'cor${i}.pnm;
done;
# the commands below make a labeled composite image, and require NetPBM
pnmcat -lr -jcenter -black $sags > sag.pnm;
pnmcat -lr -jcenter -black $cors > cor.pnm;
pnmcat -tb -jcenter -black sag.pnm cor.pnm > qqq.pnm
# make a text overlay
pbmtext $jnam  > qqq.pbm
# overlay the text image on the composite, convert to JPEG
pamcomp -xoff=1 -yoff=1 qqq.pbm qqq.pnm | cjpeg -quality 95 > ~/tmp/snapshots/$jnam.jpg

 exit 0
