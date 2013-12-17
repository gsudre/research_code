# Plots the results of computing independence within NV group multiple times
thresh = seq(.2,1,.1)

getCI <- function(file, other) {
    res = read.table(sprintf('~/data/results/structural_v2/perm_dists_NVOnly_%s_thalamusR%sR.txt',
                 file, other))
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

par(mfrow=c(1,2))
others = c('gp','striatum')
files = c('baseline', 'last', 'diff', 'delta')
colors = c('black','red','blue','green')
for (o in 1:length(others)) {
    plot(thresh, getCI(files[1], others[o]), type='l', lwd=2, 
         ylab='Independence', xlab='ES threshold', ylim=c(0,1), col=colors[1])
    for (i in 2:length(files)) {
        lines(thresh, getCI(files[i], others[o]), lwd=2, col=colors[i])
    }
    title(sprintf('Within NVs: thalamus2%s',others[o]))
    legend('bottomright',files,lty=1,lwd=2,col=colors)
}