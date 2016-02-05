# define roi in the command line
brain_data = dtR_thalamus_1473

library(ggplot2)

# ##### outcome #####
# groups = c('persistent','NV','remission')
# idx <- (gf_1473$outcome.dsm5==groups[1] | gf_1473$outcome.dsm5==groups[2] | gf_1473$outcome.dsm5==groups[3]) & gf_1473$MATCH7==1
# d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=colSums(brain_data[roi,idx]), subject=as.factor(gf_1473[idx,]$PERSON.x))
# dg<-groupedData(y~age|subject, data=d)
# linear = lme(y ~ sx*age, data=dg, random=~1|subject)
# pdata <- expand.grid(age=seq(min(dg$age), max(dg$age), by=1), sx=groups)
# pdata$pred <- predict(linear, pdata, level = 0)
# Designmat <- model.matrix(eval(eval(linear$call$fixed)[-2]), pdata[-3]) 
# predvar <- diag(Designmat %*% linear$varFix %*% t(Designmat)) 
# pdata$SE <- sqrt(predvar) 
# g0 <- ggplot(pdata,aes(x=age,y=pred,colour=sx))+
#     geom_line(size=3) + theme(text = element_text(size=32))+
#     geom_ribbon(data=pdata,aes(ymin=pred-2*SE,ymax=pred+2*SE),alpha=0.2,linetype='dashed') + ylab('Surface area (mm2)') + xlab('Age (years)')+
#     xlim(sort(dg$age)[length(dg$age)*.05],sort(dg$age)[length(dg$age)*.95])+
#     theme(legend.title=element_blank())+
#     ylim(65,87)+
#     scale_colour_discrete(name  ="doesntmatter", labels=c('persistent','TD','remission'))
# print(g0)

# ##### outcome quadratic  #####
# groups = c('persistent','NV','remission')
# idx <- (gf_1473$outcome.dsm5==groups[1] | gf_1473$outcome.dsm5==groups[2] | gf_1473$outcome.dsm5==groups[3]) & gf_1473$MATCH7==1
# d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=colSums(brain_data[,idx]), subject=as.factor(gf_1473[idx,]$PERSON.x))
# dg<-groupedData(y~age|subject, data=d)
# linear = lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg)
# pdata <- expand.grid(age=seq(min(dg$age), max(dg$age), by=1), sx=groups)
# pdata$pred <- predict(linear, pdata, level = 0)
# Designmat <- model.matrix(eval(eval(linear$call$fixed)[-2]), pdata[-3]) 
# predvar <- diag(Designmat %*% linear$varFix %*% t(Designmat)) 
# pdata$SE <- sqrt(predvar) 
# g0 <- ggplot(pdata,aes(x=age,y=pred,colour=sx))+
#     geom_line(size=3) + theme(text = element_text(size=32))+
#     geom_ribbon(data=pdata,aes(ymin=pred-2*SE,ymax=pred+2*SE),alpha=0.2,linetype='dashed') + ylab('Surface area (mm2)') + xlab('Age (years)')+
#     xlim(sort(dg$age)[length(dg$age)*.05],sort(dg$age)[length(dg$age)*.95])+
#     theme(legend.title=element_blank())+
#     ylim(2580,2800)+
#     scale_colour_discrete(name  ="doesntmatter", labels=c('persistent','TD','remission'))
# print(g0)
# 
# idx <- (gf_1473$DX=='NV' | gf_1473$DX=='ADHD') & gf_1473$MATCH5==1
# d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$DX, y=colSums(brain_data[,idx]), subject=as.factor(gf_1473[idx,]$PERSON.x))
# d
# dg<-groupedData(y~age|subject, data=d)
# linear = lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg)
# summary(linear)

##### outcome quadratic  small cohort #####
groups = c('persistent','NV','remission')
idx <- group==groups[1] | group==groups[2] | group==groups[3]
d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$outcome.dsm5, y=colSums(brain_data[,idx]), subject=as.factor(gf_1473[idx,]$PERSON.x))
dg<-groupedData(y~age|subject, data=d)
linear = lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg)
pdata <- expand.grid(age=seq(min(dg$age), max(dg$age), by=1), sx=groups)
pdata$pred <- predict(linear, pdata, level = 0)
Designmat <- model.matrix(eval(eval(linear$call$fixed)[-2]), pdata[-3]) 
predvar <- diag(Designmat %*% linear$varFix %*% t(Designmat)) 
pdata$SE <- sqrt(predvar) 
g0 <- ggplot(pdata,aes(x=age,y=pred,colour=sx))+
    geom_line(size=3) + theme(text = element_text(size=32))+
    geom_ribbon(data=pdata,aes(ymin=pred-2*SE,ymax=pred+2*SE),alpha=0.2,linetype='dashed') + ylab('Surface area (mm2)') + xlab('Age (years)')+
    xlim(sort(dg$age)[length(dg$age)*.05],sort(dg$age)[length(dg$age)*.95])+
    theme(legend.title=element_blank())+
    ylim(2580,2800)+
    scale_colour_discrete(name  ="doesntmatter", labels=c('persistent','TD','remission'))
print(g0)

idx <- (gf_1473$DX=='NV' | gf_1473$DX=='ADHD') & gf_1473$MATCH5==1
d = data.frame(age=gf_1473[idx,]$AGESCAN, sx=gf_1473[idx,]$DX, y=colSums(brain_data[,idx]), subject=as.factor(gf_1473[idx,]$PERSON.x))
d
dg<-groupedData(y~age|subject, data=d)
linear = lme(y ~ sx*age + sx*I(age^2), random=~1|subject, data=dg)
summary(linear)