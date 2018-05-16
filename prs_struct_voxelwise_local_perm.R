# runs mediation for each voxel individually
args <- commandArgs(trailingOnly = TRUE)
m_file = args[1]
local = args[2]
hemi = args[3]
myseed = args[4]
x_str = args[5]
y_str = args[6]

if (local=='lscratch') {
  jobid=Sys.getenv('SLURM_JOBID')
  local=sprintf('/lscratch/%s/', jobid)
}

gf_fname = sprintf('%s/structSE2_prs_05042018.csv', local)
maskid_fname = sprintf('%s/struct355.txt', local)
voxel_fname = sprintf('%s/%s.volume_residuals_355.10.gzip', local, hemi)
dir_root = sprintf('%s/struct_voxels_volume_%s_355_wnhaa_famID_lme_1kg9_residuals', local, hemi)

mydata<-read.csv(gf_fname)

load(voxel_fname)

cnames = sapply(1:163842, function(x) sprintf('v%06d', x))
colnames(data) = cnames

maskid = read.table(maskid_fname)[,1]
data = cbind(maskid, data)


dim(mydata)
dim(data)
mydata = merge(mydata, data, by='maskid')
mydata$SX_TOTAL = mydata$SX_INATT + mydata$SX_HI
dim(mydata)

# choosing mediators

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
                        FAMID = data2[!idx,]$extendedFamID,
                        age= data2[!idx,]$AGE_CLIN,
                        sex = data2[!idx,]$Sex)
  
  if (!is.na(run_data[1,]$FAMID)) {
    library(lme4)
    fm = as.formula('M ~ X + age(1|FAMID)')
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
  mydata$NuclearFamID = NA
}

dir.create(dir_root, showWarnings = FALSE)
dir_name = sprintf('%s/%s', dir_root, x_str)
dir.create(dir_name, showWarnings = FALSE)
X = mydata[, x_str]
dir_name = sprintf('%s/%s/%s', dir_root, x_str, y_str)
dir.create(dir_name, showWarnings = FALSE)
Y = mydata[, y_str]
dir_name = sprintf('%s/%s/%s/perm%s', dir_root, x_str, y_str, myseed)
dir.create(dir_name, showWarnings = FALSE)

# shuffle mydata around, but only change M, as we want the relationship between
# X and Y to stay the same
set.seed(as.integer(myseed) %% 2^31)
perm_labels <- sample.int(dim(mydata)[1], replace = FALSE)
print(perm_labels[1:10])

vox_list = read.table(m_file)[, 1]

X = mydata[, x_str]
Y = mydata[, y_str]
for (m_str in vox_list) {
    out_fname = sprintf('%s/%s.csv', dir_name, m_str)
    print(out_fname)
    # some voxels are all zeros! give them a bad result
    if (sum(mydata[, m_str]==0) == nrow(mydata)) {
        res_names = c('nobs', 'tot', 'tot_p', 'acme', 'acme_p', 'ade', 'ade_p', 'prop', 'prop_p',
                    'tot_2p5ci', 'tot_97p5ci', 'acme_2p5ci', 'acme_97p5ci', 'ade_2p5ci', 'ade_97p5ci', 'prop_2p5ci', 'prop_97p5ci')
        all_res = rep(1, length(res_names))
        names(all_res) = res_names    
    } else {
        all_res = run_model4(X, mydata[perm_labels, m_str], Y, nboot=nboot, data2=mydata)
    }
    write.csv(t(all_res), file=out_fname, row.names=F, quote=F)
}
