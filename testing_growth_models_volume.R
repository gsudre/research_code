groups = c('NV','persistent','remission')
thresh=.01

csvData = read.csv('~/data/structural/VOLUMES_SA_SOOURCE_OCT_2012.csv')
load('~/data/structural/just_gf1473_dsm45.RData')
vol_columns = c(4,7,14:35)
nsubjs = dim(gf_1473)[1]
thalVolume = matrix(nrow=nsubjs, ncol=length(vol_columns))
for (i in 1:nsubjs) {
    idx = csvData[,1]==gf_1473[i,]$MASKID.x
    if (sum(idx) != 1) {
        cat('ERROR finding maskid',gfBase[i,]$MASKID.x,'\n')
    } else {
        thalVolume[i,] = as.matrix(csvData[idx,vol_columns])
    }
}
colnames(thalVolume) = colnames(csvData)[vol_columns]

nvoxels = dim(thalVolume)[2]
model = vector()
nvVSper = vector()
nvVSrem = vector()
perVSrem = vector()
for (v in 3:nvoxels) {
    cat(v,'\n')
    cnt = 0
    for (g in groups) {
        idx <- gf_1473$outcome.dsm5==g & gf_1473$MATCH7==1
        d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=thalVolume[idx,v], subject=as.factor(gf_1473[idx,]$PERSON.x))
        dg<-groupedData(y~age|subject, data=d)
        # try a quadratic fit
        m.quad = try(lme(y ~ age + I(age^2), random=~1|subject, data=dg))
        if (length(m.quad)>1 && summary(m.quad)$tTable[3,5] < thresh) {
            cnt = cnt + 1
        }
    }
    cnt=0
    idx <- (gf_1473$outcome.dsm5==groups[1] | gf_1473$outcome.dsm5==groups[2] | gf_1473$outcome.dsm5==groups[3]) & gf_1473$MATCH7==1
    d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=thalVolume[idx,v], subject=as.factor(gf_1473[idx,]$PERSON.x))
    dg<-groupedData(y~age|subject, data=d)
    if (cnt==length(groups)) {
        m.quad = try(lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg))
        if (length(m.quad)>1) {
            model[v]=2
            nvVSper[v]=summary(m.quad)$tTable[8,5]
            nvVSrem[v]=summary(m.quad)$tTable[9,5]
            contrasts(dg$sx) <- contr.treatment(levels(dg$sx), base=2)
            m.quad = try(lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg))
            if (length(m.quad) > 1) {
                perVSrem[v]=summary(m.quad)$tTable[9,5] 
            }
        }
    } else {
        m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
        if (length(m.linear)>1) {
            model[v]=1
            nvVSper[v]=summary(m.linear)$tTable[5,5]
            nvVSrem[v]=summary(m.linear)$tTable[6,5]
            contrasts(dg$sx) <- contr.treatment(levels(dg$sx), base=2)
            m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
            if (length(m.linear) > 1) {
                perVSrem[v]=summary(m.linear)$tTable[6,5]
            }
        }
    }
}

##### WHOLE DATA ANALYSIS #####

for (v in 1:2) {
    # check which model works best for each group
    cnt = 0
    for (g in groups) {
        idx <- gf_1473$outcome.dsm5==g & gf_1473$MATCH7==1
        d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=thalVolume[idx,v], subject=as.factor(gf_1473[idx,]$PERSON.x))
        dg<-groupedData(y~age|subject, data=d)
        # try a quadratic fit
        m.quad = try(lme(y ~ age + I(age^2), random=~1|subject, data=dg))
        if (summary(m.quad)$tTable[3,5] < thresh) {
            cnt = cnt + 1
        }
    }
    # moving on to group comparison analysis
    idx <- (gf_1473$outcome.dsm5==groups[1] | gf_1473$outcome.dsm5==groups[2] | gf_1473$outcome.dsm5==groups[3]) & gf_1473$MATCH7==1
    d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=thalVolume[idx,v], subject=as.factor(gf_1473[idx,]$PERSON.x))
    dg<-groupedData(y~age|subject, data=d)
    if (cnt==length(groups)) {
        print('Quadratic fits all groups. Running per-group model.')
        m.quad = try(lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg))
        print(summary(m.quad)$tTable)
        contrasts(dg$sx) <- contr.treatment(levels(dg$sx), base=2)
        m.quad = try(lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg))
        print(summary(m.quad)$tTable)
    } else {
        m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
        contrasts(dg$sx) <- contr.treatment(levels(dg$sx), base=2)
        m.linear = try(lme(y ~ sx*age, data=dg, random=~1|subject))
        print(summary(m.linear)$tTable)
    }
}
