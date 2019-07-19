# plots the % of significant QC-FC connections and the overal pearson R
# distribution

pipelines = c('', '-p25', '-p5', '-gsr-p25', '-gsr-p5',
              '-gsr-p25-nc', '-gsr-p5-nc', '-p5-nc', '-p25-nc')
at_least_mins = c(0, 3, 4)  # needs to have at least these minutes of data
scans_file = '/Volumes/Labs/AROMA_ICA/filtered_minFD_2scans.csv'
mvmt_file = '/Volumes/Labs/AROMA_ICA/xcp_movement.csv'

df = read.csv(scans_file)
mvmt = read.csv(mvmt_file)
pdist = c()
rdist = c()
header = c()
for (p in pipelines) {
    pipe_dir = sprintf('~/data/AROMA_ICA/connectivity/xcpengine_output_AROMA%s/', p)
    cat(sprintf('Reading connectivity data from %s\n', pipe_dir))
    for (tmin in at_least_mins) {
        fc = c()
        qc = c()
        # reading quality metric for all scans
        for (s in df$subj[1:10]) {
            midx = mvmt$subj==s & mvmt$pipeline==p
            # if scan was successfully processed in this pipeline
            if (mvmt[midx,]$fcon &&
                ((mvmt[midx,]$TRs_used * 2.5 / 60) >= tmin)) {
                fname = sprintf('%s/%s_power264_network.txt', pipe_dir, s)
                data = read.table(fname)[, 1]
                fc = cbind(fc, data)
                qc = c(qc, mvmt[midx, 'meanFD'])
            }
        }
        # compute correlations
        cat(sprintf('Computing correlations for at least %d minutes\n', tmin))
        ps = c()
        rs = c()
        for (conn in 1:nrow(fc)) {
            res = cor.test(fc[conn, ], qc)
            rs = c(rs, res$estimate)
            ps = c(ps, res$p.value)
        }
        rdist = cbind(rdist, rs)
        pdist = cbind(pdist, ps)
        header = c(header, sprintf('%dmin%s', tmin, p))
    }
}

# computing metrics and plotting
colnames(pdist) = header
colnames(rdist) = header
prop_sig = colSums(pdist<.05) / nrow(fc) * 100
par(mar=c(5,7,1,1))
barplot(prop_sig, main="QC-FC p < .05 uncorrected connection",
        ylab="Pipeline", xlab='% conn', horiz=TRUE, las=2)
dev.new()
boxplot(rdist, main="QC-FC", ylab="Pipeline", xlab='Pearson r', las=2)