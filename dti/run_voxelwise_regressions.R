# Runs a mixed model linear regression for all voxels in each tract. Also report the regression values for the regression using the mean over all voxels. The results are graphs of the T-values for every voxel.

tract_names = c('left_cst')#, 'left_ifo', 'left_ilf', 'left_slf', 'left_unc', 'right_cst', 'right_ifo', 'right_ilf', 'right_slf', 'right_unc', 'cc')
var_names = c('FA')#, 'AD', 'RD')
subj_file = '/mnt/shaw/dti_robust_tsa/analysis/subjs_diffeo.txt'
data_dir = '/mnt/shaw/dti_robust_tsa/analysis/family_and_sibs_sampling/'
phen_dir = '~/data/solar_familyAndSibs/'
dti_type = 'mean'

in_fname = sprintf('%s_sampling.gzip',dti_type)
phen_fname = sprintf('%s/dti_%s_phenotype_cleanedWithinTract_merged_nodups.csv',phen_dir, dti_type)

load('~/research_code/mni_functions.RData')
library(nlme)
load(sprintf('%s/%s',data_dir,in_fname))
subjs = read.table(subj_file)
res = as.character(subjs$V1)
# keeping only mask ids in the first column
cnt = 1
for (subj in res) {
    res[cnt] = unlist(strsplit(subj,'_'))[1]
    cnt = cnt + 1
}
subjs = as.numeric(res)

# figure out the indexes of the phenotype subjects in the voxel data. This avoids having to re-clean the data and look for duplicates again. Also,  we were running all of memory to spit out the values of each voxel as a TXT
phen = read.csv(phen_fname)
idx = vector()
for (m in phen$file) {
    idx = c(idx, which(subjs==m))
}

for (tract in tract_names) {
    print(sprintf("%s",tract))
    for (var in var_names) {
        eval(parse(text=sprintf('data = %s_%s', var, tract)))

        data = data[,idx]

        # for (sx in c('inatt', 'hi', 'total')) {
        #     fixed = sprintf('y ~ %s + age + sex', sx)
        #     vs = mni.vertex.mixed.model(phen, fixed, '~1|famid', data)
        #     eval(parse(text=sprintf('y = phen$%s_%s', var, tract)))
        #     fit = lme(as.formula(fixed), random=~1|famid, data=phen, na.action=na.omit)
        #     p = summary(fit)$tTable[2,5]
        #     t = summary(fit)$tTable[2,4]

        #     jpeg(sprintf('%s/%s_%s_%s_%s.jpg',phen_dir,dti_type,sx,var,tract))
        #     plot(vs$t.value[,2],type='l',xlab='voxels',ylab='T-stats')
        #     title(sprintf('%s_%s : %s : mean t=%.3f (p<%.3f)', var, tract, in_fname, t, p))
        #     abline(h=1.96,lty=3,col='red')
        #     abline(h=-1.96,lty=3,col='red')
        #     abline(h=-2.58,lty=3,col='blue')
        #     abline(h=2.58,lty=3,col='blue')
        #     dev.off()
        # }
    }
}
