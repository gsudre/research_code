# Collect the results of 3dNetCorr. It matches based on column name, replacing
# by NA when  column is not in a dataset.
#
# GS 04/2019

subj_dir = '~/data/heritability_change/fmri_corr_tables/'
subjs = read.csv(sprintf('%s/../rsfmri_3min_assoc_n462.csv', subj_dir))[,'Mask.ID']

library(plyr)  # for rbind.fill

for (parc in c('aparc', 'aparc.a2009s')) {
    print(parc)
    if (parc == 'aparc') {
        expected_rois = 87
    } else {
        expected_rois = 167
    }
    data = c()
    for (s in subjs) {
        a = read.table(sprintf('%s/%04d_%s_000.netcc', subj_dir, s, parc),
                       header=1)
        # remove weird integer row
        b = a[2:nrow(a),]
        # split matrix into first set of rows as Rs, second set as Zs
        rs = b[1:ncol(b),]
        zs = b[(ncol(b)+1):nrow(b),]
        # put correct names in the square matrix
        rois = colnames(rs)
        rownames(rs) = rois
        
        # note that we're doing this only for Rs, but we could as easily do it for Zs!
    
        b.tri = rs[upper.tri(rs, diag=F)]
        # format a header for the vectorized version of the table
        w = which(upper.tri(rs, diag=F), arr.ind = TRUE)
        header = sapply(1:length(b.tri),
                        function(i) sprintf('%s.TO.%s', rois[w[i,1]],
                                                        rois[w[i,2]]))
        # concatenate vectorized matrices for the same mask id in the same row
        subj_data = c(s, b.tri)
        names(subj_data) = c('mask.id', header)  

        if (length(rois) == expected_rois) {
            data = rbind(data, subj_data)
        } else {
            # this is much slower than regular bind, so we only do it when needed
            print(sprintf('Scan %s has different number of ROIs (%d): filling missing with NA', s, length(rois)))
            data = rbind.fill(as.data.frame(data), as.data.frame(t(subj_data)))
        }
    }
    # rename it so that each row is a mask id
    write.csv(data, file=sprintf('%s/pearson_3min_n462_%s.csv', subj_dir, parc),
              row.names=F)
}
