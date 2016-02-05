# Selects all voxels above a certain 1-p threshold and plots the mean property value over all selected voxels against a regressor
library(nlme)
# 1-p threshold
thresh=.95
# where the results (e.g. _tfce_corrp.txt) are stored
out_dir='~/data/results/dti_longitudinal/'
# where the data to be plotted (e.g. slope data) are stored
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
data_name = sprintf('%s/%s_slopes_p2.RData', data_dir, property)
phen_name = sprintf('%s/gf_short_110.csv', data_dir)
# file to threshold the voxels
out_name = sprintf('%s/HI_slopes_%s_tfce_corrp.txt', out_dir, property)

load(sprintf(data_name))
phen = read.csv(phen_name)
brain_data = slopes

# make sure phen and brain_data are in the same order (ascending by MRN)
phen = phen[order(phen$person),]
if (! all(subj_order==phen$person)) {
  print('ERROR!!!! Subjects not in the same order')
}

# select the rows to use
idx = subj_order>0  # includes everybody
# idx = phen$DX=='ADHD' & phen$SEX=='Male' 

phen = phen[idx,]
brain_data = brain_data[,idx]
subj_order = subj_order[idx]

# make a mask that contains the good voxels
stats = read.table(out_name)
good_voxels = stats[,4]>thresh

# plot the mean of good voxels by symptoms
target = phen$HI_SLOPE
data = colMeans(brain_data[good_voxels,])
fit = lm(data~target)
plot(target,data,xlab='IV',ylab='Mean data')
abline(coef=fit$coefficients,lwd=2)
print(summary(fit))
mycor = cor.test(target,data)
print(mycor)
title(sprintf('Slope sig: %.1e, R: %.3f', 
              summary(fit)$coefficients[2,4],
              mycor$estimate))





