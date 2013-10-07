library(igraph)
createNetwork <- function(data, sparsity) {
    # remove correlation to itself
    data[data==1] = 0
    step=.01
    sp = 0
    thresh = .9
    while (sp < sparsity) {
        thresh = thresh - step
        mb = data
        mb[abs(data)>thresh] = 1
        mb[abs(data)<=thresh] = 0
        sp = sum(mb==1)/(dim(data)[1]*dim(data)[2])
    }
    net = graph.adjacency(mb,mode='undirected')
    return(net)
}

getGamma <- function(net) {
    num_perms = 100
    d = mean(degree(net))
    # degree needs to be even, so get the closest even number to the degree
    if (floor(d) %% 2 == 0) {
        d = floor(d)
    } else {
        d = ceiling(d)
    }
    v = vcount(net)
    cc = transitivity(net)
    rn = 0
    for (i in 1:num_perms) {
        rn = rn + transitivity(degree.sequence.game(rep(d,v)))
    }
    rn = rn/num_perms
    return(cc/rn)
}

getLambda <- function(mynet) {
    num_perms = 100
    d = mean(degree(mynet))
    # degree needs to be even, so get the closest even number to the degree
    if (floor(d) %% 2 == 0) {
        d = floor(d)
    } else {
        d = ceiling(d)
    }
    v = vcount(mynet)
    apl = average.path.length(mynet)
    rn = 0
    for (i in 1:num_perms) {
        rn = rn + average.path.length(degree.sequence.game(rep(d,v)))
    }
    rn = rn/num_perms
    return(apl/rn)
}

permuteMetric <- function(data1, data2, sparsity, fun) 
{
    nperms = 1000
    ds <- vector(mode = "numeric", length = nperms) 
    all_data = rbind(data1, data2)
    n1 = dim(data1)[1]
    n2 = dim(data2)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(all_data)[1], replace = FALSE)
        perm_data <- all_data[perm_labels, ]
        pmat1 = perm_data[1:n1, ]
        pmat2 = perm_data[(n1+1):(n1+n2), ]
        cor1 = pcor(pmat1)$estimate
        cor2 = pcor(pmat2)$estimate
        net1 = createNetwork(cor1, sparsity)
        net2 = createNetwork(cor2, sparsity)
        ds[i] = fun(net1) - fun(net2)
    }
    ds = sort(ds)
    res = list(m=mean(ds),lci=ds[floor(.025*nperms)],uci=ds[floor(.975*nperms)])
    return(res)
}

permuteBetweeness <- function(data1, data2, sparsity) 
{
    nperms = 1000
    nrois = dim(data1)[2]
    ds <- matrix(nrow=nperms,ncol=nrois)
    all_data = rbind(data1, data2)
    n1 = dim(data1)[1]
    n2 = dim(data2)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(all_data)[1], replace = FALSE)
        perm_data <- all_data[perm_labels, ]
        pmat1 = perm_data[1:n1, ]
        pmat2 = perm_data[(n1+1):(n1+n2), ]
        cor1 = pcor(pmat1)$estimate
        cor2 = pcor(pmat2)$estimate
        net1 = createNetwork(cor1, sparsity)
        net2 = createNetwork(cor2, sparsity)
        b = betweenness(net1)
        bnorm1 = b/mean(b)
        b = betweenness(net2)
        bnorm2 = b/mean(b)
        ds[i,] = bnorm1 - bnorm2
    }
    lci <- vector(mode = "numeric", length = nrois) 
    uci <- vector(mode = "numeric", length = nrois)
    for (r in 1:nrois) {
        rds = sort(ds[,r])
        lci[r] = rds[floor(.025*nperms)]   
        uci[r] = rds[floor(.975*nperms)]
    }
    res = list(m=colMeans(ds),lci=lci,uci=uci)
    return(res)
}

getPval <- function(r1, r2, n1, n2) {
    # returns the p-value for the null hypothesis that r1==r2. Uses a Z-transformation
    # r1 and r2 are square matrices of Rs
    print('DO NOT USE ME TO TEST DIFFERENCE OF CORRELATIONS!!! USE THAT OTHER PAPER TO GET CIS')
    z1 = atanh(r1)
    z2 = atanh(r2)
    variance = 1/(n1-3) + 1/(n2-3)
    z = (z1-z2)/sqrt(variance)
    pval = pnorm(z)
    for (i in 1:dim(pval)[1]) {
        for (j in 1:dim(pval)[1]) {
            pval[i,j] = min(pval[i,j],1-pval[i,j])
        }
    }
    return(pval*2)
}

pcorr = pcorb
rcorr = rcorb
pdata = pmatb
rdata = rmatb
sparsity = seq(.06,.4,.02)

