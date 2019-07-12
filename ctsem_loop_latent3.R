# Runs ctsem for a group of variables
#
# Usage: Rscript ctsem_loop_latent3.R [data_fname sx1 phen1 cog1 out_fname]
# if arguments are specified, script runs those. IF nothing, it runs what's in
# the code
# 
# GS. 07/2019
library(ctsem)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) > 0) {
    data_fname = args[1]
    sx = c(args[2])
    brain = c(args[3])
    cog = c(args[4])
    out_fname = args[5]
} else {
    data_fname = '~/Downloads/DATA_DEVEL_TIME_DTI_SX_COG_no+PII.csv'
    # assuming that T0..T2 variables start with these names
    sx = c('SX_hi')#, 'SX_inatt')
    brain = sapply(1:2, function(x) sprintf('Y%d', x)) #sapply(1:44, function(x) sprintf('Y%d', x))
    cog = sapply(45:46, function(x) sprintf('Y%d', x))
    out_fname = '~/tmp/T1_out.csv'
}

TIs = c('TI1')

### DONE DECLARING VARIABLES

data = read.csv(data_fname, T)
out_res = c()
for (s in sx) {
    for (b in brain) {
        for (g in cog) {
            # just so we can get consistent results!
            set.seed(42)
            cat(sprintf('Running %s : %s : %s\n', s, b, g))
            myctmodel = ctModel(n.latent=3, n.manifest=3, Tpoints=4,
                                n.TIpred=length(TIs), manifestNames=c(s, b, g), latentNames=c(s, b, g),
                                TIpredNames=TIs, LAMBDA=diag(3))
            cols = c(sprintf('%s_T0', s), sprintf('%s_T0', b),
                     sprintf('%s_T0', g), sprintf('%s_T1', s),
                     sprintf('%s_T1', b), sprintf('%s_T1', g),
                     sprintf('%s_T2', s), sprintf('%s_T2', b),
                     sprintf('%s_T2', g), sprintf('%s_T3', s),
                     sprintf('%s_T3', b), sprintf('%s_T3', g),
                     'dT1', 'dT2', 'dT3', TIs)
            print(cols)
            fit = ctFit(dat=data[, cols], ctmodelobj=myctmodel)
            cis = ctCI(fit, confidenceintervals='DRIFT')
            # storing results
            res = summary(fit)
            tmp = summary(cis)$omxsummary$CI
            tmp$note=NULL
            tmp$StdError=NA
            # grabbing SE from different table of results
            for (r in rownames(b)) {
                idx = rownames(res$ctparameters)==r
                tmp[r, 'StdError'] = res$ctparameters[idx, 'StdError']
            }
            tmp = rbind(tmp, c(NA, res$omxsummary$BIC.Mx, NA, NA))
            tmp = rbind(tmp, c(NA, res$omxsummary$AIC.Mx, NA, NA))
            tmp = rbind(tmp, c(NA, res$omxsummary$npsolMessage, NA, NA))
            rownames(tmp)[5:7] = c('BIC', 'AIC', 'msg')
            tmp$var = rownames(tmp)
            tmp$sx = s
            tmp$brain = b
            tmp$cog = g
            out_res = rbind(out_res, tmp)
        }
    }
}
write.csv(out_res, file=out_fname, row.names=F)
