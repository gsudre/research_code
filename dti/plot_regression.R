gf = read.csv('~/Documents/philip/dti/FINAL_TSA_noOutliers.csv')
data = gf$SX_inattb
nsubj = dim(gf)[1]
tmp = vector()
for (i in 1:nsubj) {
    if (gf[i,]$DX_GROUP=='persistent') {
        tmp = c(tmp, data[i])
    }
}
for (i in 1:nsubj) {
    if (gf[i,]$DX_GROUP=='remitted') {
        tmp = c(tmp, data[i])
    }
}
a = read.table('~/data/results/tbss/good_RD_inatt_cov_02.txt')
data = colMeans(a[,4:dim(a)[2]])
fit = lm(data~tmp)
plot(tmp,data,xlab='Inattention symptoms',ylab='Mean RD')
pdata = expand.grid(tmp=seq(0, 9, by=1))
y = predict(fit, pdata, level = 0)
lines(pdata$tmp,y,lwd=2)
print(summary(fit))
mycor = cor.test(tmp,data)
print(mycor)
title(sprintf('Slope sig: %.1e, R: %.3f', 
              summary(fit)$coefficients[2,4],
              mycor$estimate))