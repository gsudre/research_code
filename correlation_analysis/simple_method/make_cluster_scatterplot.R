# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
my_roi = clusters==5  # get this from separate_other_rois_per_group.R
cor = rowSums(cortexR[,my_roi])
other_roi = which(rowSums(bes[,my_roi])>0)
tha = rowSums(thalamusR[,other_roi])


# par(mfrow=c(2,3))
# for (g in c('NV', 'persistent', 'remission')) {
#     idx = group==g
#     plot(age[idx], tha[idx], ylab='thalamus', xlab='age')
#     abline(lm(tha[idx] ~ age[idx]), col="red")
#     title(g)
# }
# for (g in c('NV', 'persistent', 'remission')) {
#     idx = group==g
#     plot(age[idx], cor[idx], ylab='cortex', xlab='age')
#     abline(lm(cor[idx] ~ age[idx]), col="red")
#     fit = lm(cor[idx] ~ tha[idx])
#     title(sprintf('r=%.2f; t=%.2f', cor.test(tha[idx],cor[idx])$estimate,
#                   summary(fit)$coefficients[2,3]))
# }

rs = vector()
par(mfrow=c(1,3))
for (g in c('NV', 'persistent', 'remission')) {
    idx = group==g
    x = tha[idx]
    x = x[seq(2,length(x),2)] - x[seq(1,length(x),2)]
    y = cor[idx]
    y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
    plot(x, y, xlab='Thalamus SA difference (mm2)',
         ylab='Cortex SA difference (mm2)')
    fit = lm(y ~ x)
    abline(fit, col="red")
    my_r = cor.test(y,x)$estimate
    title(sprintf('%s; r=%.2f; t=%.2f', g, my_r, summary(fit)$coefficients[2,3]))
    rs = c(rs, my_r)
}

get_pval_from_Rs <- function(r1, n1, r2, n2) {
    b1 = 1/2*log((1+r1)/(1-r1))
    b2 = 1/2*log((1+r2)/(1-r2))
    z = (b1-b2)/sqrt(1/(n1-3)+1/(n2-3))
    return(2*pnorm(-abs(z)))
}

# hard coded based on group order above!!!
cat('NV VS per:', get_pval_from_Rs(rs[1],64,rs[2],32), '\n')
cat('NV VS rem:', get_pval_from_Rs(rs[1],64,rs[3],32), '\n')
cat('per VS rem:', get_pval_from_Rs(rs[2],32,rs[3],32), '\n')