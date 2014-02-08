gf = read.csv('~/Documents/philip/dti/FINAL_TSA_noOutliers.csv')
tmp = gf$DX_GROUP
a = read.table('~/data/results/tbss/good_RD_nvVSper_cov_02.txt')
data = colMeans(a[,4:dim(a)[2]])
idx = tmp=='NV' | tmp=='persistent'
te = t.test(data[idx] ~ tmp[idx])
str = sprintf('Group differences, nv < persistent (p<%.2e)',
              te$p.value)
boxplot(data~tmp, main=str, xlab="Outcome", ylab="Mean RD")
