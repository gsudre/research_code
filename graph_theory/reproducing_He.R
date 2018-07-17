# Reproducing the analysis outlined in He, Chen, Evans - 2008 - Structural insights into aberrant topological patterns of large-scale cortical networks in Alzheimer's disease
#
# GS, 07/2018, revising version from 10/2013
#

gf1_fname = '~/tmp/gf_low_roi.csv'
gf2_fname = '~/tmp/gf_high_roi.csv'

data1 = read.csv(gf1_fname)[,2:57]
data2 = read.csv(gf2_fname)[,2:57]

gtitle1 = 'Low'
gtitle2 = 'High'

# when delta==T, data1=G1B, data2=G2B, data3=G1L, data4=G2L, so that delta1=data3-data1
delta = F
# data3 = pmatl
# data4 = rmatl
sparsity = seq(.06,.2,.02)

# permutations for lambda and gamma
num_perms = 10
# permutations for statistics
nperms = 50




library(ppcor)
corr1 = pcor(data1)$estimate
corr2 = pcor(data2)$estimate

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

permuteDeltaMetric <- function(data1B, data2B, data1L, data2L, sparsity, fun) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    all_dataB = rbind(data1B, data2B)
    all_dataL = rbind(data1L, data2L)
    n1 = dim(data1B)[1]
    n2 = dim(data2B)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(n1+n2, replace = FALSE)
        perm_dataB <- all_dataB[perm_labels, ]
        perm_dataL <- all_dataL[perm_labels, ]
        pmat1b = perm_dataB[1:n1, ]
        pmat2b = perm_dataB[(n1+1):(n1+n2), ]
        pmat1l = perm_dataL[1:n1, ]
        pmat2l = perm_dataL[(n1+1):(n1+n2), ]
        cor1b = pcor(pmat1b)$estimate
        cor2b = pcor(pmat2b)$estimate
        cor1l = pcor(pmat1l)$estimate
        cor2l = pcor(pmat2l)$estimate
        deltaCor1 = cor1l - cor1b
        deltaCor2 = cor2l - cor2b
        net1 = createNetwork(deltaCor1, sparsity)
        net2 = createNetwork(deltaCor2, sparsity)
        ds[i] = fun(net1) - fun(net2)
    }
    ds = sort(ds)
    res = list(m=mean(ds),lci=ds[floor(.025*nperms)],uci=ds[floor(.975*nperms)])
    return(res)
}

