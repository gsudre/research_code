getESfromR <- function(m1, m2) {
    a = cbind(m1, m2)
    b = cor(a)
    tail = dim(b)[1]
    b = b[1:nverts, (nverts+1):tail]
    # got formula from http://cran.r-project.org/web/packages/compute.es/compute.es.pdf, page 72
    es = 2*b/sqrt(1-b^2)
    return(es)
}

getESfromDeltaInR <- function(m11, m12, m21, m22) {
    # formulas from http://psych.wfu.edu/furr/EffectSizeFormulas.pdf
    b1 = cor(cbind(m11, m12))
    b2 = cor(cbind(m21, m22))
    tail = dim(b1)[1]
    b1 = b1[1:nverts,(nverts+1):tail]
    b2 = b2[1:nverts,(nverts+1):tail]
    z1 = 1/2*log((1+b1)/(1-b1))
    z2 = 1/2*log((1+b2)/(1-b2))
    es = z2 - z1
    return(es)
}

groups = list(1:32, 33:64)
visits = c('baseline','last')

# creating the effect size matrices and saving to disk
nverts = dim(thalamusR)[2]
cnt = 1
for (g in groups) {
    for (v in visits) {
        cat('\t',v,'\n')
        idx = which(group=='NV' & visit==v)[g]
        esThalamusRgpR = getESfromR(thalamusR[idx,], gpR[idx,])
        esThalamusRstriatumR = 1#getESfromR(thalamusR[idx,], striatumR[idx,])
        esThalamusRcortexR = 1#getESfromR(thalamusR[idx,], cortexR[idx,])        
        save(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR,
             file=sprintf('~/data/results/structural_v2/es_NVonly%d_%s.RData',cnt, v))
        rm(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR)
    }
    # WE ASSUME THAT SUBJECTS ARE IN THE SAME ORDER FOR BASELINE AND LAST SCANS
    idx1 = which(group=='NV' & visit=='baseline')[g]
    idx2 = which(group=='NV' & visit=='last')[g]
    
    # calculating diff (correlation of the difference)
    cat('\t diff\n')
    esThalamusRgpR = getESfromR(thalamusR[idx2,]-thalamusR[idx1,], gpR[idx2,]-gpR[idx1,])
    esThalamusRstriatumR = 1#getESfromR(thalamusR[idx2,]-thalamusR[idx1,], striatumR[idx2,]-striatumR[idx1,])
    esThalamusRcortexR = 1#getESfromR(thalamusR[idx2,]-thalamusR[idx1,], cortexR[idx2,]-cortexR[idx1,])
    save(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR,
         file=sprintf('~/data/results/structural_v2/es_NVonly%d_diff.RData',cnt))
    rm(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR)
    
    # calculating delta (difference of correlations)
    cat('\t delta\n')
    esThalamusRgpR = getESfromDeltaInR(thalamusR[idx1,], gpR[idx1,], thalamusR[idx2,], gpR[idx2,])
    esThalamusRstriatumR = 1#getESfromDeltaInR(thalamusR[idx1,], striatumR[idx1,], thalamusR[idx2,], striatumR[idx2,])
    esThalamusRcortexR = 1#getESfromDeltaInR(thalamusR[idx1,], cortexR[idx1,], thalamusR[idx2,], cortexR[idx2,])
    save(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR,
         file=sprintf('~/data/results/structural_v2/es_NVonly%d_delta.RData',cnt))
    rm(esThalamusRstriatumR,esThalamusRgpR,esThalamusRcortexR)
    cnt = cnt+1
}
