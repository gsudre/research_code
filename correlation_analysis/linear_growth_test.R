source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')

### nvVSadhd ###
fnameRoot = '~/data/results/structural_v2/growth_correlationCohort_anova'
idx = group=='persistent' | group=='remission' | group=='NV'
# group2 = as.character(group)
# group2[group2=='persistent'] = 'ADHD'
# group2[group2=='remission'] = 'ADHD'
brain_data = c('thalamusL','thalamusR')
for (b in brain_data) {
    eval(parse(text=sprintf('data=%s', b)))
    d = data.frame(aging=age[idx], personid=subject[idx], dx=as.factor(group[idx]))
#     vs = mni.vertex.mixed.model(d, 'y~dx*aging', '~1|personid', t(data[idx,]))
    vs = mni.vertex.mixed.model.anova(d, 'y~dx*aging', '~1|personid', t(data[idx,]))
    fname = sprintf('%s_%s.txt', fnameRoot, b)
    mni.write.vertex.stats(vs, fname)
#     num_voxels = dim(data)[2]
#     tsLinear <- array(dim=c(num_voxels, 2))
#     for (v in 1:num_voxels) {
#         print(sprintf('%d / %d', v, num_voxels))
#         d = data.frame(time=age, subject=subject, y=data[,v], group=as.factor(group2))
#         fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
#         if (length(fit) > 1) {  
#             tsLinear[v,1] <- summary(fit)$tTable[4,4]
#             tsLinear[v,2] <- summary(fit)$tTable[4,5]
#         }
#     }
#     fname = sprintf('%s_%s.txt', fnameRoot, b)
#     write_vertices(tsLinear, fname, c('Tval','pval'))
}

# ### outcome differences ###
# brain_data = c('thalamusL','thalamusR')
# for (b in brain_data) {
#     eval(parse(text=sprintf('data=%s', b)))
#     num_voxels = dim(data)[2]
#     nvVSper <- array(dim=c(num_voxels, 2))
#     nvVSrem <- array(dim=c(num_voxels, 2))
#     perVSrem <- array(dim=c(num_voxels, 2))
#     for (v in 1:num_voxels) {
#         print(sprintf('%d / %d', v, num_voxels))
#         d = data.frame(time=age, subject=subject, y=data[,v], group=as.factor(group))
#         fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
#         if (length(fit) > 1) {  
#             nvVSper[v,1]=summary(fit)$tTable[5,4]
#             nvVSper[v,2]=summary(fit)$tTable[5,5]
#             nvVSrem[v,1]=summary(fit)$tTable[6,4]
#             nvVSrem[v,2]=summary(fit)$tTable[6,5]
#             contrasts(d$group) <- contr.treatment(levels(d$group), base=2)
#             fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
#             perVSrem[v,1]=summary(fit)$tTable[6,4]
#             perVSrem[v,2]=summary(fit)$tTable[6,5]
#         }
#     }
#     write_vertices(nvVSper, 
#                    sprintf('~/data/results/structural_v2/growth_correlationCohort_nvVSper_%s.txt',b),
#                    c('Tval','pval'))
#     write_vertices(nvVSrem, 
#                    sprintf('~/data/results/structural_v2/growth_correlationCohort_nvVSrem_%s.txt',b),
#                    c('Tval','pval'))
#     write_vertices(perVSrem, 
#                    sprintf('~/data/results/structural_v2/growth_correlationCohort_perVSrem_%s.txt',b),
#                    c('Tval','pval'))
# }




# # making plot for good regions... VERY HARD CODED CHUNK!
# library(ggplot2)
# fname = "~/data/results/structural_v2/growth_MATCHDIFF_dsm5_ADHDvsNV_thalamusL.txt"
# a = read.table(fname, skip=3)
# fvals = a[,1]
# roi = abs(fvals)>3.49
# idx <- group2=="ADHD" | group2=="NV"
# df <- data.frame(age=age, subject=subject, sa=rowSums(thalamusL[idx, roi]), dx=group2)
# linear <- lme(sa~dx*age, random=~1|subject, data=df)
# pdata <- expand.grid(age=seq(5, 36, by=2), dx=c("NV", "ADHD"))
# pdata$pred <- predict(linear, pdata, level = 0)
# Designmat <- model.matrix(eval(eval(linear$call$fixed)[-2]), pdata[-3]) 
# predvar <- diag(Designmat %*% linear$varFix %*% t(Designmat)) 
# pdata$SE <- sqrt(predvar) 
# pd <- position_dodge(width=0.4) 
# g0 <- ggplot(pdata,aes(x=age,y=pred,colour=dx))+ 
#     geom_line(position=pd, size=3) + theme(text = element_text(size=32))
# g0 + geom_ribbon(data=pdata,aes(ymin=pred-2*SE,ymax=pred+2*SE),alpha=0.1,linetype='dashed') + ylab('Surface area (mm2)') + xlab('Age (years)') 
# print(g0)

# # anything for remission vs persistent?
# fnameRoot = '~/data/results/structural_v2/growth_MATCHDIFF_dsm5_3way'
# idx = group=='NV' | group=='persistent'
# group2 = as.character(group[idx])
# brain_data = c('thalamusL','thalamusR')
# for (b in brain_data) {
#     eval(parse(text=sprintf('data=%s', b)))
#     num_voxels = dim(data)[2]
#     tsLinear <- array(dim=c(num_voxels, 2))
#     for (v in 1:num_voxels) {
#         print(sprintf('%d / %d', v, num_voxels))
#         d = data.frame(time=age[idx], subject=subject[idx], y=data[idx,v], group=as.factor(group2))
#         fit<- try(lme(y~group*time, random=~1|subject, data=d), TRUE)
#         if (length(fit) > 1) {  
#             tsLinear[v,1] <- summary(fit)$tTable[4,4]
#             tsLinear[v,2] <- summary(fit)$tTable[4,5]
#         }
#     }
#     fname = sprintf('%s_%s.txt', fnameRoot, b)
#     write_vertices(tsLinear, fname, c('Tval','pval'))
# }

# # double checking symptom count
# # SX_inatt.x, SX_HI, SX_total.x
# fnameRoot = '~/data/results/structural/growth_MATCHDIFF_dsm5_total'
# idx = group=='persistent' | group=='remission'
# gf_sx = read.csv('~/data/structural/gf_1473_dsm45.csv')
# sx_maskids = maskid[idx]
# sx = vector(mode='numeric', length=length(sx_maskids))
# for (s in 1:length(sx_maskids)) {
#     sx[s] = gf_sx[gf_sx$MASKID.x == sx_maskids[s],]$SX_total.x
# }
# brain_data = c('thalamusL','thalamusR')
# for (b in brain_data) {
#     eval(parse(text=sprintf('data=%s', b)))
#     num_voxels = dim(data)[2]
#     tsLinear <- array(dim=c(num_voxels, 2))
#     for (v in 1:num_voxels) {
#         print(sprintf('%d / %d', v, num_voxels))
#         d = data.frame(time=age[idx], subject=subject[idx], y=data[idx,v], sx=sx)
#         fit<- try(lme(y~sx*time, random=~1|subject, data=d), TRUE)
#         if (length(fit) > 1) {  
#             tsLinear[v,1] <- summary(fit)$tTable[4,4]
#             tsLinear[v,2] <- summary(fit)$tTable[4,5]
#         }
#     }
#     fname = sprintf('%s_%s.txt', fnameRoot, b)
#     write_vertices(tsLinear, fname, c('Tval','pval'))
# }