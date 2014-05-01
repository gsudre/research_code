source('~/research_code/correlation_analysis/massage_volume_data.R')

idx = group=='remission' | group=='persistent' | group=='NV'
group2 = as.character(group[idx])
group2[group2=='persistent'] = 'ADHD'
group2[group2=='remission'] = 'ADHD'
cols = c(3,6,7:28)
num_voxels = length(cols)
tsLinear <- array(dim=c(num_voxels, 2))
cnt = 1

# plotting code
par(mfrow=c(2,3))
pdata <- expand.grid(time=seq(min(age), max(age), by=1), group=c("NV", "ADHD"))
require(nlme)
for (v in cols) {
    d = data.frame(time=age[idx], subject=subject[idx], y=subcortexVol[idx,v], group=as.factor(group2))
#     fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
    fit<- try(lme(y~group*time + group*I(time^2), random=~1|subject, data=d), TRUE)
    if (length(fit) > 1) {  
        
        # plotting code
        plot(d$time,d$y,col='black',xlab='Age',ylab='Volume')
        pred <- predict(fit, pdata, level = 0)
        lines(pdata$time[pdata$group=='NV'], pred[pdata$group=='NV'], col="blue",lwd=2)
        lines(pdata$time[pdata$group=='ADHD'], pred[pdata$group=='ADHD'], col="red",lwd=2)
        title(colnames(subcortexVol)[v])
        
#         #linear
#         tsLinear[cnt,1] <- summary(fit)$tTable[4,4]
#         tsLinear[cnt,2] <- summary(fit)$tTable[4,5]
        #quadratic
        tsLinear[cnt,1] <- summary(fit)$tTable[5,5]
        tsLinear[cnt,2] <- summary(fit)$tTable[6,5]
    }
    cnt = cnt + 1
}
thresh = .05
goodRegions = which(tsLinear[,2]<thresh)
cat('Regions with significant slope:', length(goodRegions))
for (r in goodRegions) {
    cat('\n',colnames(subcortexVol)[cols][r],'(',tsLinear[r,2],')')
}

# # anything for outcome comparisons?
# idx = group=='NV' | group=='persistent'
# group2 = as.character(group[idx])
# cols = c(3,6,7:28)
# num_voxels = length(cols)
# tsLinear <- array(dim=c(num_voxels, 2))
# cnt = 1
# for (v in cols) {
#     d = data.frame(time=age[idx], subject=subject[idx], y=subcortexVol[idx,v], group=as.factor(group2))
#     fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
#     if (length(fit) > 1) {  
#         tsLinear[cnt,1] <- summary(fit)$tTable[4,4]
#         tsLinear[cnt,2] <- summary(fit)$tTable[4,5]
#     }
#     cnt = cnt + 1
# }
# thresh = .05
# goodRegions = which(tsLinear[,2]<thresh)
# cat('\nRegions with significant slope:', length(goodRegions))
# for (r in goodRegions) {
#     cat('\n',colnames(subcortexVol)[cols][r],'(',tsLinear[r,2],')')
# }
# 
# # 3-way?
# idx = group=='persistent' | group=='remission' | group=='NV'
# group2 = as.character(group[idx])
# cols = c(3,6,7:28)
# num_voxels = length(cols)
# tsLinear <- array(dim=c(num_voxels, 2))
# cnt = 1
# for (v in cols) {
#     d = data.frame(time=age[idx], subject=subject[idx], y=subcortexVol[idx,v], group=as.factor(group2))
#     fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
#     if (length(fit) > 1) {  
#         tsLinear[cnt,1] <- summary(fit)$tTable[6,4]
#         tsLinear[cnt,2] <- summary(fit)$tTable[6,5]
#     }
#     cnt = cnt + 1
# }
# thresh = .05
# goodRegions = which(tsLinear[,2]<thresh)
# cat('\nRegions with significant slope:', length(goodRegions))
# for (r in goodRegions) {
#     cat('\n',colnames(subcortexVol)[cols][r],'(',tsLinear[r,2],')')
# }