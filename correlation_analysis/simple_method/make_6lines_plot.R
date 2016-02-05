# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')

# get this from separate_other_rois_per_group.R
my_roi = b==4#paintme==5#clusters==1  

# # some extra ROI massaging
# load('~/data/results/simple/clusterROIs')
# my_roi = my_roi & cingulate

cor = rowSums(cortexR[,my_roi])
other_roi = which(rowSums(bes[,my_roi])>0)
tha = rowSums(thalamusR[,other_roi])


# par(mfrow=c(2,3))
# for (g in c('NV', 'persistent', 'remission')) {
#     idx = group==g
#     plot(age[idx], tha[idx], ylab='thalamus', xlab='age')
#     abline(lm(tha[idx] ~ age[idx]), col="red")
#     title(g)
# }
# for (g in c('NV', 'persistent', 'remission')) {
#     idx = group==g
#     plot(age[idx], cor[idx], ylab='cortex', xlab='age')
#     abline(lm(cor[idx] ~ age[idx]), col="red")
#     fit = lm(cor[idx] ~ tha[idx])
#     title(sprintf('r=%.2f; t=%.2f', cor.test(tha[idx],cor[idx])$estimate,
#                   summary(fit)$coefficients[2,3]))
# }

pdata <- expand.grid(age=seq(min(age), max(age), by=1), group=levels(group))
y=scale(tha)
fit = lme(y~group*age, random=~1|subject)
plot(age,y,col='black',xlab='Age',ylab='SA z-score')
pred <- predict(fit, pdata, level = 0)
lines(pdata$age[pdata$group=='NV'], pred[pdata$group=='NV'], col="green",lwd=4)
lines(pdata$age[pdata$group=='persistent'], pred[pdata$group=='persistent'], col="red",lwd=4)
lines(pdata$age[pdata$group=='remission'], pred[pdata$group=='remission'], col="blue",lwd=4)
y=scale(cor)
fit = lme(y~group*age, random=~1|subject)
points(age,y,col='black',pch=0)
pred <- predict(fit, pdata, level = 0)
lines(pdata$age[pdata$group=='NV'], pred[pdata$group=='NV'], col="green",lwd=4,lty=3)
lines(pdata$age[pdata$group=='persistent'], pred[pdata$group=='persistent'], col="red",lwd=4, lty=3)
lines(pdata$age[pdata$group=='remission'], pred[pdata$group=='remission'], col="blue",lwd=4, lty=3)
title('solid=thalamus, dashed=cortex')
legend("bottomright", c('NV','persistent','remission'), cex=0.8, col=c("green","red",'blue'), lty=1, lwd=2, bty="n")