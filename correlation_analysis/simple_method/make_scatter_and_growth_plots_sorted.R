# Makes scatterplots and growth plots of thalamus regions connected to seed, and cortical cluster around seed

# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')

seed=6503
hemi='R'
g = 'persistent'
conn_limit = .3

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

get_pval_from_Rs <- function(r1, n1, r2, n2) {
    b1 = 1/2*log((1+r1)/(1-r1))
    b2 = 1/2*log((1+r2)/(1-r2))
    z = (b1-b2)/sqrt(1/(n1-3)+1/(n2-3))
    return(2*pnorm(-abs(z)))
}

# makes brain picture with what vertices in the thalamus are connected to the seed.
# Also used to define thalamic ROIs later used in plots
load(sprintf('~/data/results/simple/es%s_thalamus2cortex_diff_%s.RData',hemi, g))
bes = binarize(abs(es),.5)
tha_roi = bes[,seed]
fname = sprintf('~/data/results/simple/thalamus2seed%d_%s_diff_%s.txt', 
                seed, hemi, g)
write_vertices(tha_roi, fname, c(g))

# let's define cor_roi as the neighboring vertices to the seed that share up
# to .41 connectivity
require(R.matlab)
mat = readMat('~/Documents/surfaces/IMAGING_TOOLS/cortex.mat')
if (hemi=='R') {
    nbr = mat[[7]]
} else {
    nbr = mat[[3]]
}
# load the cortex->thalamus connectivity values
conn = read.table(sprintf('~/data/results/simple/connectedness_p001_cortex%s_diff_per.txt',hemi),
                  skip=3)
conn = conn[,1]
roi = conn>=conn_limit
seed_cluster = vector(mode='numeric', length=length(conn))
# start with the seed and paint it
v = seed
seed_cluster[v] = 2
# find out what are the neighbors that are significant
paint_nbrs = intersect(nbr[v,],which(roi))
# of those, find out which ones haven't been painted yet
fresh_nbrs = paint_nbrs[seed_cluster[paint_nbrs]==0]
# while we still have significant neighbors to be painted
while (length(fresh_nbrs) > 0) {
    # paint all significant neighbors with the same current color
    seed_cluster[fresh_nbrs] = 1
    # the recently-painted neighbors become the target vertices 
    v = fresh_nbrs
    # repeat above until we have no more neighbors to paint
    paint_nbrs = intersect(nbr[v,],which(roi))
    fresh_nbrs = paint_nbrs[seed_cluster[paint_nbrs]==0]
}
cor_roi = seed_cluster>0
# write a brain file with the selected cluster and the seed in red
fname = sprintf('~/data/results/simple/clusterizedSeed%d_%s_diff_%s.txt', 
                seed, hemi, g)
write_vertices(seed_cluster, fname, c(g))

# makes a thalamus figure of correlations to the seed
eval(parse(text=sprintf('cor = cortex%s[,seed]', hemi)))
eval(parse(text=sprintf('tha = thalamus%s', hemi)))
for (g in c('persistent', 'remission', 'NV')) {
    cat('Correlations for group', g, '\n')
    idx = group==g
    y = cor[idx]
    y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
    rs = vector()
    ps = vector()
    for (v in 1:dim(tha)[2]) {
        x = tha[idx,v]
        x = x[seq(2,length(x),2)] - x[seq(1,length(x),2)]
        my_r = cor.test(y,x)$estimate
        my_p = cor.test(y,x)$p.value
        rs = c(rs, my_r)
        ps = c(ps, my_p)
    }
    fname = sprintf('~/data/results/simple/thalamusRs_seed%d_%s_diff_%s.txt', 
                    seed, hemi, g)
    write_vertices(cbind(rs,ps), fname, c('r','p'))
}

rs = vector()
par(mfrow=c(4,3))
# eval(parse(text=sprintf('cor = cortex%s[,seed]', hemi)))
eval(parse(text=sprintf('cor = rowSums(cortex%s[,cor_roi])', hemi)))
eval(parse(text=sprintf('tha = rowSums(thalamus%s[,tha_roi])', hemi)))
# separating the data for correlation plots
for (g in c('persistent', 'remission', 'NV')) {
    idx = group==g
    x = tha[idx]
    x = scale(x[seq(2,length(x),2)] - x[seq(1,length(x),2)])
    y = cor[idx]
    y = scale(y[seq(2,length(y),2)] - y[seq(1,length(y),2)])
#     x = x[y>=-.3]
#     y = y[y>=-.3]
    plot(x, y, xlab='Thalamus SA difference (mm2)',
         ylab='Cortex SA difference (mm2)',ylim=c(-6,4),xlim=c(-2.5,3.5))
    fit = lm(y ~ x)
    abline(fit, col="red", lwd=4)
    my_r = cor.test(y,x)$estimate
    title(sprintf('%s; r=%.2f; t=%.2f', g, my_r, summary(fit)$coefficients[2,3]))
    rs = c(rs, my_r)
}
# hard coded based on group order above!!!
cat('NV VS per:', get_pval_from_Rs(rs[3],64,rs[1],32), '\n')
cat('NV VS rem:', get_pval_from_Rs(rs[3],64,rs[2],32), '\n')
cat('per VS rem:', get_pval_from_Rs(rs[1],32,rs[2],32), '\n')

# setting up for cortical line growth plot
pdata <- expand.grid(age=seq(min(age), max(age), by=1))
for (g in c('persistent', 'remission', 'NV')) {
    idx = group==g
    y = cor[idx]
    y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
    x = age[idx]
    s = subject[idx]
    a = sort(y,index.return=T)
    eval(parse(text=sprintf('ix_%s = a$ix', g)))
    plot(a$x,ylab='Cortex SA',ylim=c(-200,200))
#     fit = lme(y~x, random=~1|s)
#     pred <- predict(fit, pdata, level = 0)
#     lines(x, pred, col='red',lwd=4)
    title(sprintf('beta=%.2f+-%.2f; p=%.2f',summary(fit)$tTable[2,1],
                  summary(fit)$tTable[2,2],summary(fit)$tTable[2,5]))
}

# setting up for thalamic line growth plot
pdata <- expand.grid(age=seq(min(age), max(age), by=1))
for (g in c('persistent', 'remission', 'NV')) {
    idx = group==g
    y = tha[idx]
    y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
    x = age[idx]
    s = subject[idx]
    eval(parse(text=sprintf('a = ix_%s', g)))
    plot(y[a],ylab='Thalamus SA',ylim=c(-50,200))
#     fit = lme(y~x, random=~1|s)
#     pred <- predict(fit, pdata, level = 0)
#     lines(x, pred, col='red',lwd=4)
    title(sprintf('beta=%.2f+-%.2f; p=%.2f',summary(fit)$tTable[2,1],
                  summary(fit)$tTable[2,2],summary(fit)$tTable[2,5]))
}

# setting up for z-score plots
pdata <- expand.grid(age=seq(min(age), max(age), by=1))
for (g in c('persistent', 'remission', 'NV')) {
    idx = group==g
    yc = scale(cor[idx])
    yt = scale(tha[idx])
    x = age[idx]
    s = subject[idx]
    fit = lme(yt~x, random=~1|s)
    pred <- predict(fit, pdata, level = 0)
    plot(x,pred,type='l',col='blue',xlab='Age',ylab='SA (red=cortex)',ylim=c(-.5,.8),xlim=c(5,35))
    fit = lme(yc~x, random=~1|s)
    pred <- predict(fit, pdata, level = 0)
    lines(x, pred, col='red',lwd=4)
    title(sprintf('blue=thalamus'))
}