thresh=.5
hemi = 'R'
other = 'gp'
time = 'diff'
g1 = 'NV'
g2 = 'persistent'
g3 = 'remission'

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

cnt = 1
for (g in c(g1, g2, g3)) {
    load(sprintf('~/data/results/structural_v2/es%s_thalamus2%s_%s_%s.RData',
                 hemi, other, time, g))
    eval(parse(text=sprintf('es%d = abs(es)',cnt)))
    eval(parse(text=sprintf('bes%d = binarize(es%d,thresh)',cnt, cnt)))
    cnt = cnt + 1
}
m = matrix(data=F, nrow=dim(es1)[1], ncol=dim(es1)[2])
conn_diff = setdiff(which(bes1),union(which(bes2),which(bes3)))
m[conn_diff] = T

# first dimension is the thalamus, so assign colors to it
paint_voxels = which(rowSums(m)>0)
data = vector(mode='numeric',length=dim(m)[1])
# paint each vertex in the thalamus with how many voxels it connects to
# this way we can get a sense of how sparse out plot willl be for the other brain region
for (v in 1:length(paint_voxels)) {
    data[paint_voxels[v]] = sum(m[paint_voxels[v],])/dim(m)[2]
}
fname = sprintf('~/data/results/structural_v2/%sthalamus2%s_%s_thresh%.2f_%sOnly.txt', 
                hemi, other, time, thresh, g1)
write_vertices(data, fname, c(g1))

# then only plot the other region for parts connected to a specific roi in the thalamus
roi = which(data>.3)
roi = roi[roi>800]
paint_voxels = which(colSums(m[roi,])>0)
data = vector(mode='numeric',length=dim(m)[2])
for (v in 1:length(paint_voxels)) {
    data[paint_voxels[v]] = sum(m[roi, paint_voxels[v]])/length(roi)
}
fname = sprintf('~/data/results/structural_v2/%s%s_%s_thresh%.2f_%sOnly.txt', 
                hemi, other, time, thresh, g1)
write_vertices(data, fname, c(g1))