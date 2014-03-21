gf = read.csv('~/Documents/philip/dti/FINAL_TSA_allClean149.csv')
tmp = gf$DX_GROUP
a = read.table('~/data/results/tbss/plotdata_FA_nvVSper_95.txt')
data = colMeans(a[,4:dim(a)[2]])
idx = tmp=='NV' | tmp=='persistent'
te = t.test(data[idx] ~ tmp[idx])
str = sprintf('Group differences, nv < persistent (p<%.2e)',
              te$p.value)
boxplot(data~tmp, main=str, xlab="Outcome", ylab="FA",
        col='red')