#### Generating figure 2
plambda = vector(length=length(sparsity))
rlambda = vector(length=length(sparsity))
pgamma = vector(length=length(sparsity))
rgamma = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    pnet = createNetwork(pcorr, s)
    plambda[cnt] = getLambda(pnet)
    pgamma[cnt] = getGamma(pnet)
    rnet = createNetwork(rcorr, s)
    rlambda[cnt] = getLambda(rnet)
    rgamma[cnt] = getGamma(rnet)
    cnt = cnt + 1
}
maxY = max(ceiling(max(rgamma)),ceiling(max(pgamma)))
par(mfrow=c(1,2))
plot(sparsity, plambda, type="l", col='black', ylim=c(0, maxY), lwd=2)
lines(sparsity, pgamma, type="l", col='grey', lwd=2)
legend('topright', c('Lambda', 'Gamma'), col=c('black','grey'), lwd=2)
title('Small-Worldness, Persistent')
plot(sparsity, rlambda, type="l", col='black', ylim=c(0, maxY), lwd=2)
lines(sparsity, rgamma, type="l", col='grey', lwd=2)
legend('topright', c('Lambda', 'Gamma'), col=c('black','grey'), lwd=2)
title('Small-Worldness, Remission')

#### Figure 3A ####
pcc = vector(length=length(sparsity))
rcc = vector(length=length(sparsity))
lcicc = vector(length=length(sparsity))
ucicc = vector(length=length(sparsity))
nullcc = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    print(sprintf('Working on sparsity %.2f', s))
    pcc[cnt] = transitivity(createNetwork(pcorr, s))
    rcc[cnt] = transitivity(createNetwork(rcorr, s))
    perm = permuteMetric(pdata,rdata,s,transitivity)
    nullcc[cnt] = perm$m
    ucicc[cnt] = perm$uci
    lcicc[cnt] = perm$lci
    cnt = cnt + 1
}
diff_cc = pcc-rcc
maxY = max(max(rcc),max(pcc))
par(mfrow=c(1,2))
plot(sparsity, pcc, type="l", col='black', ylab='Cp', ylim=c(0, maxY), lwd=2)
lines(sparsity, rcc, type="l", col='grey', lwd=2)
legend('bottomright', c('Persistent', 'Remission'), col=c('black','grey'), lwd=2)
title('Mean Clustering Coefficient')
maxY = max(max(ucicc),max(diff_cc))
minY = min(min(lcicc),min(diff_cc))
plot(sparsity, diff_cc, type="o", ylab='Diff Cp', col='red', ylim=c(minY, maxY), lwd=2)
lines(sparsity, nullcc, type="o", col='grey', lwd=2)
lines(sparsity, lcicc, type="l", col='grey', lwd=2)
lines(sparsity, ucicc, type="l", col='grey', lwd=2)
title('Difference')

#### Figure 3B ####
papl = vector(length=length(sparsity))
rapl = vector(length=length(sparsity))
lciapl = vector(length=length(sparsity))
uciapl = vector(length=length(sparsity))
nullapl = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    print(sprintf('Working on sparsity %.2f', s))
    papl[cnt] = average.path.length(createNetwork(pcorr, s))
    rapl[cnt] = average.path.length(createNetwork(rcorr, s))
    perm = permuteMetric(pdata,rdata,s,average.path.length)
    nullapl[cnt] = perm$m
    uciapl[cnt] = perm$uci
    lciapl[cnt] = perm$lci
    cnt = cnt + 1
}
diff_apl = papl-rapl
maxY = max(max(rapl),max(papl))
par(mfrow=c(1,2))
plot(sparsity, papl, type="l", col='black', ylab='Cp', ylim=c(0, maxY), lwd=2)
lines(sparsity, rapl, type="l", col='grey', lwd=2)
legend('bottomright', c('Persistent', 'Remission'), col=c('black','grey'), lwd=2)
title('Mean Path Length')
maxY = max(max(uciapl),max(diff_apl))
minY = min(min(lciapl),min(diff_apl))
plot(sparsity, diff_apl, type="o", ylab='Diff Cp', col='red', ylim=c(minY, maxY), lwd=2)
lines(sparsity, nullapl, type="o", col='grey', lwd=2)
lines(sparsity, lciapl, type="l", col='grey', lwd=2)
lines(sparsity, uciapl, type="l", col='grey', lwd=2)
title('Difference')

#### Figure 4 ####
library(MESS)
par(mfrow=c(1,2))
y = auc(sparsity,nullcc)
x = 0
upper = auc(sparsity,ucicc)
lower = auc(sparsity,lcicc)
auccc = auc(sparsity,diff_cc)
maxY = max(max(upper),max(auccc))
minY = min(min(lower),min(auccc))
plot(x, y, ylim=c(minY, maxY),xaxt='n',ylab='AUC Diff Cp',xlab='')
arrows(x,upper, x, lower, angle=90, code=3, length=.1)
points(x, auccc, pch=15, col='black')
title('Cluster coefficient')
y = auc(sparsity,nullapl)
upper = auc(sparsity,uciapl)
lower = auc(sparsity,lciapl)
aucapl = auc(sparsity,diff_apl)
maxY = max(max(upper),max(aucapl))
minY = min(min(lower),min(aucapl))
plot(x, y, ylim=c(minY, maxY),xaxt='n',ylab='AUC Diff Lp',xlab='')
arrows(x,upper, x, lower, angle=90, code=3, length=.1)
points(x, aucapl, pch=15, col='black')
title('Path length')

