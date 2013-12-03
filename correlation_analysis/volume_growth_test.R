source('~/research_code/correlation_analysis/massage_volume_data.R')

idx = group=='remission' | group=='persistent' | group=='NV'
group2 = as.character(group[idx])
group2[group2=='persistent'] = 'ADHD'
group2[group2=='remission'] = 'ADHD'
cols = c(7:28)
num_voxels = length(cols)
tsLinear <- array(dim=c(num_voxels, 2))
cnt = 1
for (v in cols) {
    d = data.frame(time=age[idx], subject=subject[idx], y=subcortexVol[idx,v], group=as.factor(group2))
    fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
    if (length(fit) > 1) {  
        tsLinear[cnt,1] <- summary(fit)$tTable[4,4]
        tsLinear[cnt,2] <- summary(fit)$tTable[4,5]
    }
    cnt = cnt + 1
}
thresh = .05
goodRegions = which(tsLinear[,2]<thresh)
cat('Regions with significant slope:', length(goodRegions))
for (r in goodRegions) {
    cat('\n',colnames(subcortexVol)[cols][r],'(',tsLinear[r,2],')')
}

# anything for outcome comparisons?
idx = group=='persistent' | group=='remission'
group2 = as.character(group[idx])
cols = c(7:28)
num_voxels = length(cols)
tsLinear <- array(dim=c(num_voxels, 2))
cnt = 1
for (v in cols) {
    d = data.frame(time=age[idx], subject=subject[idx], y=subcortexVol[idx,v], group=as.factor(group2))
    fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
    if (length(fit) > 1) {  
        tsLinear[cnt,1] <- summary(fit)$tTable[4,4]
        tsLinear[cnt,2] <- summary(fit)$tTable[4,5]
    }
    cnt = cnt + 1
}
thresh = .05
goodRegions = which(tsLinear[,2]<thresh)
cat('\nRegions with significant slope:', length(goodRegions))
for (r in goodRegions) {
    cat('\n',colnames(subcortexVol)[cols][r],'(',tsLinear[r,2],')')
}

# 3-way?
idx = group=='persistent' | group=='remission' | group=='NV'
group2 = as.character(group[idx])
cols = c(7:28)
num_voxels = length(cols)
tsLinear <- array(dim=c(num_voxels, 2))
cnt = 1
for (v in cols) {
    d = data.frame(time=age[idx], subject=subject[idx], y=subcortexVol[idx,v], group=as.factor(group2))
    fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
    if (length(fit) > 1) {  
        tsLinear[cnt,1] <- summary(fit)$tTable[6,4]
        tsLinear[cnt,2] <- summary(fit)$tTable[6,5]
    }
    cnt = cnt + 1
}
thresh = .05
goodRegions = which(tsLinear[,2]<thresh)
cat('\nRegions with significant slope:', length(goodRegions))
for (r in goodRegions) {
    cat('\n',colnames(subcortexVol)[cols][r],'(',tsLinear[r,2],')')
}