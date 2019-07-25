# plots the % of significant QC-FC connections and the overal pearson R
# distribution, following the analysis in 
# - Ciric, Rastko, Daniel H. Wolf, Jonathan D. Power, David R. Roalf, Graham L.
#   Baum, Kosha Ruparel, Russell T. Shinohara, et al. “Benchmarking of
#   Participant-Level Confound Regression Strategies for the Control of Motion
#   Artifact in Studies of Functional Connectivity.” NeuroImage, Cleaning up the
#   fMRI time series: Mitigating noise with advanced acquisition and correction
#   strategies, 154 (July 1, 2017): 174–87.
#   https://doi.org/10.1016/j.neuroimage.2017.03.020.
# - Parkes, Linden, Ben Fulcher, Murat Yücel, and Alex Fornito. “An Evaluation
#   of the Efficacy, Reliability, and Sensitivity of Motion Correction
#   Strategies for Resting-State Functional MRI.” NeuroImage 171 (May 1, 2018):
#   415–36. https://doi.org/10.1016/j.neuroimage.2017.12.073.
# 
# Same as its parent function, but here do some filtering by FD

pipeline = ''
fd_thresh = c(13, 2, 1, .44, .18)
mvmt_file = '/Volumes/Labs/AROMA_ICA/xcp_movement.csv'

# looking at best fo 2 or 3 scans!!!
scans_file = '/Volumes/Labs/AROMA_ICA/filtered_minFD_2scans.csv'
scans = read.csv(scans_file)
subjs = unique(as.character(scans$subj))

mvmt = read.csv(mvmt_file)
pdist = c()
rdist = c()
header = c()
pipe_dir = sprintf('~/data/AROMA_ICA/connectivity/xcpengine_output_AROMA%s/', pipeline)
cat(sprintf('Reading connectivity data from %s\n', pipe_dir))
for (t in fd_thresh) {
    fc = c()
    qc = c()
    sex = c()
    age = c()
    # reading quality metric for all scans
    for (s in subjs) {
        midx = mvmt$subj==s & mvmt$pipeline==pipeline
        # if scan was successfully processed in this pipeline
        if (mvmt[midx,]$fcon && mvmt[midx,]$meanFD < t) {
            fname = sprintf('%s/%s_power264_network.txt', pipe_dir, s)
            data = read.table(fname)[, 1]
            fc = cbind(fc, data)
            qc = c(qc, mvmt[midx, 'meanFD'])
            sex = c(sex, scans[scans$subj == s, 'Sex'])
            age = c(age, scans[scans$subj == s, 'age_at_scan'])
        }
    }
    # compute correlations
    cat(sprintf('Computing correlations for FD < %.2f (%d scans)\n',
                t, length(qc)))
    sex = as.factor(sex)
    fc_resids = fc
    for (conn in 1:nrow(fc)) {
        fc_resids[conn, ] = residuals(lm(fc[conn, ] ~ sex + age,
                                                na.action=na.exclude))
    }
    ps = c()
    rs = c()
    for (conn in 1:nrow(fc)) {
        res = cor.test(fc_resids[conn, ], qc, method='spearman')
        rs = c(rs, res$estimate)
        ps = c(ps, res$p.value)
    }
    rdist = cbind(rdist, rs)
    pdist = cbind(pdist, ps)
    header = c(header, sprintf('%sFDlt%.2f', pipeline, t))
}

# computing metrics and plotting
colnames(pdist) = header
colnames(rdist) = header
prop_sig = colSums(pdist<.05) / nrow(fc) * 100
dev.new()
par(mar=c(5,7.5,1,1))
barplot(prop_sig, main="QC-FC p < .05 uncorrected connection",
        xlab='% conn', horiz=TRUE, las=2)

pdist2 = pdist
for (i in 1:length(header)) {
    pdist2[, i] = p.adjust(pdist[, i], method='fdr')
}
prop_sig2 = colSums(pdist2<.05) / nrow(fc) * 100
dev.new()
par(mar=c(5,7.5,1,1))
barplot(prop_sig2, main="QC-FC q < .05",
        xlab='% conn', horiz=TRUE, las=2)

dev.new()
par(mar=c(7.5,4,1,1))
boxplot(rdist, main="QC-FC", ylab="Correlation", las=2)

# FC-QC to distance correlation
cat('Calculating distance matrix between spheres\n')
coords = read.csv('~/research_code/fmri/Neuron_consensus_264.csv')
dists = c()
for (i in 1:(nrow(coords)-1)) {
    for (j in (i+1):nrow(coords)) {
        dists = c(dists, sqrt(sum((coords[j,2:4] - coords[i,2:4])^2)))
    }
}
cat('Computing distance to FC-QC correlations\n')
rhos = c()
for (p in 1:ncol(pdist)) {
    res = cor.test(pdist[, p], dists, method='spearman')
    rhos = c(rhos, res$estimate)
}
names(rhos) = header
dev.new()
par(mar=c(5,7,1,1))
barplot(rhos, main="QC-FC distance dependence",
        xlab='Spherman rho', horiz=TRUE, las=2)
