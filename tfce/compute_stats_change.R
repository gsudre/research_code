library(nlme)
load('~/research_code/mni_functions.RData')
data_dir = '~/data/dti_longitudinal/'
prefix = 'matchedByHand'
property = 'FA'
gf_name = sprintf('%s/merged_gf_clinical_neuropsych_clean_matchedByHand.txt', data_dir)
data_name = sprintf('%s/%s_%s_skeletonised.txt', data_dir, prefix, property)


gf = read.table(gf_name, sep='\t', header=1)
colnames(gf)[3]='age'
colnames(gf)[2]='mrn'
colnames(gf)[5]='dx'
colnames(gf)[12]='inatt'
colnames(gf)[13]='hi'

brain_data = read.table(data_name)
out = brain_data[,1:4]

data = as.matrix(brain_data[,4:dim(brain_data)[2]])

idx = gf$dx=='ADHD'
data = data[,idx]
gf = gf[idx,]

# calculate the actual change data we'll be running
# initiate the variables... make sure to remove them later!
changeInatt = c(0)
changeHI = c(0)
changeBrain = as.matrix(data[,1])
for (s in unique(gf$mrn)) {
    idx = gf$mrn==s
    change = lm(gf[idx,]$inatt ~ gf[idx,]$age)$coefficients[2]
    changeInatt = c(changeInatt, change)
    change = lm(gf[idx,]$hi ~ gf[idx,]$age)$coefficients[2]
    changeHI = c(changeHI, change)
    change = mni.vertex.statistics(gf[idx,], 'y~age', data[,idx])$slope[,2]
    changeBrain = cbind(changeBrain,as.matrix(change))
}
changeHI = changeHI[2:length(changeHI)]
changeInatt = changeInatt[2:length(changeInatt)]
changeBrain = changeBrain[,2:dim(changeBrain)[2]]

out_name = sprintf('%s/deltas_%s_%s', data_dir, prefix, property)
save(changeHI,changeInatt,changeBrain,file=out_name)