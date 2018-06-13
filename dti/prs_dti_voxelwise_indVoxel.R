# runs mediation for each voxel individually. Arguments are voxel name then DTI type

imuser=Sys.getenv('USER')
args <- commandArgs(trailingOnly = TRUE)

mydata<-read.csv(sprintf('/scratch/%s/prs/dti_prs_06122018.csv', imuser))

load(sprintf('/scratch/%s/prs/dti_%s_voxelwise_05152018.RData', imuser, args[2]))

dim(mydata)
dim(m)
mydata = merge(mydata, m, by="MRN")
mydata$motion = as.numeric((scale(mydata$norm_trans) + scale(mydata$norm_rot))/2)
dim(mydata)


# choosing mediators
m_str = args[1]
Xs = c('PROFILES.0.01.profile','PROFILES.0.05.profile', 'PROFILES.0.1.profile', 'PROFILES.0.2.profile',
       'PROFILES.0.3.profile', 'PROFILES.0.4.profile', 'PROFILES.0.5.profile')
Ys = c('SX_HI_checked', 'SX_inatt_checked', 'SX_total_checked')

nboot = 1000
mixed = T
dir_root = sprintf('/scratch/%s/prs/dti_voxels_%s_352_wnhaa_famID_lme_1kg9_residuals_checked',
                    imuser, args[2])

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
                        FAMID = data2[!idx,]$famID,
                        age= data2[!idx,]$age_at_scan,
                        sex = data2[!idx,]$Sex,
                        motion = data2[!idx,]$motion)
  
  if (!is.na(run_data[1,]$FAMID)) {
    library(lme4)
    fm = as.formula('M ~ X + (1|FAMID)')
    fy = as.formula('Y ~ X + M + (1|FAMID)')
    model.M <- lmer(fm, data=run_data)
    if (imdiscrete) {
      model.Y <- glmer(fy, data=run_data, family=binomial(link='logit'))
    } else {
      model.Y <- lmer(fy, data=run_data)
    }
    results <- mediate(model.M, model.Y, treat='X', mediator='M', boot=F, sims=nboot)
  } else {
    fm = as.formula('M ~ X')
    fy = as.formula('Y ~ X + M')
    model.M <- lm(fm, data=run_data)
    if (imdiscrete) {
      model.Y <- glm(fy, data=run_data, family=binomial(link='logit'))
    } else {
      model.Y <- lm(fy, data=run_data)
    }
    results <- mediate(model.M, model.Y, treat='X', mediator='M', boot=T, sims=nboot, boot.ci.type='bca')
  }
  
  if (short) {
res = c(results$nobs, results$tau.coef, results$tau.p, results$d.avg, results$d.avg.p,
            results$z.avg, results$z.avg.p, results$n.avg, results$n.avg.p, results$tau.ci[1], results$tau.ci[2],
            results$d.avg.ci[1], results$d.avg.ci[2], results$z.avg.ci[1], results$z.avg.ci[2], results$n.avg.ci[1], results$n.avg.ci[2])
    names(res) = c('nobs', 'tot', 'tot_p', 'acme', 'acme_p', 'ade', 'ade_p', 'prop', 'prop_p',
                   'tot_2p5ci', 'tot_97p5ci', 'acme_2p5ci', 'acme_97p5ci', 'ade_2p5ci', 'ade_97p5ci', 'prop_2p5ci', 'prop_97p5ci')
    return(res)     
  } else {
    return(results)
  }
}

if (!mixed) {
  mydata$famID = NA
}

dir.create(dir_root, showWarnings = FALSE)
for (x_str in Xs) {
  dir.create(file.path(dir_root, x_str), showWarnings = FALSE)
  X = mydata[, x_str]
  for (y_str in Ys) {
    dir.create(file.path(sprintf('%s/%s', dir_root, x_str), y_str), showWarnings = FALSE)
    Y = mydata[, y_str]
    
    out_fname = sprintf('%s/%s/%s/%s.csv', dir_root, x_str, y_str, m_str)
    print(out_fname)
    
    all_res = run_model4(X, mydata[, m_str], Y, nboot=nboot, data2=mydata)
    
    write.csv(t(all_res), file=out_fname, row.names=F, quote=F)
  }
}


