# runs mediation for each voxel individually

mydata<-read.csv('/scratch/sudregp/prs/dti_wnhaa_304_03272018.csv')

load('/scratch/sudregp/prs/dti_rd_voxelwise_08162017.RData')

dim(mydata)
dim(m)
mydata = merge(mydata, m, by="MRN")
dim(mydata)

# syntax is x_str, y_str, voxel, seed
args <- commandArgs(trailingOnly = TRUE)

# choosing mediators
x_str = args[1]
y_str = args[2]
m_str = args[3]
myseed = args[4]

nboot = 1000
mixed = T
dir_root = '/scratch/sudregp/prs/dti_voxels_rd_wnhaa_extendedfamID_lme_1kg9_cov_agePlusSex'

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
  mydata$NuclearFamID = NA
}

# shuffle mydata around
set.seed(as.integer(myseed) %% 2^31)
perm_labels <- sample.int(dim(mydata)[1], replace = FALSE)
mydata = mydata[perm_labels, ]
print(perm_labels[1:10])

dir.create(dir_root, showWarnings = FALSE)
dir_name = sprintf('%s/%s', dir_root, x_str)
dir.create(dir_name, showWarnings = FALSE)
X = mydata[, x_str]
dir_name = sprintf('%s/%s/%s', dir_root, x_str, y_str)
dir.create(dir_name, showWarnings = FALSE)
Y = mydata[, y_str]
dir_name = sprintf('%s/%s/%s/perm%s', dir_root, x_str, y_str, myseed)
dir.create(dir_name, showWarnings = FALSE)
out_fname = sprintf('%s/%s.csv', dir_name, m_str)
print(out_fname)

all_res = run_model4(X, mydata[, m_str], Y, nboot=nboot, data2=mydata)

write.csv(t(all_res), file=out_fname, row.names=F, quote=F)
