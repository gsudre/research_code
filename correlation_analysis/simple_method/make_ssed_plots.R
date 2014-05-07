# Makes plots of thalamus regions connected to cortical seed, 6 lines plot, and correlation plots + tests.

# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')

seed=6503
hemi='R'
g = 'persistent'

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

load(sprintf('~/data/results/simple/es%s_thalamus2cortex_diff_%s.RData',hemi, g))
es = abs(es)
bes = binarize(es,.5)
# writing what vertices in the thalamus are connected to the seed
tha_roi = bes[,seed]
fname = sprintf('~/data/results/simple/thalamus2seed%d_%s_diff_%s.txt', 
                seed, hemi, g)
write_vertices(tha_roi, fname, c(g))

rs = vector()
par(mfrow=c(1,3))
for (g in c('persistent', 'remission', 'NV')) {
    # separating the data for correlation plots
    eval(parse(text=sprintf('cor = cortex%s[,seed]', hemi)))
    eval(parse(text=sprintf('tha = rowSums(thalamus%s[,tha_roi])', hemi)))
    idx = group==g
    x = tha[idx]
    x = x[seq(2,length(x),2)] - x[seq(1,length(x),2)]
    y = cor[idx]
    y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
    plot(x, y, xlab='Thalamus SA difference (mm2)',
         ylab='Cortex SA difference (mm2)')
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

# # setting up for line plot
# pdata <- expand.grid(age=seq(min(age), max(age), by=1), group=levels(group))
# y=scale(tha)
# fit = lme(y~group*age, random=~1|subject)
# plot(age,y,col='black',xlab='Age',ylab='SA z-score')
# pred <- predict(fit, pdata, level = 0)
# lines(pdata$age[pdata$group=='NV'], pred[pdata$group=='NV'], col="green",lwd=4)
# lines(pdata$age[pdata$group=='persistent'], pred[pdata$group=='persistent'], col="red",lwd=4)
# lines(pdata$age[pdata$group=='remission'], pred[pdata$group=='remission'], col="blue",lwd=4)
# y=scale(cor)
# fit = lme(y~group*age, random=~1|subject)
# points(age,y,col='black',pch=0)
# pred <- predict(fit, pdata, level = 0)
# lines(pdata$age[pdata$group=='NV'], pred[pdata$group=='NV'], col="green",lwd=4,lty=3)
# lines(pdata$age[pdata$group=='persistent'], pred[pdata$group=='persistent'], col="red",lwd=4, lty=3)
# lines(pdata$age[pdata$group=='remission'], pred[pdata$group=='remission'], col="blue",lwd=4, lty=3)
# title('solid=thalamus, dashed=cortex')
# legend("bottomright", c('NV','persistent','remission'), cex=0.8, col=c("green","red",'blue'), lty=1, lwd=2, bty="n")