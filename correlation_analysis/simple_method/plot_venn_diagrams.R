# Venn diagrams
thresh = .6
hemi = 'R'
other = 'gp'

library(venneuler)
files = c('baseline','last','diff','delta')
par(mfrow=c(2,2))
for (f in files) {
    for (g in groups) {
        load(sprintf('~/data/results/structural_v2/es%s_thalamus2%s_%s_%s.RData',
                     hemi, other, f, g))
        eval(parse(text=sprintf('%s = abs(es)',g)))
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
