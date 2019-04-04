doClean=TRUE
doZ = TRUE

library(nlme)
a = read.csv('~/data/heritability_change/resting_demo.csv')
a$famID = a$Extended.ID...FamilyIDs
a[is.na(a$Extended.ID...FamilyIDs), 'famID'] = a[is.na(a$Extended.ID...FamilyIDs), 'Nuclear.ID...FamilyIDs']
famids = unique(a[, c('famID', 'Medical.Record...MRN')])
data_fname = '~/data/heritability_change/rsfmri_3min_assoc_n231_slopes'
if (doZ) {
    data_fname = paste0(data_fname, 'Z')
}
if (doClean) {
    data_fname = paste0(data_fname, 'Clean')
}
print(data_fname)
data = read.csv(sprintf('%s.csv', data_fname))
data$sex = as.factor(data$sex)
data = merge(data, famids, by.x='ID', by.y='Medical.Record...MRN', all.x=T)

# just to get var_names
b = read.csv('~/data/heritability_change/fmri_corr_tables/pearson_3min_n462_aparc.csv')
var_names = colnames(b)[2:ncol(b)]

out_fname = '~/data/heritability_change/assoc_LME_3min_n231_pearsonSlopes'
if (doZ) {
    out_fname = paste0(out_fname, 'Z')
}
if (doClean) {
    out_fname = paste0(out_fname, 'Clean')
}

predictors = c('SX_inatt', 'SX_HI', 'inatt_baseline', 'HI_baseline', 'DX', 'DX2')
targets = var_names
hold=NULL
for (i in targets) {
    for (j in predictors) {
        fm_str = sprintf('%s ~ %s + sex', i, j)
        model1<-try(lme(as.formula(fm_str), data, ~1|famID, na.action=na.omit))
        if (length(model1) > 1) {
            temp<-summary(model1)$tTable
            a<-as.data.frame(temp)
            a$formula<-fm_str
            a$target = i
            a$predictor = j
            a$term = rownames(temp)
            hold=rbind(hold,a)
        } else {
            hold=rbind(hold, NA)
        }
    }
}
write.csv(hold, sprintf('%s.csv', out_fname), row.names=F)

data2 = data[data$DX=='ADHD', ]
predictors = c('SX_inatt', 'SX_HI', 'inatt_baseline', 'HI_baseline')
targets = var_names
hold=NULL
for (i in targets) {
    for (j in predictors) {
        fm_str = sprintf('%s ~ %s + sex', i, j)
        model1<-try(lme(as.formula(fm_str), data2, ~1|famID, na.action=na.omit))
        if (length(model1) > 1) {
            temp<-summary(model1)$tTable
            a<-as.data.frame(temp)
            a$formula<-fm_str
            a$target = i
            a$predictor = j
            a$term = rownames(temp)
            hold=rbind(hold,a)
        } else {
            hold=rbind(hold, NA)
        }
    }
}
write.csv(hold, sprintf('%s_dx1.csv', out_fname), row.names=F)

data2 = data[data$DX2=='ADHD', ]
predictors = c('SX_inatt', 'SX_HI', 'inatt_baseline', 'HI_baseline')
targets = var_names
hold=NULL
for (i in targets) {
    for (j in predictors) {
        fm_str = sprintf('%s ~ %s + sex', i, j)
        model1<-try(lme(as.formula(fm_str), data2, ~1|famID, na.action=na.omit))
        if (length(model1) > 1) {
            temp<-summary(model1)$tTable
            a<-as.data.frame(temp)
            a$formula<-fm_str
            a$target = i
            a$predictor = j
            a$term = rownames(temp)
            hold=rbind(hold,a)
        } else {
            hold=rbind(hold, NA)
        }
    }
}
write.csv(hold, sprintf('%s_dx2.csv', out_fname), row.names=F)