permuteBetweeness <- function(data1, data2, sparsity) 
{
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

permuteDeltaBetweeness <- function(data1B, data2B, data1L, data2L, sparsity) 
{
    nrois = dim(data1)[2]
    ds <- matrix(nrow=nperms,ncol=nrois) 
    all_dataB = rbind(data1B, data2B)
    all_dataL = rbind(data1L, data2L)
    n1 = dim(data1B)[1]
    n2 = dim(data2B)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(n1+n2, replace = FALSE)
        perm_dataB <- all_dataB[perm_labels, ]
        perm_dataL <- all_dataL[perm_labels, ]
        pmat1b = perm_dataB[1:n1, ]
        pmat2b = perm_dataB[(n1+1):(n1+n2), ]
        pmat1l = perm_dataL[1:n1, ]
        pmat2l = perm_dataL[(n1+1):(n1+n2), ]
        cor1b = pcor(pmat1b)$estimate
        cor2b = pcor(pmat2b)$estimate
        cor1l = pcor(pmat1l)$estimate
        cor2l = pcor(pmat2l)$estimate
        deltaCor1 = cor1l - cor1b
        deltaCor2 = cor2l - cor2b
        net1 = createNetwork(deltaCor1, sparsity)
        net2 = createNetwork(deltaCor2, sparsity)
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

#### Generating figure 2
lambda1 = vector(length=length(sparsity))
lambda2 = vector(length=length(sparsity))
gamma1 = vector(length=length(sparsity))
gamma2 = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    net1 = createNetwork(corr1, s)
    lambda1[cnt] = getLambda(net1)
    gamma1[cnt] = getGamma(net1)
    net2 = createNetwork(corr2, s)
    lambda2[cnt] = getLambda(net2)
    gamma2[cnt] = getGamma(net2)
    cnt = cnt + 1
}
dev.new()
maxY = max(ceiling(max(gamma1,na.rm=T)),ceiling(max(gamma2,na.rm=T)))
par(mfrow=c(1,2))
plot(sparsity, lambda1, type="l", col='black', ylim=c(0, maxY), lwd=2)
lines(sparsity, gamma1, type="l", col='grey', lwd=2)
legend('topright', c('Lambda', 'Gamma'), col=c('black','grey'), lwd=2)
title('Small-Worldness, Persistent')
plot(sparsity, lambda2, type="l", col='black', ylim=c(0, maxY), lwd=2)
lines(sparsity, gamma2, type="l", col='grey', lwd=2)
legend('topright', c('Lambda', 'Gamma'), col=c('black','grey'), lwd=2)
title('Small-Worldness, Remission')
# reconfigure sparsity to keep sigma > 1
sigma1 = gamma1/lambda1
sigma2 = gamma2/lambda2
sparsity = sparsity[sigma1>0 & sigma2>0 & !is.na(sigma1) & !is.na(sigma2)]

#### Figure 3A ####
cc1 = vector(length=length(sparsity))
cc2 = vector(length=length(sparsity))
lcicc = vector(length=length(sparsity))
ucicc = vector(length=length(sparsity))
nullcc = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    print(sprintf('Working on sparsity %.2f', s))
    cc1[cnt] = transitivity(createNetwork(corr1, s))
    cc2[cnt] = transitivity(createNetwork(corr2, s))
    if (delta) {
        perm = permuteDeltaMetric(data1,data2,data3,data4,s,transitivity)
    } else {
        perm = permuteMetric(data1,data2,s,transitivity)
    }
    nullcc[cnt] = perm$m
    ucicc[cnt] = perm$uci
    lcicc[cnt] = perm$lci
    cnt = cnt + 1
}
diff_cc = cc1-cc2
maxY = max(max(cc2),max(cc1))
dev.new()
par(mfrow=c(1,2))
plot(sparsity, cc1, type="l", col='black', ylab='Cp', ylim=c(0, maxY), lwd=2)
lines(sparsity, cc2, type="l", col='grey', lwd=2)
legend('bottomright', c(gtitle1, gtitle2), col=c('black','grey'), lwd=2)
title('Mean Clustering Coefficient')
maxY = max(max(ucicc),max(diff_cc))
minY = min(min(lcicc),min(diff_cc))
plot(sparsity, diff_cc, type="o", ylab='Diff Cp', col='red', ylim=c(minY, maxY), lwd=2)
lines(sparsity, nullcc, type="o", col='grey', lwd=2)
lines(sparsity, lcicc, type="l", col='grey', lwd=2)
lines(sparsity, ucicc, type="l", col='grey', lwd=2)
title('Difference')

#### Figure 3B ####
apl1 = vector(length=length(sparsity))
apl2 = vector(length=length(sparsity))
lciapl = vector(length=length(sparsity))
uciapl = vector(length=length(sparsity))
nullapl = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    print(sprintf('Working on sparsity %.2f', s))
    apl1[cnt] = average.path.length(createNetwork(corr1, s))
    apl2[cnt] = average.path.length(createNetwork(corr2, s))
    if (delta) {
        perm = permuteDeltaMetric(data1,data2,data3,data4,s,average.path.length)
    } else {
        perm = permuteMetric(data1,data2,s,average.path.length)
    }
    nullapl[cnt] = perm$m
    uciapl[cnt] = perm$uci
    lciapl[cnt] = perm$lci
    cnt = cnt + 1
}
diff_apl = apl1-apl2
maxY = max(max(apl2),max(apl1))
dev.new()
par(mfrow=c(1,2))
plot(sparsity, apl1, type="l", col='black', ylab='Cp', ylim=c(0, maxY), lwd=2)
lines(sparsity, apl2, type="l", col='grey', lwd=2)
legend('bottomright', c(gtitle1, gtitle2), col=c('black','grey'), lwd=2)
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
dev.new()
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
if (!delta) {
    thresh = .05
    pval_connections = getPval(corr1, corr2, dim(data1)[1], dim(data2)[1])
    pval_connections = pval_connections[upper.tri(pval_connections)]
    pval_connections = p.adjust(pval_connections, method='fdr')
    good_pvals = pval_connections < thresh
    num_good_pvals = sum(good_pvals)
    print(sprintf('Total of significant differences: %d', sum(good_pvals)))
    if (num_good_pvals > 0) {
        pvals1 = pcor(data1)$p.value
        pvals2 = pcor(data2)$p.value
        pvals1 = pvals1[upper.tri(pvals1)]
        pvals2 = pvals2[upper.tri(pvals2)]
        pvals1 = p.adjust(pvals1, method='fdr')
        pvals2 = p.adjust(pvals2, method='fdr')
        good_pvals1 = pvals1 < thresh
        good_pvals2 = pvals2 < thresh
        very_good_pvals = good_pvals & (good_pvals1 | good_pvals2)
        nrows = sum(very_good_pvals)
        print(sprintf('Significant differences with significant Rs: %d', nrows))
        if (nrows > 0) {
            pvals2list = pval_connections[very_good_pvals]
            corr12list = corr1[upper.tri(corr1)][very_good_pvals]
            corr22list = corr2[upper.tri(corr2)][very_good_pvals]
            cat('ROI1\t\t\t\t\t\t\t\tROI2\t\t\t\t\t\t\tPersistent\t\t\tRemission\t\t\tDiff pval\n')
            for (i in 1:nrows) {
                idx = which(corr1==corr12list[i] & corr2==corr22list[i], arr.ind=TRUE)
                cat(sprintf("%s\t\t\t%s\t\t\t%.2f\t\t\t%.2f\t\t\t%.3f\n",
                            colnames(corr1)[idx[1]],colnames(corr1)[idx[2]],
                              corr12list[i],corr22list[i],pvals2list[i]))
            }
        }
    }
}

