# Computes mean and SD tables across brain regions
#
# GS 12/2018

data = read.csv('~/Downloads/for_patrick_4_sites.csv')
out_fname1 = '~/tmp/mean_sds.csv'  # where to write the means and SDs
out_fname2 = '~/tmp/anovas.csv'  # where to write the ANOVA results
data_cols = c(31:33)  # column numbers for the data variables
site_var = 'SITE'
sex_var = 'SEX'
dx_var = 'DX'
age_var = 'AGE'
icv_var = 'cerebellum'  # temporary


# working on means and SDs
res = data.frame()
cnt = 1
for (si in unique(data[, site_var])) {
  for (d in unique(data[, dx_var])) {
    for (sex in unique(data[, sex_var])) {
      for (k in data_cols) {
        res[cnt, 'site'] = si
        res[cnt, 'dx'] = d
        res[cnt, 'sex'] = sex
        res[cnt, 'pheno'] = colnames(data)[k]
        idx = data[, site_var]==si & data[, sex_var]==sex & data[, dx_var]==d
        
        res[cnt, 'mean'] = mean(data[idx, k], na.rm=T)
        res[cnt, 'sd'] = sd(data[idx, k], na.rm=T)
        
        fm_str = sprintf('%s ~ scale(%s, scale=F)', colnames(data)[k], age_var)
        fit = lm(as.formula(fm_str), data=data[idx, ], na.action=na.omit)
        res[cnt, 'mean_resid_age'] = mean(fit$residuals)
        res[cnt, 'sd_resid_age'] = sd(fit$residuals)
        
        fm_str = sprintf('%s ~ scale(%s, scale=F) + scale(%s, scale=F)', colnames(data)[k], age_var, icv_var)
        fit = lm(as.formula(fm_str), data=data[idx, ], na.action=na.omit)
        res[cnt, 'mean_resid_age_icv'] = mean(fit$residuals)
        res[cnt, 'sd_resid_age_icv'] = sd(fit$residuals)
        
        cnt = cnt + 1
      }
    }
  }
}
write.csv(res, file=out_fname1, row.names=F)


# working on ANOVAs
res = data.frame()
cnt = 1
for (si in unique(data[, site_var])) {
  for (k in data_cols) {
    idx = data[, site_var]==si
    
    # y ~ DX*SEX
    fm_str = sprintf('%s ~ %s*%s', colnames(data)[k], dx_var, sex_var)
    fit = lm(as.formula(fm_str), data=data[idx, ], na.action=na.omit)
    tmp = as.matrix(anova(fit))
    for (t in 1:(nrow(tmp)-1)) { #ignore residuals row
      res[cnt, 'site'] = si
      res[cnt, 'pheno'] = colnames(data)[k]
      res[cnt, 'formula'] = fm_str
      res[cnt, 'nobs'] = sum(idx)
      
      res[cnt, 'term'] = rownames(tmp)[t]
      res[cnt, 'Fstat'] = tmp[t, 'F value']
      res[cnt, 'pval'] = tmp[t, 'Pr(>F)']
      
      cnt = cnt + 1
    }
    
    # y ~ dx + sex
    fm_str = sprintf('%s ~ %s + %s', colnames(data)[k], dx_var, sex_var)
    fit = lm(as.formula(fm_str), data=data[idx, ], na.action=na.omit)
    tmp = as.matrix(anova(fit))
    for (t in 1:(nrow(tmp)-1)) { #ignore residuals row
      res[cnt, 'site'] = si
      res[cnt, 'pheno'] = colnames(data)[k]
      res[cnt, 'formula'] = fm_str
      res[cnt, 'nobs'] = sum(idx)
      
      res[cnt, 'term'] = rownames(tmp)[t]
      res[cnt, 'Fstat'] = tmp[t, 'F value']
      res[cnt, 'pval'] = tmp[t, 'Pr(>F)']
      
      cnt = cnt + 1
    }
    
    # y ~ dx*sex + age
    fm_str = sprintf('%s ~ %s*%s + scale(%s, scale=F)', colnames(data)[k], dx_var, sex_var, age_var)
    fit = lm(as.formula(fm_str), data=data[idx, ], na.action=na.omit)
    tmp = as.matrix(anova(fit))
    for (t in 1:(nrow(tmp)-1)) { #ignore residuals row
      res[cnt, 'site'] = si
      res[cnt, 'pheno'] = colnames(data)[k]
      res[cnt, 'formula'] = fm_str
      res[cnt, 'nobs'] = sum(idx)
      
      res[cnt, 'term'] = rownames(tmp)[t]
      res[cnt, 'Fstat'] = tmp[t, 'F value']
      res[cnt, 'pval'] = tmp[t, 'Pr(>F)']
      
      cnt = cnt + 1
    }
    
    # y ~ dx*sex + age + icv
    fm_str = sprintf('%s ~ %s*%s + scale(%s, scale=F) + scale(%s, scale=F)', colnames(data)[k], dx_var, sex_var, age_var, icv_var)
    fit = lm(as.formula(fm_str), data=data[idx, ], na.action=na.omit)
    tmp = as.matrix(anova(fit))
    for (t in 1:(nrow(tmp)-1)) { #ignore residuals row
      res[cnt, 'site'] = si
      res[cnt, 'pheno'] = colnames(data)[k]
      res[cnt, 'formula'] = fm_str
      res[cnt, 'nobs'] = sum(idx)
      
      res[cnt, 'term'] = rownames(tmp)[t]
      res[cnt, 'Fstat'] = tmp[t, 'F value']
      res[cnt, 'pval'] = tmp[t, 'Pr(>F)']
      
      cnt = cnt + 1
    }
  }
}
write.csv(res, file=out_fname2, row.names=F)
