groups = c('NV','persistent','remission')
library(ggplot2)
library(nlme)
d = data.frame(age=age, sx=group, y=rowSums(thalamusR), subject=as.factor(subject))
dg<-groupedData(y~age|subject, data=d)
linear = lme(y ~ sx*age, data=dg, random=~1|subject)
pdata <- expand.grid(age=seq(min(dg$age), max(dg$age), by=1), sx=groups)
pdata$pred <- predict(linear, pdata, level = 0)
Designmat <- model.matrix(eval(eval(linear$call$fixed)[-2]), pdata[-3]) 
predvar <- diag(Designmat %*% linear$varFix %*% t(Designmat)) 
pdata$SE <- sqrt(predvar) 
pdata$upper = pdata$pred+1.98*pdata$SE
pdata$lower = pdata$pred-1.98*pdata$SE
pdata$subject = as.factor(seq(nrow(pdata)))
dat = merge(pdata, dg, by=c('subject', 'age'), all=T)

g <- ggplot(dat, aes(x=age,y=y,group=sx.y,color=sx.y)) +
#     geom_point(size=1)+
#     geom_line(aes(age, y, group=subject, color=sx.y), size=.2)+
    geom_line(aes(age, pred, group=sx.x, color=sx.x), size=2)+
    geom_ribbon(aes(ymin=lower,ymax=upper,group=sx.x,color=sx.x), alpha=.1,linetype='dashed')+
    ylab('Surface area (mm^2)')+xlab('Age (years)')+
    ggtitle('Surface area: data, fitted lines, and 95% confidence intervals')+
    coord_cartesian(xlim=c(min(age)-1,max(age)+1),
                    ylim=c(min(dat$y,na.rm=T)-100, max(dat$y,na.rm=T)+100))+
    theme_bw() + 
    theme(
        text = element_text(size=10),
        axis.text.y=element_text(size=10),
        panel.grid.minor=element_blank(),
        text=element_text(family='Times'),
        legend.title=element_blank(),
        legend.position='bottom')
print(g)