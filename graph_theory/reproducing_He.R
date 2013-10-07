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

pdata = pcorb
rdata = rcorb
sparsity = seq(.06,.4,.02)

#### Generating figure 2
plambda = vector(length=length(sparsity))
rlambda = vector(length=length(sparsity))
pgamma = vector(length=length(sparsity))
rgamma = vector(length=length(sparsity))
cnt=1
for (s in sparsity) {
    pnet = createNetwork(pdata, s)
    plambda[cnt] = getLambda(pnet)
    pgamma[cnt] = getGamma(pnet)
    rnet = createNetwork(rdata, s)
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
