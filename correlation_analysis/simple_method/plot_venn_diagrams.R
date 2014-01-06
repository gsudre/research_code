# Venn diagrams
thresh = 1
hemi = 'R'
other = 'gp'
groups = c('remission', 'persistent', 'NV')

library(venneuler)
files = c('baseline','last','diff','delta')

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}


par(mfrow=c(2,2))
for (f in files) {
    for (g in groups) {
        load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                     hemi, other, f, g))
        eval(parse(text=sprintf('%s = binarize(abs(es), thresh)',g)))
    }
    vd <- venneuler(c(NV=sum(NV,na.rm=T), 
                      persistent=sum(persistent,na.rm=T), 
                      remission=sum(remission,na.rm=T),
                      "NV&persistent"=sum(NV & persistent,na.rm=T),
                      "NV&remission"=sum(NV & remission,na.rm=T),
                      "persistent&remission"=sum(persistent & remission,na.rm=T),
                      "NV&persistent&remission"=sum(NV & persistent & remission,na.rm=T)))
    plot(vd)
    title(f)
}
