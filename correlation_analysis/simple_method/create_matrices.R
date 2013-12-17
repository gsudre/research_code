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

groups = c('NV','persistent','remission')
visits = c('baseline','last')

# creating the effect size matrices and saving to disk
nverts = dim(thalamusL)[2]
for (g in groups) {
    cat('group',g,'\n')
    for (v in visits) {
        cat('\t',v,'\n')
        idx = group==g & visit==v
        esThalamusLgpL = getESfromL(thalamusL[idx,], gpL[idx,])
        esThalamusLstriatumL = getESfromR(thalamusL[idx,], striatumL[idx,])
        esThalamusLcortexL = getESfromR(thalamusL[idx,], cortexL[idx,])        
        save(esThalamusLstriatumL,esThalamusLgpL,esThalamusLcortexL,
             file=sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,v))
        rm(esThalamusLstriatumL,esThalamusLgpL,esThalamusLcortexL)
    }
    # WE ASSUME THAT SUBJECTS ARE IN THE SAME ORDER FOR BASELINE AND LAST SCANS
    idx1 = group==g & visit=='baseline'
    idx2 = group==g & visit=='last'
    
    # calculating diff (correlation of the difference)
    cat('\t diff\n')
    esThalamusLgpL = getESfromR(thalamusL[idx2,]-thalamusL[idx1,], gpL[idx2,]-gpL[idx1,])
    esThalamusLstriatumL = getESfromR(thalamusL[idx2,]-thalamusL[idx1,], striatumL[idx2,]-striatumL[idx1,])
    esThalamusLcortexL = getESfromR(thalamusL[idx2,]-thalamusL[idx1,], cortexL[idx2,]-cortexL[idx1,])
    save(esThalamusLstriatumL,esThalamusLgpL,esThalamusLcortexL,
         file=sprintf('~/data/results/structural_v2/es_%s_diff.RData',g))
    rm(esThalamusLstriatumL,esThalamusLgpL,esThalamusLcortexL)
    
    # calculating delta (difference of correlations)
    cat('\t delta\n')
    esThalamusLgpL = getESfromDeltaInR(thalamusL[idx1,], gpL[idx1,], thalamusL[idx2,], gpL[idx2,])
    esThalamusLstriatumL = getESfromDeltaInR(thalamusL[idx1,], striatumL[idx1,], thalamusL[idx2,], striatumL[idx2,])
    esThalamusLcortexL = getESfromDeltaInR(thalamusL[idx1,], cortexL[idx1,], thalamusL[idx2,], cortexL[idx2,])
    save(esThalamusLstriatumL,esThalamusLgpL,esThalamusLcortexL,
         file=sprintf('~/data/results/structural_v2/es_%s_delta.RData',g))
    rm(esThalamusLstriatumL,esThalamusLgpL,esThalamusLcortexL)
}
