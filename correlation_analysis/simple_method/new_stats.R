get_pval_from_Rs <- function(r1, n1, r2, n2) {
    b1 = 1/2*log((1+r1)/(1-r1))
    b2 = 1/2*log((1+r2)/(1-r2))
    z = (b1-b2)/sqrt(1/(n1-3)+1/(n2-3))
    return(2*pnorm(-abs(z)))
}

# get this from separate_other_rois_per_group.R
my_roi = cl_rois>0  

# some extra ROI massaging
# load('~/data/results/simple/clusterROIs')
# my_roi = my_roi & cingulate

cor = cortexR
tha = thalamusR
nvoxels = dim(cor)[2]

nvVSper = vector()
nvVSrem = vector()
perVSrem = vector()
for (v in 1:nvoxels) {
    cat(v,'\n')
    if (my_roi[v]) {
        other_roi = which(bes[,v]>0)
        rs = vector()
        for (gr in c('NV', 'persistent', 'remission')) {
            idx = group==gr
            x = rowSums(tha[idx, other_roi])
            y = cor[idx, v]
            if (time=='diff') {
                x = x[seq(2,length(x),2)] - x[seq(1,length(x),2)]
                y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
            } else if (time=='baseline') {
                x = x[seq(1,length(x),2)]
                y = y[seq(1,length(y),2)]
            } else {
                x = x[seq(2,length(x),2)]
                y = y[seq(2,length(y),2)]
            }
            my_r = cor.test(y,x)$estimate
            rs = c(rs, my_r)
        } 
        nvVSper[v] = get_pval_from_Rs(rs[1],64,rs[2],32)
        nvVSrem[v] = get_pval_from_Rs(rs[1],64,rs[3],32)
        perVSrem[v] = get_pval_from_Rs(rs[2],32,rs[3],32)
    } else {
        nvVSper[v] = NA
        nvVSrem[v] = NA
        perVSrem[v] = NA
    }  
}

# now we paint the voxels based on their membership
fdr_thresh = .05
paintme = vector(length=nvoxels, mode='numeric')
paintme[my_roi] = 1
# g comes from separate_other_rois_per_group.R
if (g=='NV') {
    paintme[which(p.adjust(nvVSper,method='fdr')<fdr_thresh)] = 2
    paintme[which(p.adjust(nvVSrem,method='fdr')<fdr_thresh)] = 3
    idx = intersect(which(p.adjust(nvVSper,method='fdr')<fdr_thresh),
                    which(p.adjust(nvVSrem,method='fdr')<fdr_thresh))
    paintme[idx] = 5
} else if (g=='persistent') {
    paintme[which(p.adjust(nvVSper,method='fdr')<fdr_thresh)] = 2
    paintme[which(p.adjust(perVSrem,method='fdr')<fdr_thresh)] = 4
    idx = intersect(which(p.adjust(nvVSper,method='fdr')<fdr_thresh),
                    which(p.adjust(perVSrem,method='fdr')<fdr_thresh))
    paintme[idx] = 5
} else {
    paintme[which(p.adjust(perVSrem,method='fdr')<fdr_thresh)] = 4
    paintme[which(p.adjust(nvVSrem,method='fdr')<fdr_thresh)] = 3
    idx = intersect(which(p.adjust(perVSrem,method='fdr')<fdr_thresh),
                    which(p.adjust(nvVSrem,method='fdr')<fdr_thresh))
    paintme[idx] = 5
}
fname = sprintf('~/data/results/simple/sigCortex2thalamus%s_thresh0.50_%s_%s.txt', 
                hemi, time, g)
write_vertices(paintme, fname, c(g))


t1 = rowSums(bes[,b==4])/sum(b==4)
t2 = rowSums(bes[,b==5])/sum(b==5)
tmp = t1
tmp[]=0
tmp[t1==1]=4
tmp[t2==1]=5
tmp[]=0
tmp[t1==1&t2!=1]=4
tmp[t1!=1&t2==1]=5
tmp[t1==1&t2==1]=6



