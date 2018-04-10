# Plots different maskids in a 2D plot according to 2 aggregate dimensions of
# movement
#
# GS, 04/2018, for Ayaka's irritability project

library(ggplot2)

maskids = read.table('~/tmp/ayaka_fmri2.txt')[, 1]
root_dir = '/Volumes/T/resting_all/'

all_mvmt = c()
for (m in maskids) {
    # dir_name = sprintf('%s/%04d/afni/%04d.rest.example11.results/', root_dir,
    #                     m, m)

    # if (!file.exists(dir_name)) {
    #     dir_name = sprintf('%s/%04d/afni/%04d.rest.example11_HaskinsPeds.results/',
    #                         root_dir, m, m)
    # }

    # if (!file.exists(dir_name)) {
    #     dir_name = sprintf('%s/%04d/afni/%04d.rest.compCor.results/',
    #                         root_dir, m, m)
    # }

    # if (!file.exists(dir_name)) {
    #     dir_name = sprintf('%s/%04d/afni/%04d.rest.subjectSpace.results/',
    #                         root_dir, m, m)
    # }

    # fname = sprintf('%s/dfile_rall.1D', dir_name)
    
    fname = sprintf('%s/%04dR/rp_%04dR_001.txt', root_dir, m, m)
    if (file.exists(fname)) {
        mvmt = read.table(fname)
        # skip first row which is zero
        mvmt = mvmt[2:nrow(mvmt), ]
        all_mvmt = rbind(all_mvmt, c(m, colMeans(abs(mvmt))))
    } else {
        print(m)
    }
}
pca = prcomp(all_mvmt[, 2:6], scale=T)
p = ggplot(as.data.frame(pca$x), aes(x=PC1, y=PC2)) + geom_point()
print(p)

df = as.data.frame(cbind(all_mvmt[, 1], pca$x[, 'PC1'], pca$x[, 'PC2']))
colnames(df) = c('maskid', 'PC1', 'PC2')
write.csv(df, file='~/tmp/rsfmri_movement_PCs.csv', row.names=F)