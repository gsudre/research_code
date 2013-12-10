groups = c('NV','persistent','remission')
visits = c('baseline','last')

# creating the effect size matrices and saving to disk
nverts = dim(thalamusR)[2]
for (g in groups) {
    cat('group',g,'\n')
    for (v in visits) {
        idx = group==g & visit==v
        
        a = cbind(thalamusR[idx,],gpR[idx,])
        b = cor(a)
        tail = dim(b)[1]
        b = b[1:nverts,nverts:tail]
        # got formula from http://cran.r-project.org/web/packages/compute.es/compute.es.pdf, page 72
        esThalamusRgpR = 2*b/sqrt(1-b^2)
        
        a = cbind(thalamusR[idx,],striatumR[idx,])
        b = cor(a)
        tail = dim(b)[1]
        b = b[1:nverts,nverts:tail]
        esThalamusRstriatumR = 2*b/sqrt(1-b^2)
        
        a = cbind(thalamusR[idx,],cortexR[idx,])
        b = cor(a)
        tail = dim(b)[1]
        b = b[1:nverts,nverts:tail]
        esThalamusRcortexR = 2*b/sqrt(1-b^2)
        
        save(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR,
             file=sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,v))
    }
    idx1 = group==g & visit=='baseline'
    idx2 = group==g & visit=='last'
    
    # WE ASSUME THAT SUBJECTS ARE IN THE SAME ORDER FOR BASELINE AND LAST SCANS
    
    # calculating diff (correlation of the difference)
    a = cbind(thalamusR[idx2,]-thalamusR[idx1,],gpR[idx2,]-gpR[idx1,])
    b = cor(a)
    tail = dim(b)[1]
    b = b[1:nverts,nverts:tail]
    # got formula from http://cran.r-project.org/web/packages/compute.es/compute.es.pdf, page 72
    esThalamusRgpR = 2*b/sqrt(1-b^2)
    
    a = cbind(thalamusR[idx2,]-thalamusR[idx1,],striatumR[idx2,]-striatumR[idx1,])
    b = cor(a)
    tail = dim(b)[1]
    b = b[1:nverts,nverts:tail]
    esThalamusRstriatumR = 2*b/sqrt(1-b^2)
    save(esThalamusRstriatumR,esThalamusRgpR,
         file=sprintf('~/data/results/structural_v2/es_%s_diff.RData',g))
    
    # calculating delta (difference of correlations)
    # formulas from http://psych.wfu.edu/furr/EffectSizeFormulas.pdf
    b1 = cor(cbind(thalamusR[idx1,],gpR[idx1,]))
    b2 = cor(cbind(thalamusR[idx2,],gpR[idx2,]))
    tail = dim(b1)[1]
    b1 = b1[1:nverts,nverts:tail]
    b2 = b2[1:nverts,nverts:tail]
    z1 = 1/2*log((1+b1)/(1-b1))
    z2 = 1/2*log((1+b2)/(1-b2))
    esThalamusRgpR = z2 - z1
    
    b1 = cor(cbind(thalamusR[idx1,],striatumR[idx1,]))
    b2 = cor(cbind(thalamusR[idx2,],striatumR[idx2,]))
    tail = dim(b1)[1]
    b1 = b1[1:nverts,nverts:tail]
    b2 = b2[1:nverts,nverts:tail]
    z1 = 1/2*log((1+b1)/(1-b1))
    z2 = 1/2*log((1+b2)/(1-b2))
    esThalamusRstriatumR = z2 - z1
    save(esThalamusRstriatumR,esThalamusRgpR,
         file=sprintf('~/data/results/structural_v2/es_%s_delta.RData',g))
}

# Venn diagrams
thresh = .5
files = c('baseline','last','diff','delta')
par(mfrow=c(2,2))
for (f in files) {
    for (g in groups) {
        load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,f))
        eval(parse(text=sprintf('%s = esThalamusRgpR',g)))
        eval(parse(text=sprintf('%s[%s<thresh] = 0',g,g)))
        eval(parse(text=sprintf('%s[%s>=thresh] = 1',g,g)))
    }
    vd <- venneuler(c(NV=sum(NV==1,na.rm=T), 
                      persistent=sum(persistent==1,na.rm=T), 
                      remission=sum(remission==1,na.rm=T),
                      "NV&persistent"=sum((NV+persistent)==2,na.rm=T),
                      "NV&remission"=sum((NV+remission)==2,na.rm=T),
                      "persistent&remission"=sum((persistent+remission)==2,na.rm=T),
                      "NV&persistent&remission"=sum((NV+persistent+remission)==3,na.rm=T)))
    plot(vd)
    title(f)
}

# plots of intersection
thresh = seq(.2,1,.1)
files = c('baseline','last','diff','delta')
par(mfrow=c(2,2))
for (f in files) {
    for (g in groups) {
        load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,f))
        eval(parse(text=sprintf('%sOrig = esThalamusRgpR',g)))
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


# plots of intersection by group pairs (3 plots total)
thresh = seq(.2,1,.1)
files = c('baseline','last','diff','delta')

par(mfrow=c(2,2))
for (f in files) {
    for (g in groups) {
        load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,f))
        eval(parse(text=sprintf('%sOrig = esThalamusRgpR',g)))
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

# plotting the relationship in the brain
thresh=.4
for (g in c('remission','persistent')) {
    load(sprintf('~/data/results/structural_v2/es_%s_delta.RData',g,f))
    eval(parse(text=sprintf('%s = esThalamusRstriatumR',g)))
    eval(parse(text=sprintf('%s[%s<thresh] = 0',g,g)))
    eval(parse(text=sprintf('%s[%s>=thresh] = 1',g,g)))
}
m = abs(remission-persistent)
# first dimension is the thalamus, so assign colors to it
paint_voxels = which(rowSums(m)>0)
data = vector(mode='numeric',length=dim(m)[1])
data[paint_voxels] = 1
write_vertices(data, '~/data/results/structural_v2/test_thalamus.txt', c('val'))
# then only plot the other region for parts connected to a specific roi in the thalamus
roi = paint_voxels[paint_voxels<2200 & paint_voxels>1800]
paint_voxels = which(colSums(m[roi,])>0)
data = vector(mode='numeric',length=dim(m)[2])
data[paint_voxels] = 1
write_vertices(data, '~/data/results/structural_v2/test_striatum.txt', c('val'))