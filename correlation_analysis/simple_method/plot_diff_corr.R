library(ggplot2)
hemi = 'R'
X = 'thalamus'
Y = 'gp'
groups = c('NV','remission','persistent')
ns = c(64,32,32)

fname = sprintf('~/data/results/simple/%sthalamus2%s_diff_thresh0.50_%sOnly.txt', 
                hemi, Y, groups[2])
res = read.table(fname, skip=3)
###
roiX = which(res[,1]>.21)
roiX = roiX[roiX<500]
###
fname = sprintf('~/data/results/simple/%s%s_diff_thresh0.50_%sOnly.txt', 
                hemi, Y, groups[2])
res = read.table(fname, skip=3)
###
roiY = which(res[,1]>.5)
###

eval(parse(text=sprintf('xdata = rowSums(%s%s[,roiX])',X,hemi)))
eval(parse(text=sprintf('ydata = rowSums(%s%s[,roiY])',Y,hemi)))


colors = c('black', 'red', 'blue')
rs = vector(mode='numeric', length=length(groups))
for (g in 1:3) {
    idxb = group==groups[g] & visit=='baseline'
    idxl = group==groups[g] & visit=='last'
    x=(xdata[idxl]-xdata[idxb])
    y=(ydata[idxl]-ydata[idxb])
    if (g==1) {
        plot(x,y,col=colors[g],pch=19,xlab=X,ylab=Y)
    } else {
        points(x,y,col=colors[g],pch=19)
    }
    rs[g] = cor(x,y)
    cat(groups[g],'r =',rs[g],'\n')
}
legend('topleft',groups,pch=19,col=colors)
title(sprintf('Diff (%s)',hemi))
# formulas from http://www.fon.hum.uva.nl/Service/Statistics/Two_Correlations.html
# and http://www.cyclismo.org/tutorial/R/pValues.html
zs = 1/2*log((1+rs)/(1-rs))
cat('Two-tailed p-values:\n')
cat(groups[1],'vs',groups[2],
    2*pnorm(-abs((zs[1]-zs[2])/sqrt(1/(ns[1]-3) + 1/(ns[2]-3)))),'\n')
cat(groups[1],'vs',groups[3],
    2*pnorm(-abs((zs[1]-zs[3])/sqrt(1/(ns[1]-3) + 1/(ns[3]-3)))),'\n')
cat(groups[2],'vs',groups[3],
    2*pnorm(-abs((zs[2]-zs[3])/sqrt(1/(ns[2]-3) + 1/(ns[3]-3)))),'\n')