#### Table 1 ####
thresh = .05
pval_connections = getPval(pcorr, rcorr, dim(pdata)[1], dim(rdata)[1])
pval_connections = pval_connections[upper.tri(pval_connections)]
pval_connections = p.adjust(pval_connections, method='fdr')
good_pvals = pval_connections < thresh
num_good_pvals = sum(good_pvals)
print(sprintf('Total of significant differences: %d', sum(good_pvals)))
if (num_good_pvals > 0) {
    ppvals = pcor(pmatb)$p.value
    rpvals = pcor(rmatb)$p.value
    ppvals = ppvals[upper.tri(ppvals)]
    rpvals = rpvals[upper.tri(rpvals)]
    ppvals = p.adjust(ppvals, method='fdr')
    rpvals = p.adjust(rpvals, method='fdr')
    p_good_pvals = ppvals < thresh
    r_good_pvals = rpvals < thresh
    very_good_pvals = good_pvals & (p_good_pvals | r_good_pvals)
    nrows = sum(very_good_pvals)
    print(sprintf('Significant differences with significant Rs: %d', nrows))
    if (nrows > 0) {
        pvals2list = pval_connections[very_good_pvals]
        pcorr2list = pcorr[upper.tri(pcorr)][very_good_pvals]
        rcorr2list = rcorr[upper.tri(rcorr)][very_good_pvals]
        cat('ROI1\t\t\t\t\t\t\t\tROI2\t\t\t\t\t\t\tPersistent\t\t\tRemission\t\t\tDiff pval\n')
        for (i in 1:nrows) {
            idx = which(pcorr==pcorr2list[i] & rcorr==rcorr2list[i], arr.ind=TRUE)
            cat(sprintf("%s\t\t\t%s\t\t\t%.2f\t\t\t%.2f\t\t\t%.3f\n",
                        colnames(pcorr)[idx[1]],colnames(pcorr)[idx[2]],
                          pcorr2list[i],rcorr2list[i],pvals2list[i]))
        }
    }
}

#### Figure 5 ####
pmax = vector(length=length(sparsity))
rmax = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    pmax[cnt] = max(clusters(createNetwork(pcorr, s))$csize)
    rmax[cnt] = max(clusters(createNetwork(rcorr, s))$csize)
    cnt = cnt + 1
}
plot(sparsity,pmax,type='l',lwd=2,col='black',ylim=c(5,dim(pcorr)[1]+2),ylab='Size of largest component')
lines(sparsity,rmax,type='l',lwd=2,col='grey')
legend('bottomright', c('Persistent', 'Remission'), col=c('black','grey'), lwd=2)
print('Lowest sparsity threshold in which both of the networks included all connected nodes:')
min_sparsity = min(sparsity[pmax==dim(pcorr)[1] & rmax==dim(pcorr)[1]])
print(min_sparsity)

#### Figure 6A ####
pnet = createNetwork(pcorr, min_sparsity)
b = betweenness(pnet)
pbnorm = b/mean(b)
rnet = createNetwork(rcorr, min_sparsity)
b = betweenness(rnet)
rbnorm = b/mean(b)
diff_bt = pbnorm - rbnorm
res = permuteBetweeness(pdata,rdata,min_sparsity)
x = seq(1,dim(pcorr)[2])
maxY = max(max(res$uci),max(diff_bt))
minY = min(min(res$lci),min(diff_bt))
plot(x, res$m, ylim=c(minY, maxY),ylab='Diff Betweenness',xaxt='n',xlab='')
axis(1, at=x, lab=colnames(pcorr), las=2)
arrows(x, res$uci, x, res$lci, angle=90, code=3, length=.1)
points(x, diff_bt, pch=15, col='red')
title('Changes in Betweenness')

#### Tables 2 and 3 ####
thresh = 1.5
print(sprintf('Hub regions (b>%.2f) for %s', thresh, 'Persistent'))
cat('Region\tNormBi\tDegree\n')
nhubs = sum(pbnorm>thresh)
sb = sort(pbnorm, index.return=T, decreasing=T)
d = degree(pnet)
for (i in 1:nhubs) {
    cat(sprintf("%s\t%.2f\t%d\n", colnames(pcorr)[sb$ix[i]], sb$x[i], d[sb$ix[i]]))
}
print(sprintf('Hub regions (b>%.2f) for %s', thresh, 'Remission'))
cat('Region\tNormBi\tDegree\n')
nhubs = sum(rbnorm>thresh)
sb = sort(rbnorm, index.return=T, decreasing=T)
d = degree(rnet)
for (i in 1:nhubs) {
    cat(sprintf("%s\t%.2f\t%d\n", colnames(rcorr)[sb$ix[i]], sb$x[i], d[sb$ix[i]]))
}