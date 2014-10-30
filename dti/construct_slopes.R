# Computes the slope for symptom count and for brain data
library(nlme)
load('~/research_code/mni_functions.RData')
data_dir = '~/data/dti_longitudinal/'
prefix = 'all'
property = 'RD'
gf_name = sprintf('%s/merged_gf_clinical_neuropsych_clean.txt', data_dir)
data_name = sprintf('%s/%s_%s_skeletonised.txt', data_dir, prefix, property)


gf = read.table(gf_name, sep='\t', header=1)
colnames(gf)[3]='age'
colnames(gf)[2]='mrn'
colnames(gf)[5]='dx'
colnames(gf)[12]='inatt'
colnames(gf)[13]='hi'
colnames(gf)[19]='usemeds'

brain_data = read.table(data_name)
out = brain_data[,1:4]

data = as.matrix(brain_data[,4:dim(brain_data)[2]])

idx = gf$usemeds==1
data = data[,idx]
gf = gf[idx,]

# calculate the actual change data we'll be running
# initiate the variables... make sure to remove them later!
changeInatt = c(0)
changeHI = c(0)
dx = c(0)
baseAge = c(0)
lastAge = c(0)
subjOrder = c(0)
changeBrain = as.matrix(data[,1])
for (s in unique(gf$mrn)) {
    idx = gf$mrn==s
    # NVs will only have NAs for symptoms, so let's take care of that
    if (sum(is.na(gf[idx,]$inatt))==sum(idx)) {
        changeInatt = c(changeInatt, 0)
        changeHI = c(changeHI, 0)
    } else {
        change = lm(gf[idx,]$inatt ~ gf[idx,]$age)$coefficients[2]
        changeInatt = c(changeInatt, change)
        change = lm(gf[idx,]$hi ~ gf[idx,]$age)$coefficients[2]
        changeHI = c(changeHI, change)
    }
    change = mni.vertex.statistics(gf[idx,], 'y~age', data[,idx])$slope[,2]
    changeBrain = cbind(changeBrain,as.matrix(change))
    dx = c(dx, unique(gf[idx,]$dx))
    baseAge = c(baseAge, min(gf[idx,]$age))
    lastAge = c(lastAge, max(gf[idx,]$age))
    subjOrder = c(subjOrder, s)
}
changeHI = changeHI[2:length(changeHI)]
changeInatt = changeInatt[2:length(changeInatt)]
changeBrain = changeBrain[,2:dim(changeBrain)[2]]
dx = dx[2:length(dx)]
baseAge = baseAge[2:length(baseAge)]
lastAge = lastAge[2:length(lastAge)]
subjOrder = subjOrder[2:length(subjOrder)]

out_name = sprintf('%s/deltasWithNVs_%s_%s.RData', data_dir, prefix, property)
save(changeHI,changeInatt,changeBrain,dx,baseAge,lastAge,subjOrder,file=out_name)