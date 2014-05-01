# Constructs the masked results in standard space
# RUN IT FROM THE SAME DIRECTORY WHERE RESULTS ARE STORED!
# Remember to also change the comparison based on the test that was made and the mode being used!

# # nv vs persistent
# for num in 95; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             # FA is always a bit different
#             echo "FA"
#             fname=nvVSrem_covs_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_nvVSrem_covs_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # for mode in TR AD RD; do
#             #     echo ${mode}
#             #     fname=nvVSper_${mode}_${num}_${clu}_${mc}p
#             #     fslmaths tbss_10K_nvVSper_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#             #     applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # done;
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

# # inatt
# for num in 05; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             # FA is always a bit different
#             echo "FA"
#             fname=inatt_covs_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_inatt_covs_FA_${clu}_${mc}p_tstat1.nii.gz -uthr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # for mode in TR AD RD; do
#             #     echo ${mode}
#             #     fname=inatt_${mode}_${num}_${clu}_${mc}p
#             #     fslmaths tbss_10K_inatt_${mode}_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname} 
#             #     applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # done;
#         done;
#     done;
# done

# # nv vs persistent Inatt only
# for num in 95 99 995 999; do
#     echo $num 
#     for clu in tfce vox; do 
#         for mc in corr ''; do
#             # FA is always a bit different
#             echo "FA"
#             fname=nvVSperInatt_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_nvVSperInatt_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             for mode in AD RD; do
#                 echo ${mode}
#                 fname=nvVSperInatt_${mode}_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_nvVSperInatt_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             done;
#         done;
#     done;
# done

# # persistent vs remitted Inatt only
# for num in 95; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             # FA is always a bit different
#             echo "FA"
#             fname=perVSremInatt_covs_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_perVSremInatt_covs_FA_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # for mode in AD RD; do
#             #     echo ${mode}
#             #     fname=perVSremInatt_${mode}_${num}_${clu}_${mc}p
#             #     fslmaths tbss_10K_perVSremInatt_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#             #     applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # done;
#         done;
#     done;
# done

# # nv vs adhd only
# for num in 95 99 995 999; do
#     echo $num 
#     for clu in tfce vox; do 
#         for mc in corr ''; do
#             # FA is always a bit different
#             echo "FA"
#             fname=nvVSadhd_covs_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_nvVSadhd_covs_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             for mode in TR AD RD; do
#                 echo ${mode}
#                 fname=nvVSadhd_covs_${mode}_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_nvVSadhd_covs_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             done;
#         done;
#     done;
# done

# # dx groups
# for num in 95; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             for g in 5 6; do
#                 fname=anova_DXG${g}_FA_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_anova_DX${g}_FA_${clu}_${mc}p_fstat1.nii.gz -thr 0.${num} -bin ${fname} 
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             done;
#         done;
#     done;
# done

# # with covariates
# for num in 95; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             fname=nvVSadhd_covs_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_nvVSadhd_covs_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname} 
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#         done;
#     done;
# done

# intersect, nvVSadhdOnly, inattOnly
for num in 95; do
    echo $num 
    for clu in tfce; do 
        for mc in corr; do
            for mode in FA; do
                echo ${mode}
                fname=nvVSperOnly_comp1_covs_${mode}_${num}_${clu}_${mc}p
                3dcalc -prefix ${fname}.nii.gz -a nvVSrem_comp1_covs_FA_95_tfce_corrp.nii.gz -b nvVSper_comp1_covs_FA_95_tfce_corrp.nii.gz -expr 'b*not(a*b)'
                applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
            done;
        done;
    done;
done

# # inatt
# for num in 95; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             # FA is always a bit different
#             echo "FA"
#             fname=hi_covs_FA_${num}_${clu}_${mc}p
#             fslmaths tbss_10K_hi_covs_FA_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname};
#             applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # for mode in TR AD RD; do
#             #     echo ${mode}
#             #     fname=inatt_${mode}_${num}_${clu}_${mc}p
#             #     fslmaths tbss_10K_inatt_${mode}_${clu}_${mc}p_tstat1.nii.gz -thr 0.${num} -bin ${fname} 
#             #     applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#             # done;
#         done;
#     done;
# done

# # final analysis?
# for num in 95; do
#     echo $num 
#     for clu in tfce; do 
#         for mc in corr; do
#             for comp in 1 2; do 
#                 # FA is always a bit different
#                 echo "FA"
#                 fname=nvVSper_comp${comp}_covs_FA_${num}_${clu}_${mc}p
#                 fslmaths tbss_10K_nvVSper_covs_FA_${clu}_${mc}p_tstat${comp}.nii.gz -thr 0.${num} -bin ${fname};
#                 applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#                 # for mode in TR AD RD; do
#                 #     echo ${mode}
#                 #     fname=nvVSrem_${mode}_${num}_${clu}_${mc}p
#                 #     fslmaths tbss_10K_nvVSrem_${mode}_${clu}_${mc}p_tstat2.nii.gz -thr 0.${num} -bin ${fname} 
#                 #     applywarp -i ${fname} -r $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz -o ${fname}+FMRIB58 --premat=mean2FMRIB58.mat;
#                 # done;
#             done;
#         done;
#     done;
# done