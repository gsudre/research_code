thresh=.5
hemi = 'L'
other = 'cortex'
time = 'diff'
g = 'persistent'
conn_thresh = .16
max_vertices = 100

require(R.matlab)
mat = readMat('~/Documents/surfaces/IMAGING_TOOLS/thalamus.mat')
if (hemi=='R') {
    coordT = t(mat[[6]])
    nbr = mat[[7]]
} else {
    coordT = t(mat[[2]])
    nbr = mat[[3]]
}
mat = readMat(sprintf('~/Documents/surfaces/IMAGING_TOOLS/%s.mat',other))
if (hemi=='R') {
    coordO = t(mat[[6]])
} else {
    coordO = t(mat[[2]])
}

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

# the idea is to assign a number to each cluster of continuous good voxels.
# then we can remove the clusters with smallest number of voxels
fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh0.50_%s.txt', 
                hemi, other, time, g)
res = read.table(fname, skip=3)
roi = res[,1]>conn_thresh

clusters = vector(mode='numeric', length=length(roi))
clusters[roi] = -1 # everything -1 needs to be painted
# clusters==0 are non-significant vertices
cl = 1
# while we still have vertices to be painted
while (sum(clusters<0)>0) {
    # get the first vertex to be painted
    v = which(clusters<0)[1]
    # paint it with the current color (which starts at 1)
    clusters[v] = cl
    # find out what are the neighbors that are significant
    paint_nbrs = intersect(nbr[v,],which(roi))
    # of those, find out which ones haven't been painted yet
    fresh_nbrs = paint_nbrs[clusters[paint_nbrs]<0]
    # while we still have significant neighbors to be painted
    while (length(fresh_nbrs) > 0) {
        # paint all significant neighbors with the same current color
        clusters[fresh_nbrs] = cl
        # the recently-painted neighbors become the target vertices 
        v = fresh_nbrs
        # repeat above until we have no more neighbors to paint
        paint_nbrs = intersect(nbr[v,],which(roi))
        fresh_nbrs = paint_nbrs[clusters[paint_nbrs]<0]
    }
    # increase the current color
    cl = cl + 1
}

# now we paint all clusters that have more than max_vertices in them
cl_rois = vector(mode='numeric', length=length(roi))
for (i in 1:cl) {
    cl_size = sum(clusters==i)
    if (cl_size >= max_vertices) {
        cat('Good cluster: val=',i,'size=',cl_size,'\n')
        cl_rois[clusters==i] = i
    }
}
fname = sprintf('~/data/results/simple/%sthalamus2%s_ROIs_%s_thresh%.2f_%s.txt', hemi, other, time, thresh, g)
write_vertices(cl_rois, fname, c(g))

# # finally, for each roi, create the a file for its connections
# load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
#                  hemi, other, time, g))
# es = abs(es)
# bes = binarize(es,thresh)
# for (i in 1:max_clusters) {
#     myroi = which(cl_rois==i)
#     paint_voxels = which(colSums(bes[myroi,])>0)
#     data = vector(mode='numeric',length=dim(bes)[2])
#     for (v in 1:length(paint_voxels)) {
#        data[paint_voxels[v]] = i
#     }
#     fname = sprintf('~/data/results/simple/%s%s_ROI%d_%s_thresh%.2f_%s.txt', hemi, other, i, time, thresh, g)
#     write_vertices(data, fname, c(g))
# }