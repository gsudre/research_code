mydata<-read.csv('/scratch/sudregp/prs/wnh_aa_jhu_tract2_pca_03262018.csv')

load('/scratch/sudregp/prs/dti_fa_voxelwise_08162017.RData')

dim(mydata)
dim(m)
mydata = merge(mydata, m, by="MRN")
dim(mydata)

args <- commandArgs(trailingOnly = TRUE)

# choosing mediators
Ms = c(which(colnames(mydata) == args[1]))
Xs = c('PROFILES.0.01.profile','PROFILES.0.05.profile', 'PROFILES.0.1.profile', 'PROFILES.0.2.profile',
       'PROFILES.0.3.profile', 'PROFILES.0.4.profile', 'PROFILES.0.5.profile')
Ys = c('SX_HI', 'SX_inatt')

nboot = 1000
ncpus = 2
mixed = T
fname_root = 'dti_voxels_fa_wnhaa_%s_extendedfamID_lme_1kg9_cov_age+sex_%s_264_1k.csv'

# no need to change anything below here. The functions remove NAs and zscore variables on their own
run_model4 = function(X, M, Y, nboot=1000, short=T, data2) {
  library(mediation)
  idx = is.na(X) | is.na(Y) | is.na(M)
  Y = Y[!idx]
  imdiscrete = T
  if (!is.factor(Y)) {
    Y = scale(Y)
    imdiscrete = F
  }
  run_data = data.frame(X = scale(X[!idx]),
                        Y = Y,
                        M = scale(M[!idx]),
                        FAMID = data2[!idx,]$extendedFamID,
                        age= data2[!idx,]$AGE,
                        sex = data2[!idx,]$Sex)
  
  if (!is.na(run_data[1,]$FAMID)) {
    library(lme4)
    fm = as.formula('M ~ X + age + sex + (1|FAMID)')
    fy = as.formula('Y ~ X + M + age + sex + (1|FAMID)')
    model.M <- lmer(fm, data=run_data)
    if (imdiscrete) {
      model.Y <- glmer(fy, data=run_data, family=binomial(link='logit'))
    } else {
      model.Y <- lmer(fy, data=run_data)
    }
    results <- mediate(model.M, model.Y, treat='X', mediator='M', boot=F, sims=nboot)
  } else {
    fm = as.formula('M ~ X + age + sex')
    fy = as.formula('Y ~ X + M + age + sex')
    model.M <- lm(fm, data=run_data)
    if (imdiscrete) {
      model.Y <- glm(fy, data=run_data, family=binomial(link='logit'))
    } else {
      model.Y <- lm(fy, data=run_data)
    }
    results <- mediate(model.M, model.Y, treat='X', mediator='M', boot=T, sims=nboot, boot.ci.type='bca')
  }
  
  if (short) {
res = c(results$mediator, results$nobs, results$tau.coef, results$tau.p, results$d.avg, results$d.avg.p,
            results$z.avg, results$z.avg.p, results$n.avg, results$n.avg.p, results$tau.ci[1], results$tau.ci[2],
            results$d.avg.ci[1], results$d.avg.ci[2], results$z.avg.ci[1], results$z.avg.ci[2], results$n.avg.ci[1], results$n.avg.ci[2])
    names(res) = c('M', 'nobs', 'tot', 'tot_p', 'acme', 'acme_p', 'ade', 'ade_p', 'prop', 'prop_p',
                   'tot_2p5ci', 'tot_97p5ci', 'acme_2p5ci', 'acme_97p5ci', 'ade_2p5ci', 'ade_97p5ci', 'prop_2p5ci', 'prop_97p5ci')
    return(res)     
  } else {
    return(results)
  }
}

run_wrapper = function(m, run_model, mydata, nboot, X, Y) {
  cat('\t', sprintf('M=%s', colnames(mydata)[m]), '\n')
  tmp = run_model(X, mydata[, m], Y, nboot=nboot, data2=mydata)
  tmp$M = colnames(mydata)[m]
  return(tmp)
}

if (!mixed) {
  mydata$NuclearFamID = NA
}

for (x_str in Xs) {
  for (y_str in Ys) {
    X = mydata[, x_str]
    Y = mydata[, y_str]
    out_fname = sprintf(fname_root,
                        y_str, x_str)
    print(out_fname)
    
    if (ncpus > 1) {
      library(parallel)
      cl <- makeCluster(ncpus)
      m1_res = parLapply(cl, Ms, run_wrapper, run_model4, mydata, nboot, X, Y)
      stopCluster(cl)
    } else {
      m1_res = lapply(Ms, run_wrapper, run_model4, mydata, nboot, X, Y)
    }
    all_res = do.call(rbind, m1_res)
    
    write.csv(all_res, file=out_fname, row.names=F)
  }
}


