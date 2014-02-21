# Constructs the masked results in standard space
# RUN IT FROM THE SAME DIRECTORY WHERE RESULTS ARE STORED!
# Remember to also change the comparison based on the test that was made and the mode being used!

# # nv vs persistent
# for num in 95 99 995 999; do
#     echo $num 
#     for clu in tfce vox; do 
#         for mc in corr ''; do
#             # FA is always a bit different
#             echo "FA"
#             fname=nvVSper_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_nvVSper_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             for mode in TR AD RD; do
#                 echo ${mode}
#                 fname=nvVSper_${mode}_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_nvVSper_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             done;
#         done;
#     done;
# done

# # nv vs remitted
# for num in 95 99 995 999; do
#     echo $num 
#     for clu in tfce vox; do 
#         for mc in corr ''; do
#             # FA is always a bit different
#             echo "FA"
#             fname=nvVSrem_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_nvVSrem_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             for mode in TR AD RD; do
#                 echo ${mode}
#                 fname=nvVSrem_${mode}_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_nvVSrem_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             done;
#         done;
#     done;
# done

# # persistent vs remitted
# for num in 95 99 995 999; do
#     echo $num 
#     for clu in tfce vox; do 
#         for mc in corr ''; do
#             # FA is always a bit different
#             echo "FA"
#             fname=perVSrem_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_perVSrem_FA_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             for mode in TR AD RD; do
#                 echo ${mode}
#                 fname=perVSrem_${mode}_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_perVSrem_${mode}_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname} 
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             done;
#         done;
#     done;
# done

# inatt
for num in 95 99 995 999; do
    echo $num 
    for clu in tfce vox; do 
        for mc in corr ''; do
            # FA is always a bit different
            echo "FA"
            fname=inatt_FA_${num}_${clu}_${mc}p
            fslmaths tbss_10K_inatt_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
            applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
            for mode in TR AD RD; do
                echo ${mode}
                fname=inatt_${mode}_${num}_${clu}_${mc}p
                fslmaths tbss_10K_inatt_${mode}_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname} 
                applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
            done;
        done;
    done;
done