fout = '~/data/solar/romp_family24_dti_mean.csv'
data = read.csv('~/data/solar/family24.csv')
phen = read.csv('~/data/solar/dti_mean_phenotype_cleanedWithinTract_nodups_adhd.csv')
traits = 11:42
# only keep the MRNs for which we have data of both parents
keep = vector()
for (i in 1:(dim(data)[1])) {
    if ((length(grep("_",data[i,2]))==0) && (length(grep("_",data[i,3]))==0)
        && (length(grep("_",data[i,4]))==0)
        && (data[i,3]!=0)
        && (data[i,4]!=0)) {
        keep = c(keep, i)
    }
}
data = data[keep,]

c_titles = vector()

# let's do a run where nothing matters. It's a straight up regression for everybody
h = vector()
se = vector()
p = vector()
for (d in traits) {
    x = vector()
    y = vector()
    age = vector()
    sex = vector()
    for (i in 1:(dim(data)[1])) {
        off_idx = which(phen$id==data[i,2])
        par_idx = c(which(phen$id==data[i,3]),which(phen$id==data[i,4]))
        if (length(off_idx)>0) {
            y = c(y, phen[off_idx,d])
            age = c(age, phen[off_idx,]$age)
            sex = c(sex, data[i,5])
            x = c(x, mean(phen[par_idx,d]))
        } 
    }
    fit=lm(scale(y)~scale(x)+sex+age)
    h = c(h, abs(summary(fit)$coefficients[2,1]))
    se = c(se, abs(summary(fit)$coefficients[2,2]))
    p = c(p, abs(summary(fit)$coefficients[2,4]))
}
res1 = cbind(h,se,p)
c_titles = c(c_titles, c('h2_all','se_all','p_all'))


# now we add the family ID as a random term
library(nlme)
h = vector()
se = vector()
p = vector()
for (d in traits) {
    x = vector()
    y = vector()
    age = vector()
    sex = vector()
    fam = vector()
    for (i in 1:(dim(data)[1])) {
        off_idx = which(phen$id==data[i,2])
        par_idx = c(which(phen$id==data[i,3]),which(phen$id==data[i,4]))
        if (length(off_idx)>0) {
            y = c(y, phen[off_idx,d])
            age = c(age, phen[off_idx,]$age)
            sex = c(sex, data[i,5])
            x = c(x, mean(phen[par_idx,d]))
            fam = c(fam, data[i,1])
        } 
    }
    fit = lme(scale(y) ~ scale(x) + sex + age, random=~1|fam, na.action=na.omit)
    h = c(h, abs(summary(fit)$tTable[2,1]))
    se = c(se, abs(summary(fit)$tTable[2,2]))
    p = c(p, abs(summary(fit)$tTable[2,5]))
}
res2 = cbind(h,se,p)
c_titles = c(c_titles, c('h2_randFam','se_randFam','p_randFam'))

# let's try removing age and sex first, and using the residuals of that model
h = vector()
se = vector()
p = vector()
for (d in traits) {
    x = vector()
    y = vector()
    trait = lm(phen[,d] ~ phen$age + phen$sex)$residuals

    for (i in 1:(dim(data)[1])) {
        off_idx = which(phen$id==data[i,2])
        par_idx = c(which(phen$id==data[i,3]),which(phen$id==data[i,4]))
        if (length(off_idx)>0) {
            y = c(y, trait[off_idx])
            x = c(x, mean(trait[par_idx]))
        } 
    }
    fit=lm(scale(y)~scale(x))
    h = c(h, abs(summary(fit)$coefficients[2,1]))
    se = c(se, abs(summary(fit)$coefficients[2,2]))
    p = c(p, abs(summary(fit)$coefficients[2,4]))
}
res3 = cbind(h,se,p)
c_titles = c(c_titles, c('h2_allRes','se_allRes','p_allRes'))


# also using residuals, but this time famid is random term again
h = vector()
se = vector()
p = vector()
for (d in traits) {
    x = vector()
    y = vector()
    fam = vector()
    trait = lm(phen[,d] ~ phen$age + phen$sex)$residuals

    for (i in 1:(dim(data)[1])) {
        off_idx = which(phen$id==data[i,2])
        par_idx = c(which(phen$id==data[i,3]),which(phen$id==data[i,4]))
        if (length(off_idx)>0) {
            y = c(y, trait[off_idx])
            x = c(x, mean(trait[par_idx]))
            fam = c(fam, data[i,1])
        } 
    }
    fit = lme(scale(y) ~ scale(x), random=~1|fam, na.action=na.omit)
    h = c(h, abs(summary(fit)$tTable[2,1]))
    se = c(se, abs(summary(fit)$tTable[2,2]))
    p = c(p, abs(summary(fit)$tTable[2,5]))
}
res4 = cbind(h,se,p)
c_titles = c(c_titles, c('h2_randFarmRes','se_randFarmRes','p_randFarmRes'))



res = cbind(res1,res2,res3,res4)
colnames(res)=c_titles
rownames(res)=colnames(phen)[traits]
write.csv(res,file=fout)


# questions: 
# how to deal with siblings?
# how to deal with multi-generational families?