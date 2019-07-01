# Runs ctsem for a group of variables
#
# Usage: Rscript ctsem_loop.R [sx1 phen1 out_fname]
# if arguments are specified, script runs those. IF nothing, it runs what's in
# the code
# 
# GS. 07/2019
library(ctsem)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) > 0) {
    sx = c(args[1])
    phen = c(args[2])
    out_fname = args[3]
} else {
    # assuming that T0..T2 variables start with these names
    sx = c('SX_HI', 'SX_inatt')#, 'SX_total')
    phen = c('fa_lcst', 'ixi_ADC_left_cst')
    ys = sapply(5:46, function(x) sprintf('Y%d', x))
    phen = c(phen, ys)
    out_fname = '~/tmp/T1_out.csv'
}

data_fname = '/lscratch/$SLURM_JOBID/wider_devel_names.csv'
TIs = c('TI1')

### DONE DECLARING VARIABLES

data = read.csv(data_fname, T)
for (t in 0:2) {
    data[, sprintf('SX_total_T%d', t)] = data[, sprintf('SX_inatt_T%d', t)] +
                                         data[, sprintf('SX_HI_T%d', t)]
}
out_res = c()
for (s in sx) {
    for (p in phen) {
        cat(sprintf('Running %s and %s\n', s, p))
        myctmodel = ctModel(n.latent=2, n.manifest=2, Tpoints=3, n.TIpred=1,
                            manifestNames=c(s, p), latentNames=c(s, p),
                            TIpredNames=TIs,LAMBDA=diag(2))
        cols = c(sprintf('%s_T0', s), sprintf('%s_T0', p),
                 sprintf('%s_T1', s), sprintf('%s_T1', p),
                 sprintf('%s_T2', s), sprintf('%s_T2', p),
                 'dT1', 'dT2', TIs)
        print(cols)
        fit = ctFit(dat=data[, cols], ctmodelobj=myctmodel)
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
        rownames(b)[5:6] = c('BIC', 'AIC')
        b$var = rownames(b)
        b$sx = s
        b$phen = p
        out_res = rbind(out_res, b)
    }
}
write.csv(out_res, file=out_fname, row.names=F)
