# plots the difference of 1-Dice coefficient and NVonly data

others = c('gp','striatum','cortex')
hemi = 'L'
thresh = seq(.2,1,.1)
file = 'diff'
groups = c('remission', 'persistent', 'NV')

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

getDiff <- function(g, t, other) {
    og = setdiff(groups,g)
    # ensures that target group is first
    cnt = 1
    for (i in c(g,og)) {
        load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                     hemi, other, t, i))
        eval(parse(text=sprintf('es%d = abs(es)',cnt)))
        cnt = cnt + 1
    }
    sep = vector(mode='numeric',length=length(thresh))
    for (i in 1:length(thresh)) {
        bes1 = binarize(es1,thresh[i])
        bes2 = binarize(es2,thresh[i])
        bes3 = binarize(es3,thresh[i])
        sep[i] = length(setdiff(which(bes1),union(which(bes2),which(bes3))))/sum(bes1)
    }
    return(sep)
}

getCI <- function(v, other) {
    res = read.table(sprintf('~/data/results/simple/perm_dists_NVOnly_%s_thalamus%s%s%s.txt',
                             v, hemi, other, hemi))
    ci = vector(mode='numeric',length=dim(res)[2])
    for (i in 1:length(ci)) {
        tmp = sort(res[,i])
        # make sure I have at least 100 non-NA permutation values
        if (length(tmp)>100) {
            ci[i] = tmp[ceiling(.95*length(tmp))]
        } else {
            ci[i] = NA
        }
    }
    return(ci)
}

par(mfrow=c(1,length(others)))
for (o in others) {
    rnd_dist = getCI(file, o)
    dist = getDiff('persistent', file, o)
    y = dist-rnd_dist
    plot(thresh, y, type='l', lwd=2, ylab='Independence', xlab='ES threshold', 
         ylim=c(0,.3), col='black')
    dist = getDiff('remission', file, o)
    y = dist-rnd_dist
    lines(thresh,y,lwd=2,lty=1,col='red')
    title(sprintf('thalamus2%s (%s)', o, hemi))
    legend('topright',c('persistent','remission'),lty=1,lwd=2,col=c('black','red'))
}