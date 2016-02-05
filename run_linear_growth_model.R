# load('~/data/structural/just_gf1473_dsm45.RData')
# load('~/data/structural/DATA_1473.RData')

# groups = c('NV','persistent','remission')
# brain_data = dtR_thalamus_1473
# 
# ##### outcome #####
# nvoxels = dim(brain_data)[1]
# nvVSper = vector()
# nvVSrem = vector()
# perVSrem = vector()
# for (v in 1:nvoxels) {
#     cat(v,'\n')
#     idx <- (gf_1473$outcome.dsm5==groups[1] | gf_1473$outcome.dsm5==groups[2] | gf_1473$outcome.dsm5==groups[3]) & gf_1473$MATCH7==1
#     d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=brain_data[v,idx], subject=as.factor(gf_1473[idx,]$PERSON.x))
#     dg<-groupedData(y~age|subject, data=d)
#     m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
#     if (length(m.linear)>1) {
#         nvVSper[v]=summary(m.linear)$tTable[5,5]
#         nvVSrem[v]=summary(m.linear)$tTable[6,5]
#         contrasts(dg$sx) <- contr.treatment(levels(dg$sx), base=2)
#         m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
#         if (length(m.linear) > 1) {
#             perVSrem[v]=summary(m.linear)$tTable[6,5]
#         }
#     }
# }

##### adhd #####
brain_data = dtR_thalamus_1473
nvoxels = dim(brain_data)[1]
nvVSadhd = vector()
for (v in 1:nvoxels) {
    cat(v,'\n')
    idx <- (gf_1473$DX=='NV' | gf_1473$DX=='ADHD') & gf_1473$MATCH5==1
    d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$DX, y=brain_data[v,idx], subject=as.factor(gf_1473[idx,]$PERSON.x))
    dg<-groupedData(y~age|subject, data=d)
    m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
    if (length(m.linear)>1) {
        nvVSadhd[v]=summary(m.linear)$tTable[4,5]
    }
}
