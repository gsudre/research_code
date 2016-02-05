# checking difference between med and unmed at baseline
# source('~/research_code/correlation_analysis/compile_baseline.R')

fnameRoot = '~/data/results/structural_v2/baselineANOVA_nvVSmedVSunmed'

idx = gfBase$MED.x==1 | gfBase$MED.x==0 | gfBase$MED.x=='NV'

# # making sure there's no difference at baseline age and sex
# print(t.test(gfBase[idx,]$AGESCAN ~ as.factor(gfBase[idx,]$MED.x)))
# print(table(gfBase[idx,]$MED.x,gfBase[idx,]$SEX.x))

# whole thalamus analysis
d = data.frame(y=rowSums(thalamusLBase[idx,]), med=gfBase[idx,]$MED.x,
               age=gfBase[idx,]$AGESCAN, sex=gfBase[idx,]$SEX.x)
# fit <- lm(y~med+sex+age, data=d)
fit <- aov(y~med+sex+age, data=d)
print(summary(fit))
d = data.frame(y=rowSums(thalamusRBase[idx,]), med=gfBase[idx,]$MED.x,
               age=gfBase[idx,]$AGESCAN, sex=gfBase[idx,]$SEX.x)
# fit <- lm(y~med+sex+age, data=d)
fit <- aov(y~med+sex+age, data=d)
print(summary(fit))

# vertex analysis
brain_data = c('thalamusLBase','thalamusRBase')
for (b in brain_data) {
    eval(parse(text=sprintf('data=%s', b)))
#     vs = mni.vertex.statistics(gfBase[idx,], 'y~MED.x+AGESCAN+SEX.x', t(data[idx,]))
    vs = mni.vertex.anova(gfBase[idx,], 'y~MED.x+AGESCAN+SEX.x', t(data[idx,]))
    fname = sprintf('%s_%s.txt', fnameRoot, b)
    mni.write.vertex.stats(vs, fname)
#     num_voxels = dim(data)[2]
# #     num_values = dim(summary(fit)$coefficients)[1]*dim(summary(fit)$coefficients)[2]
#     num_values = dim(summary(fit)[[1]])[1]*dim(summary(fit)[[1]])[2]
#     tsLinear <- array(dim=c(num_voxels, num_values))
#     for (v in 1:num_voxels) {
#         print(sprintf('%d / %d', v, num_voxels))
#         d = data.frame(y=data[idx,v], med=gfBase[idx,]$MED.x,
#                        age=gfBase[idx,]$AGESCAN, sex=gfBase[idx,]$SEX.x)
#         fit <- try(lm(y~med+sex+age, data=d), TRUE)
#         fit <- try(aov(y~med+sex+age, data=d), TRUE)
#         if (length(fit) > 1) {  
# #             tmp = summary(fit)$coefficients
#             tmp = as.matrix(summary(fit)[[1]])
#             dim(tmp) = NULL
#             tsLinear[v,] <- tmp
#         }
#     }
#     colNames = vector()
# #     tmp = summary(fit)$coefficients
#     tmp = as.matrix(summary(fit)[[1]])
#     for (i in colnames(tmp)) {
#         for (j in rownames(tmp)) {
#             colNames = c(colNames, paste(i,j,sep=':'))
#         }
#     }
#     fname = sprintf('%s_%s.txt', fnameRoot, b)
#     write_vertices(tsLinear, fname, gsub(' ','',colNames))
}

# and do the same for volume analysis
csvData = read.csv('~/data/structural/VOLUMES_SA_SOOURCE_OCT_2012.csv')
vol_columns = c(4,7,14:35)
nsubjs = dim(gfBase)[1]
thalVolumeBase = matrix(nrow=nsubjs, ncol=length(vol_columns))
for (i in 1:nsubjs) {
    idx2 = csvData[,1]==gfBase[i,]$MASKID.x
    if (sum(idx2) != 1) {
        cat('ERROR finding maskid',gfBase[i,]$MASKID.x,'\n')
    } else {
        thalVolumeBase[i,] = as.matrix(csvData[idx2,vol_columns])
    }
}
colnames(thalVolumeBase) = colnames(csvData)[vol_columns]

load('~/data/structural/normalization_volumes_gf1473.RData')
ps = vector()
for (i in 1:dim(thalVolumeBase)[2]) {
    m = lm(thalVolumeBase[idx,i] ~ gfBase[idx,]$MED.x + rowSums(normVolumeBase[idx,3:5]) +
               gfBase[idx,]$AGESCAN + gfBase[idx,]$SEX.x)
    if (i<=2) { 
        cat('===', colnames(thalVolumeBase)[i], '===\n')
        print(summary(m)) }
    ps = c(ps, summary(m)$coefficients[2,4])
}