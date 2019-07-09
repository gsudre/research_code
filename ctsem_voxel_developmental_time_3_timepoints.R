# Runs ctsem for voxels
#
# Usage: Rscript ctsem_loop.R data_fname sx1 phen_list_file out_fname
# 
# GS. 07/2019
library(ctsem)

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
s = args[2]
phen_fname = args[3]
out_fname = args[4]

# TIs = c('TI1')
TIs = c('TI1', 'TI2')

### DONE DECLARING VARIABLES

load(data_fname)
phen = as.character(read.table(phen_fname)[,1])
out_res = c()
for (p in phen) {
    cat(sprintf('Running %s and %s\n', s, p))
    myctmodel = ctModel(n.latent=2, n.manifest=2, Tpoints=4, n.TIpred=2,
                        manifestNames=c(s, p), latentNames=c(s, p),
                        TIpredNames=TIs,LAMBDA=diag(2))
    cols = c(sprintf('%s_T0', s), sprintf('%s_T0', p),
                sprintf('%s_T1', s), sprintf('%s_T1', p),
                sprintf('%s_T2', s), sprintf('%s_T2', p),
                sprintf('%s_T3', s), sprintf('%s_T3', p),
                'dT1', 'dT2', 'dT3', TIs)
    print(cols)
    fit = ctFit(dat=wider_resids_motion[, cols], ctmodelobj=myctmodel)
    cis = ctCI(fit, confidenceintervals='DRIFT')
    # storing results
    res = summary(fit)
    b = summary(cis)$omxsummary$CI
    b$note=NULL
    b$StdError=NA
    # grabbing SE from different table of results
    for (r in rownames(b)) {
        idx = rownames(res$ctparameters)==r
        b[r, 'StdError'] = res$ctparameters[idx, 'StdError']
    }
    b = rbind(b, c(NA, res$omxsummary$BIC.Mx, NA, NA))
    b = rbind(b, c(NA, res$omxsummary$AIC.Mx, NA, NA))
    b = rbind(b, c(NA, res$omxsummary$npsolMessage, NA, NA))
    rownames(b)[5:7] = c('BIC', 'AIC', 'msg')
    b$var = rownames(b)
    b$sx = s
    b$phen = p
    out_res = rbind(out_res, b)
}
write.csv(out_res, file=out_fname, row.names=F)
