thresh=.5
hemi = 'R'
other = 'gp'
time = 'diff'
g = 'persistent'


# fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_%sOnly.txt', 
#                 hemi, other, time, thresh, g)
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

load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                 hemi, other, time, g))
m = binarize(abs(es),thresh)

# only plot the other region for parts connected to a specific roi in the thalamus
if (length(roi)>1) {
    paint_voxels = which(colSums(m[roi,])>0)
    data = vector(mode='numeric',length=dim(m)[2])
    for (v in 1:length(paint_voxels)) {
       data[paint_voxels[v]] = sum(m[roi, paint_voxels[v]])/length(roi)
    }
    fname = sprintf('~/data/results/simple/%s%s_%s_thresh%.2f_%s.txt', 
                    hemi, other, time, thresh, g)
    write_vertices(data, fname, c(g))
    
    # paint voxels in the thalamus roi with the same color
    data = vector(mode='numeric',length=dim(m)[1])
    data[roi] = 1
    fname = sprintf('~/data/results/simple/%sROIthalamus2%s_%s_thresh%.2f_%s.txt', 
                    hemi, other, time, thresh, g)
    write_vertices(data, fname, c(g))
} else {
    # first dimension is the thalamus, so assign colors to it
    paint_voxels = which(rowSums(m)>0)
    data = vector(mode='numeric',length=dim(m)[1])
    # paint each vertex in the thalamus with how many voxels it connects to
    # this way we can get a sense of how sparse out plot willl be for the other brain region
    for (v in 1:length(paint_voxels)) {
        data[paint_voxels[v]] = sum(m[paint_voxels[v],])/dim(m)[2]
    }
    fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_%s.txt', 
                    hemi, other, time, thresh, g)
    write_vertices(data, fname, c(g))
}