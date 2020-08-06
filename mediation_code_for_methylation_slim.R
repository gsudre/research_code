args <- commandArgs(trailingOnly = TRUE)
if (length(args) > 1) {
    fname = args[1]
    Ms = read.table(args[3])[, 1]
    Ys = read.table(args[4])[, 1]
    Xs = read.table(args[2])[, 1]
    add_Mbase = as.logical(args[5])
    cg_fname = args[6]
    out_fname = args[7]
} else {
    fname = '~/data/longitudinal_methylome/dti_2_for_sam_slim.csv'
    Ms = c('AD_left_unc_rate')
    Xs = c("cg27487187_ROC", "cg27510871_ROC")
    Ys = c("ROC_IN_one_win")
    out_fname = '~/tmp/temp1.csv'
    add_Mbase = F
    cg_fname = 'ROC_data_inattAndHI_160.csv'
}

library(mediation)

gf = read.csv(fname)
mydata = gf
# mydata$qc.bad = factor(mydata$qc.bad)

if (grepl(cg_fname, pattern='csv') {
    cg_data = read.csv(cg_fname)
} else {
    cg_data = readRDS(cg_fname)
}
cg_vars = colnames(cg_data)[grepl(colnames(cg_data), pattern='^cg') | 
                            grepl(colnames(cg_data), pattern='^ch')]
mydata = merge(mydata, cg_data, by='PersonID')
print(dim(mydata))

# make sure we have enough data in these batches
mydata[mydata$batch=='11_11', 'batch'] = 'other_batches'
mydata[mydata$batch=='3_2', 'batch'] = 'other_batches'
mydata[mydata$batch=='10_10', 'batch'] = 'other_batches'
mydata$batch = factor(mydata$batch)
mydata$sex = factor(mydata$sex)
# mydata$sample_type.y = factor(mydata$sample_type.y)
mydata$sample_type = factor(mydata$sample_type)

nboot = 2#10000
ncpus = 1 #future::availableCores() #4 # 8
# for DTI
if (any(grepl(Ys, pattern='HI'))) { 
    # neuroimaging
    fm = 'M ~ X + SXHI.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    fy = 'Y ~ X + M + SXHI.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + ageACQ.1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    
    fm = 'M ~ X + SXHI.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    fy = 'Y ~ X + M + SXHI.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + ageACQ.1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'

    # # cog
    # fm = 'M ~ X + SXHI.1 + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    # fy = 'Y ~ X + M + SXHI.1 + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + ageACQ.1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'

} else {
    fm = 'M ~ X + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    fy = 'Y ~ X + M + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    
    fm = 'M ~ X + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
    fy = 'Y ~ X + M + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + ageACQ.1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type + sex'
}
if (add_Mbase) {
    fm = sprintf('%s + m_base', fm)
    fy = sprintf('%s + m_base', fy)
}
# # for DLPFC variables
# fm = 'M ~ X + DLPFC_volume_baseline + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + age_methyl_1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.x + sex'
# fy = 'Y ~ X + M + DLPFC_volume_baseline + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + age_methyl_1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.x + sex'
# # for DLPFC variables without baseline correction
# fm = 'M ~ X + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + age_methyl_1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.x + sex'
# fy = 'Y ~ X + M + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + x_base + age_methyl_1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.x + sex'


print(fm)
print(fy)

# no need to change anything below here. The functions remove NAs and zscore
# variables on their own

run_model4 = function(X, M, Y, metadata, nboot=1000) {
    idx = is.na(X) | is.na(Y) | is.na(M)
    Y = Y[!idx]
    Y = scale(Y)
    run_data = as.data.frame(metadata[!idx, ])
    # needed to get rid of extra attributes from scaling
    run_data$X = as.numeric(scale(X[!idx]))
    run_data$M = as.numeric(scale(M[!idx]))
    run_data$Y = as.numeric(Y)

    model.M <- lm(as.formula(fm), data=run_data)
    model.Y <- lm(as.formula(fy), data=run_data)
    
    results <- mediate(model.M, model.Y, treat='X', mediator='M', boot=T,
                        sims=nboot, boot.ci.type='bca', ncpus=ncpus)
    
    res = c(results$mediator, results$nobs, results$tau.coef, results$tau.p, 
            results$d.avg, results$d.avg.p,
            results$z.avg, results$z.avg.p, results$n.avg, results$n.avg.p, results$tau.ci[1], results$tau.ci[2],
            results$d.avg.ci[1], results$d.avg.ci[2], results$z.avg.ci[1],
            results$z.avg.ci[2], results$n.avg.ci[1], results$n.avg.ci[2])
    names(res) = c('M', 'nobs', 'tot', 'tot_p', 'acme', 'acme_p', 'ade',
                    'ade_p', 'prop', 'prop_p',
                    'tot_2p5ci', 'tot_97p5ci', 'acme_2p5ci', 'acme_97p5ci', 'ade_2p5ci', 'ade_97p5ci', 'prop_2p5ci', 'prop_97p5ci')
    # adding regression results
    tmp = summary(model.M)$coefficients
    resX = tmp['X', ]
    names(resX) = sapply(1:4, function(x) sprintf('X_XtoM_%s', colnames(tmp)[x]))
    tmp = summary(model.Y)$coefficients
    resY = cbind(tmp['X', ], tmp['M',])
    names(resY) = c(sapply(1:4, function(x) sprintf('X_MtoY_%s', colnames(tmp)[x])),
                    sapply(1:4, function(x) sprintf('M_MtoY_%s', colnames(tmp)[x])))
    res = c(res, resX, resY)
    return(res)     
}

all_res = c()
for (x_str in Xs) {
    X = mydata[, x_str]
    # replace x_base by the baseline for the current X 
    # this hack only works because all computations done in parallel correpond to
    # the same X. If we had different X being processed in parallel, then a more
    # elegant change would be needed
    x_base = gsub(x=x_str, pattern='ROC', replacement='baseline')
    mydata$x_base = mydata[, x_base]
    for (y_str in Ys) {
        Y = mydata[, y_str]
        for (m_str in Ms) {
            if (add_Mbase) {
                mbase = gsub(x=m_str, pattern='rate', replacement='baseline')
                mydata$m_base = mydata[, mbase]
            }
            print(sprintf('X=%s, M=%s, Y=%s', x_str, m_str, y_str))
            M = mydata[, m_str]
            res = run_model4(X, M, Y, mydata, nboot)
            res$M = m_str
            res$X = x_str
            res$Y = y_str
            all_res = rbind(all_res, res)
        }
    }
}
write.csv(all_res, file=out_fname, row.names=F, quote=F)
