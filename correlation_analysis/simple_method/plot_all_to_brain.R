# exploratory analysis to plot everything to the brain
thresh=.5
hemi = 'R'
other = 'striatum'
time = c('baseline','last','delta','diff')
groups = c('remission', 'persistent', 'NV')

for (g in groups) {
    for (t in time) {
        cat(g,t,'\n')
        load(sprintf('~/data/results/structural_v2/es%s_thalamus2%s_%s_%s.RData',
                     hemi, other, t, g))
        es[es<thresh] = 0
        es[es>=thresh] = 1
        # first dimension is the thalamus, so assign colors to it
        paint_voxels = which(rowSums(es)>0)
        data = vector(mode='numeric',length=dim(es)[1])
        # paint each vertex in the thalamus with how many voxels it connects to
        # this way we can get a sense of how sparse out plot willl be for the other brain region
        for (v in 1:length(paint_voxels)) {
            data[paint_voxels[v]] = sum(es[paint_voxels[v],])/dim(es)[2]
        }
        fname = sprintf('~/data/results/structural_v2/%sthalamus2%s_%s_thresh%0.1f_%s_exploratory.txt',
                        hemi, other, t, thresh, g)
        write_vertices(data, fname, c(g))
        
        paint_voxels = which(colSums(es)>0)
        data = vector(mode='numeric',length=dim(es)[2])
        for (v in 1:length(paint_voxels)) {
            data[paint_voxels[v]] = sum(es[, paint_voxels[v]])/dim(es)[1]
        }
        fname = sprintf('~/data/results/structural_v2/%s%s_%s_thresh%0.1f_%s_exploratory.txt',
                        hemi, other, t, thresh, g)
        write_vertices(data, fname, c(g))
    }
}