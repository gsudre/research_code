thresh=.5
hemi = 'R'
other = 'gp'
time = 'baseline'
g1 = 'remission'
g2 = 'NV'
g3 = 'persistent'

# fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_%sOnly.txt', 
#                 hemi, other, time, thresh, g1)
# res = read.table(fname, skip=3)
# roi = which(res[,1]>.18)
# roi = roi[roi>2000]
roi=0

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

cnt = 1
for (g in c(g1, g2, g3)) {
    load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                 hemi, other, time, g))
    eval(parse(text=sprintf('es%d = abs(es)',cnt)))
    eval(parse(text=sprintf('bes%d = binarize(es%d,thresh)',cnt, cnt)))
    cnt = cnt + 1
}
m = matrix(data=F, nrow=dim(es1)[1], ncol=dim(es1)[2])
conn_diff = setdiff(which(bes1),union(which(bes2),which(bes3)))
m[conn_diff] = T

# only plot the other region for parts connected to a specific roi in the thalamus
if (length(roi)>1) {
    paint_voxels = which(colSums(m[roi,])>0)
    data = vector(mode='numeric',length=dim(m)[2])
    for (v in 1:length(paint_voxels)) {
       data[paint_voxels[v]] = sum(m[roi, paint_voxels[v]])/length(roi)
    }
    fname = sprintf('~/data/results/simple/%s%s_%s_thresh%.2f_%sOnly.txt', 
                    hemi, other, time, thresh, g1)
    write_vertices(data, fname, c(g1))
    
    # paint voxels in the thalamus roi with the same color
    data = vector(mode='numeric',length=dim(m)[1])
    data[roi] = 1
    fname = sprintf('~/data/results/simple/%sROIthalamus2%s_%s_thresh%.2f_%sOnly.txt', 
                    hemi, other, time, thresh, g1)
    write_vertices(data, fname, c(g1))
} else {
    # first dimension is the thalamus, so assign colors to it
    paint_voxels = which(rowSums(m)>0)
    data = vector(mode='numeric',length=dim(m)[1])
    # paint each vertex in the thalamus with how many voxels it connects to
    # this way we can get a sense of how sparse out plot willl be for the other brain region
    for (v in 1:length(paint_voxels)) {
        data[paint_voxels[v]] = sum(m[paint_voxels[v],])/dim(m)[2]
    }
    fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_%sOnly.txt', 
                    hemi, other, time, thresh, g1)
    write_vertices(data, fname, c(g1))
}