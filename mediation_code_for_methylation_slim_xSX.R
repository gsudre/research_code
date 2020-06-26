# this version of the script is the same as without _xSX, but here the symptoms
# are in the X variable
args <- commandArgs(trailingOnly = TRUE)
if (length(args) > 1) {
    fname = args[1]
    Ms = read.table(args[3])[, 1]
    Ys = read.table(args[4])[, 1]
    Xs = read.table(args[2])[, 1]
    out_fname = args[5]
} else {
    fname = '~/tmp/HI_ROC_methyl_sx_dti_82.csv'
    Ms = c('RD_left_ifo')
    Ys = c('ROC_HI_one_SX_win')
    Xs = c("cg00001814_ROC", "cg00009053_ROC", "cg00019746_ROC")
    out_fname = '~/tmp/temp1.csv'
}

library(mediation)

gf = read.csv(fname)
mydata = gf
mydata$qc.bad = factor(mydata$qc.bad)
# make sure we have enough data in these batches
mydata[mydata$batch=='11_11', 'batch'] = 'other_batches'
mydata[mydata$batch=='3_2', 'batch'] = 'other_batches'
mydata[mydata$batch=='10_10', 'batch'] = 'other_batches'
mydata$batch = factor(mydata$batch)
mydata$sex = factor(mydata$sex)

nboot = 1000
ncpus = 1 #future::availableCores() #4 # 8
if (any(grepl(Xs, pattern='HI'))) { 
    fm = 'M ~ X + SXHI.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + m_base + age_methyl1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.y + sex'
    fy = 'Y ~ X + M + SXHI.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + m_base + age_methyl1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.y + sex'
} else {
    fm = 'M ~ X + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + m_base + age_methyl1 + age.diff + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.y + sex'
    fy = 'Y ~ X + M + SXIN.1 + qc.bad + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + m_base + age_methyl1 + age.diff +CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sample_type.y + sex'
}

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
    return(res)     
}

all_res = c()
for (y_str in Ys) {
    Y = mydata[, y_str]
    y_base = gsub(x=y_str, pattern='ROC', replacement='baseline')
    mydata$m_base = mydata[, y_base]
    for (x_str in xs) {
        X = mydata[, x_str]
        for (m_str in Ms) {
            M = mydata[, m_str]
            print(sprintf('X=%s, M=%s, Y=%s', x_str, m_str, y_str))
            res = run_model4(X, M, Y, mydata, nboot)
            res$M = m_str
            res$X = x_str
            res$Y = y_str
            all_res = rbind(all_res, res)
        }
    }
}
write.csv(all_res, file=out_fname, row.names=F, quote=F)
