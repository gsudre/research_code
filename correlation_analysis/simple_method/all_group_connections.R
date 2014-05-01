thresh=.5
hemi = c('L','R')
other = 'cortex'
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
            thal_nverts = dim(bes)[1]
            other_nverts = dim(bes)[2]
            connectedness = rowSums(bes)/other_nverts
            fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh%.2f_%s.txt', 
                            h, other, t, thresh, g)
            write_vertices(connectedness, fname, c(g))
            connectedness = colSums(bes)/thal_nverts
            fname = sprintf('~/data/results/simple/%s%s2thalamus_%s_thresh%.2f_%s.txt', 
                            h, other, t, thresh, g)
            write_vertices(connectedness, fname, c(g))
        }
    }
    
}

