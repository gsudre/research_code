thresh=.5
hemi = 'R'
other = 'gp'
time = 'diff'
groups = c('NV','remission','persistent')

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

cnt = 1
for (g in groups) {
    load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                 hemi, other, time, g))
    eval(parse(text=sprintf('es%d = abs(es)',cnt)))
    eval(parse(text=sprintf('bes%d = binarize(es%d,thresh)',cnt, cnt)))
    cnt = cnt + 1
}
m = matrix(data=F, nrow=dim(es1)[1], ncol=dim(es1)[2])
conn = intersect(which(bes1),intersect(which(bes2),which(bes3)))
m[conn] = T

# first dimension is the thalamus, so assign colors to it
paint_voxels = which(rowSums(m)>0)
data = vector(mode='numeric',length=dim(m)[1])
# paint each vertex in the thalamus with how many voxels it connects to
# this way we can get a sense of how sparse out plot willl be for the other brain region
for (v in 1:length(paint_voxels)) {
    data[paint_voxels[v]] = sum(m[paint_voxels[v],])/dim(m)[2]
}
fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_intersection.txt', 
                hemi, other, time, thresh)
write_vertices(data, fname, 'intersection')