#### Figure 5 ####
max1 = vector(length=length(sparsity))
max2 = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    max1[cnt] = max(clusters(createNetwork(corr1, s))$csize)
    max2[cnt] = max(clusters(createNetwork(corr2, s))$csize)
    cnt = cnt + 1
}
dev.new()
plot(sparsity,max1,type='l',lwd=2,col='black',ylim=c(5,dim(corr1)[1]+2),ylab='Size of largest component')
lines(sparsity,max2,type='l',lwd=2,col='grey')
legend('bottomright', c(gtitle1, gtitle2), col=c('black','grey'), lwd=2)
print('Lowest sparsity threshold in which both of the networks included all connected nodes:')
min_sparsity = min(sparsity[max1==dim(corr1)[1] & max2==dim(corr1)[1]])
print(min_sparsity)

#### Figure 6A ####
net1 = createNetwork(corr1, min_sparsity)
b = betweenness(net1)
bnorm1 = b/mean(b)
net2 = createNetwork(corr2, min_sparsity)
b = betweenness(net2)
bnorm2 = b/mean(b)
diff_bt = bnorm1 - bnorm2
if (delta) {
    res = permuteDeltaBetweeness(data1,data2,data3,data4,min_sparsity)
} else {
    res = permuteBetweeness(data1,data2,min_sparsity)
}
x = seq(1,dim(corr1)[2])
maxY = max(max(res$uci),max(diff_bt))
minY = min(min(res$lci),min(diff_bt))
dev.new()
plot(x, res$m, ylim=c(minY, maxY),ylab='Diff Betweenness',xaxt='n',xlab='')
axis(1, at=x, lab=colnames(corr1), las=2)
arrows(x, res$uci, x, res$lci, angle=90, code=3, length=.1)
points(x, diff_bt, pch=15, col='red')
title('Changes in Betweenness')

#### Tables 2 and 3 ####
thresh = 1.5
print(sprintf('Hub regions (b>%.2f) for %s', thresh, gtitle1))
cat('Region\tNormBi\tDegree\n')
nhubs = sum(bnorm1>thresh)
sb = sort(bnorm1, index.return=T, decreasing=T)
d = degree(net1)
for (i in 1:nhubs) {
    cat(sprintf("%s\t%.2f\t%d\n", colnames(corr1)[sb$ix[i]], sb$x[i], d[sb$ix[i]]))
}
print(sprintf('Hub regions (b>%.2f) for %s', thresh, gtitle2))
cat('Region\tNormBi\tDegree\n')
nhubs = sum(bnorm2>thresh)
sb = sort(bnorm2, index.return=T, decreasing=T)
d = degree(net2)
for (i in 1:nhubs) {
    cat(sprintf("%s\t%.2f\t%d\n", colnames(corr2)[sb$ix[i]], sb$x[i], d[sb$ix[i]]))
}
