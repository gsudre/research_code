thresh=.5
hemi = c('L','R')
other = 'gp'
time = c('baseline','last','diff')
groups = c('NV', 'remission', 'persistent')

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

for (g in groups) {
    for (t in time) {
        for (h in hemi) {
            cat(g, t, h, '\n')
            load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                         h, other, t, g))
            es = abs(es)
            bes = binarize(es,thresh)
            
            # first dimension is the thalamus, so assign colors to it
            paint_voxels = which(rowSums(bes)>0)
            data = vector(mode='numeric',length=dim(bes)[1])
            # paint each vertex in the thalamus with how many voxels it connects to
            # this way we can get a sense of how sparse out plot willl be for the 
            #other brain region
            for (v in 1:length(paint_voxels)) {
                data[paint_voxels[v]] = sum(bes[paint_voxels[v],])/dim(bes)[2]
            }
            fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_%s.txt', 
                            h, other, t, thresh, g)
            write_vertices(data, fname, c(g))
        }
    }
    
}

