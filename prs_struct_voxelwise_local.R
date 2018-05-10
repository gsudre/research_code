# runs mediation for each voxel individually
args <- commandArgs(trailingOnly = TRUE)
m_file = args[1]
local = args[2]
hemi = args[3]

if (local=='lscratch') {
  jobid=Sys.getenv('SLURM_JOBID')
  local=sprintf('/lscratch/%s/', jobid)
}

gf_fname = sprintf('%s/structSE2_prs_05042018.csv', local)
maskid_fname = sprintf('%s/struct355.txt', local)
voxel_fname = sprintf('%s/%s.volume_355.10.gzip', local, hemi)
dir_root = sprintf('%s/struct_voxels_volume_%s_355_wnhaa_famID_lme_1kg9_cov_agePlusSex', local, hemi)

mydata<-read.csv(gf_fname)

load(voxel_fname)

cnames = sapply(1:163842, function(x) sprintf('v%06d', x))
colnames(data) = cnames

Mask.ID = read.table(maskid_fname)[,1]
data = cbind(Mask.ID, data)


dim(mydata)
dim(data)
mydata = merge(mydata, data, by='Mask.ID')
dim(mydata)

# choosing mediators
# Xs = c('PROFILES.0.01.profile','PROFILES.0.05.profile', 'PROFILES.0.1.profile', 'PROFILES.0.2.profile',
#        'PROFILES.0.3.profile', 'PROFILES.0.4.profile', 'PROFILES.0.5.profile')
# Ys = c('SX_HI', 'SX_INATT', 'SX_TOTAL')
Xs = c('PROFILES.0.3.profile')
Ys = c('SX_HI')

nboot = 1000
mixed = T

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
                        age= data2[!idx,]$AGE_CLIN,
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

vox_list = read.table(m_file)[, 1]

dir.create(dir_root, showWarnings = FALSE)
for (x_str in Xs) {
  dir.create(file.path(dir_root, x_str), showWarnings = FALSE)
  X = mydata[, x_str]
  for (y_str in Ys) {
    dir.create(file.path(sprintf('%s/%s', dir_root, x_str), y_str), showWarnings = FALSE)
    Y = mydata[, y_str]
    for (m_str in vox_list) {
      out_fname = sprintf('%s/%s/%s/%s.csv', dir_root, x_str, y_str, m_str)
      print(out_fname)
      # some voxels are all zeros! give them a bad result
      if (sum(mydata[, m_str]==0) == nrow(mydata)) {
        res_names = c('nobs', 'tot', 'tot_p', 'acme', 'acme_p', 'ade', 'ade_p', 'prop', 'prop_p',
                   'tot_2p5ci', 'tot_97p5ci', 'acme_2p5ci', 'acme_97p5ci', 'ade_2p5ci', 'ade_97p5ci', 'prop_2p5ci', 'prop_97p5ci')
        all_res = rep(1, length(res_names))
        names(all_res) = res_names    
      } else {
        all_res = run_model4(X, mydata[, m_str], Y, nboot=nboot, data2=mydata)
      }
      write.csv(t(all_res), file=out_fname, row.names=F, quote=F)
    }
  }
}


