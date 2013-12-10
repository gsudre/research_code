str = 'esThalamusRstriatumR'
thresh = seq(.2,1,.1)

files = c('baseline','last','diff','delta')
par(mfrow=c(2,2))
for (f in files) {
    for (g in groups) {
        load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,f))
        eval(parse(text=sprintf('%sOrig = %s',g,str)))
    }
    np = vector(mode='numeric',length=length(thresh))
    nr = vector(mode='numeric',length=length(thresh))
    pr = vector(mode='numeric',length=length(thresh))
    for (i in 1:length(thresh)) {
        for (g in groups) {
            eval(parse(text=sprintf('%s = %sOrig',g, g)))
            eval(parse(text=sprintf('%s[%s<%f] = 0',g,g,thresh[i])))
            eval(parse(text=sprintf('%s[%s>=%f] = 1',g,g,thresh[i])))
            # computing Dice coefficient, from http://en.wikipedia.org/wiki/Sørensen–Dice_coefficient
            np[i]=2*sum((NV+persistent)==2,na.rm=T)/
                (sum(NV==1,na.rm=T)+sum(persistent==1,na.rm=T))
            nr[i]=2*sum((NV+remission)==2,na.rm=T)/
                (sum(NV==1,na.rm=T)+sum(remission==1,na.rm=T))
            pr[i]=2*sum((persistent+remission)==2,na.rm=T)/
                (sum(persistent==1,na.rm=T)+sum(remission==1,na.rm=T))
        }
    }
    plot(thresh,np,col='red',lwd=2,type="l",ylim=c(0,1))
    lines(thresh,nr,col='blue',lwd=2)
    lines(thresh,pr,col='green',lwd=2)
    title(f)
}
legend('topright',c('NV+persistent','NV+remission','persistent+remission'),
       col=c('red','blue','green'),lty=1,lwd=2)