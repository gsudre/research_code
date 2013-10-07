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

pcor = pcorb
rcor = rcorb
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
    pnet = createNetwork(pcor, s)
    plambda[cnt] = getLambda(pnet)
    pgamma[cnt] = getGamma(pnet)
    rnet = createNetwork(rcor, s)
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
    pcc[cnt] = transitivity(createNetwork(pcor, s))
    rcc[cnt] = transitivity(createNetwork(rcor, s))
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
    papl[cnt] = average.path.length(createNetwork(pcor, s))
    rapl[cnt] = average.path.length(createNetwork(rcor, s))
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