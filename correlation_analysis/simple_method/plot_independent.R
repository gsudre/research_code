# plots the 1-Dice coefficient, one plot per group difference
other = 'gp'
hemi = 'R'
thresh = seq(.2,1,.1)
drawCI = F
groups = c('NVonly1','NVonly2')#c('remission', 'persistent', 'NV')

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

files = c('last','diff','delta')

getDiff <- function(g, t) {
    og = setdiff(groups,g)
    # ensures that target group is first
    cnt = 1
    for (i in c(g,og)) {
        load(sprintf('~/data/results/structural_v2/es%s_thalamus2%s_%s_%s.RData',
                     hemi, other, t, i))
        eval(parse(text=sprintf('es%d = abs(es)',cnt)))
        cnt = cnt + 1
    }
    sep = vector(mode='numeric',length=length(thresh))
    for (i in 1:length(thresh)) {
        bes1 = binarize(es1,thresh[i])
        bes2 = binarize(es2,thresh[i])
#         bes3 = binarize(es3,thresh[i])
        sep[i] = length(setdiff(which(bes1),which(bes2)))/sum(bes1)
    }
    return(sep)
}

getCI <- function(v) {
    load(sprintf('~/data/results/structural_v2/perm_dists_thalamus%s%s%s_%s',
                 hemi, other, hemi, v))
    ci = vector(mode='numeric',length=dim(perm_dist)[2])
    for (i in 1:length(ci)) {
        tmp = sort(perm_dist[,i])
        # make sure I have at least 100 non-NA permutation values
        if (length(tmp)>100) {
            ci[i] = tmp[ceiling(.95*length(tmp))]
        } else {
            ci[i] = NA
        }
    }
    return(ci)
}

par(mfrow=c(1,3))
colors = c('red','green','blue')
for (g in groups) {
    plot(thresh, getDiff(g,'baseline'), type='l', lwd=2, 
         ylab='Independence', xlab='ES threshold', ylim=c(0,1))
    if (drawCI) {
        lines(thresh,getCI('baseline'),lwd=1,lty=2,col='black')
    }
    for (f in 1:length(files)) {
        lines(thresh, getDiff(g,files[f]),lwd=2,col=colors[f])
        if (drawCI) {
            lines(thresh,getCI(files[f]),lwd=1,lty=2,col=colors[f])
        }
    }
    title(sprintf('%s',g))
    legend('bottomright',c('baseline',files),lty=1,lwd=2,col=c('black',colors))
}