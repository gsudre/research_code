# Separates ROIs based on clusters
thresh=.3
brain = 'cortex'
min_vertices = 100

require(R.matlab)
mat = readMat(sprintf('~/Documents/surfaces/IMAGING_TOOLS/%s.mat',brain))
for (hemi in c('L','R')) {
    if (hemi=='R') {
        nbr = mat[[7]]
    } else {
        nbr = mat[[3]]
    }
    for (g in c('per','rem','nv')) {
        # start by loading the connectedness value for each vertex, threshold them,
        # and apply the mask
        conn = read.table(sprintf('~/data/results/simple/connectedness_p001_%s%s_diff_%s.txt',
                                 brain, hemi, g), skip=3)
        conn = conn[,1]
        roi = conn > thresh
        
        # the idea is to assign a number to each cluster of continuous good voxels.
        # then we can remove the clusters with smallest number of voxels
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
        
        # set the vertices that don't belong to a good cluster to 0
        for (i in 1:cl) {
            if (sum(clusters==i) < min_vertices) {
                conn[clusters==i] = 0
            }
        }
        # write in the new connectedness file
        fname = sprintf('~/data/results/simple/connectedness_p001_mask%d_%s%s_diff_%s.txt',
                        min_vertices, brain, hemi, g)
        write_vertices(conn, fname, c(g))
    }
    
}
