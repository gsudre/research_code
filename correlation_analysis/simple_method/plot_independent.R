# plots the 1-Dice coefficient, one plot per group difference
other = 'gp'
hemi = 'R'
thresh = seq(.2,1,.1)
groups = c('remission', 'persistent', 'NV')

binarize <- function(m, t) {
    bm = m    
    bm[bm<t] = 0
    bm[bm>=t] = 1
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
        bes3 = binarize(es3,thresh[i])
        sep[i] = sum((bes1-bes2-bes3)==1)/sum(bes1==1)
    }
    return(sep)
}

par(mfrow=c(1,3))
colors = c('red','green','blue')
for (g in groups) {
    plot(thresh, getDiff(g,'baseline'), type='l', lwd=2, 
         ylab='Independence', xlab='ES threshold', ylim=c(0,1))
    for (f in 1:length(files)) {
        lines(thresh, getDiff(g,files[f]),lwd=2,col=colors[f])
    }
    title(sprintf('%s',g))
    legend('bottomright',c('baseline',files),lty=1,lwd=2,col=c('black',colors))
}