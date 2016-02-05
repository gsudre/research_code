# Separates ROIs based on clusters
thresh=.05
hemi = 'L'
brain = 'cortex'
max_vertices = 20
max_clusters = 50
good_connections = 10 #>=

load(sprintf('~/data/results/simple/thalCor%s_allPairwiseDiffs_strict_adjusted.RData',hemi))

require(R.matlab)
mat = readMat(sprintf('~/Documents/surfaces/IMAGING_TOOLS/%s.mat',brain))
if (hemi=='R') {
    nbr = mat[[7]]
} else {
    nbr = mat[[3]]
}

# the idea is to assign a number to each cluster of continuous good voxels.
# then we can remove the clusters with smallest number of voxels

# start by loading the connectedness value for each vertex, threshold them,
# and apply the mask

if (brain=='thalamus') {
    res = matrix(np<thresh & pr<thresh,nrow=dim(nbr)[1])
    conn = rowSums(res,na.rm=T)
    flatmask = F
} else {
    res = matrix(np<thresh & pr<thresh,ncol=dim(nbr)[1])
    conn = colSums(res,na.rm=T)
    load('~/data/results/simple/flatmask.RData')
}
roi = conn > good_connections
roi = roi & !flatmask

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

# remove all clusters that have less vertices than a threshold
good_clusters = vector()
cluster_sizes = vector()
for (i in 1:cl) {
    cl_size = sum(clusters==i)
    if (cl_size >= max_vertices) {
        good_clusters = c(good_clusters, i)
        cluster_sizes = c(cluster_sizes, cl_size)
    }
}
sorted_clusters = sort(cluster_sizes, decreasing=T, index.return=T)

# now we paint and report the top clusters
cl_rois = vector(mode='numeric', length=length(roi))
for (i in 1:min(length(good_clusters),max_clusters)) {
    this_cluster = good_clusters[sorted_clusters$ix[i]]
    cat('Good cluster',i,'index',this_cluster,'size=',sorted_clusters$x[i],'\n')
    cl_rois[clusters==this_cluster] = i
}
fname = sprintf('~/data/results/simple/clustered_allPairwise_%s%s.txt',
                brain, hemi)
write_vertices(cl_rois, fname, 'clusters')