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

pipelines = c('')#'', '-p5', '-p25') #, '-gsr', '-gsr-p5', '-gsr-p25',
            #   '-gsr-p5-nc', '-gsr-p25-nc', '-p5-nc', '-p25-nc')
at_least_mins = c(0)#, 3, 4)  # needs to have at least these minutes of data
mvmt_file = '/Volumes/Labs/AROMA_ICA/xcp_movement.csv'
rm_outliers = F

# looking at best fo 2 or 3 scans!!!
scans_file = '/Volumes/Labs/AROMA_ICA/filtered_minFD_2scans.csv'
scans = read.csv(scans_file)
subjs = unique(as.character(scans$subj))

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
        sex = c()
        age = c()
        # reading quality metric for all scans
        for (s in subjs) {
            midx = mvmt$subj==s & mvmt$pipeline==p
            # if scan was successfully processed in this pipeline
            if (mvmt[midx,]$fcon &&
                ((mvmt[midx,]$TRs_used * 2.5 / 60) >= tmin)) {
                fname = sprintf('%s/%s_power264_network.txt', pipe_dir, s)
                data = read.table(fname)[, 1]
                fc = cbind(fc, data)
                qc = c(qc, mvmt[midx, 'meanFD'])
                sex = c(sex, scans[scans$subj == s, 'Sex'])
                age = c(age, scans[scans$subj == s, 'age_at_scan'])
            }
        }
        if (rm_outliers) {
            qc_mu = mean(qc)
            qc_sd = sd(qc)
            imgood = qc < (qc_mu + 3 * qc_sd) & qc > (qc_mu - 3 * qc_sd)
            qc = qc[imgood]
            fc = fc[, imgood]
            sex = sex[imgood]
            age = age[imgood]
            cat(sprintf('Removing %d outliers out of %d scans\n',
                        sum(!imgood), length(imgood)))
        }
        # compute correlations
        cat(sprintf('Computing correlations for at least %d minutes\n', tmin))
        sex = as.factor(sex)
        fc_resids = fc
        for (conn in 1:nrow(fc)) {
            fc_resids[conn, ] = residuals(lm(fc[conn, ] ~ sex + age,
                                                   na.action=na.exclude))
        }
        ps = c()
        rs = c()
        for (conn in 1:nrow(fc)) {
            res = cor.test(fc_resids[conn, ], qc)
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
dev.new()
par(mar=c(5,7.5,1,1))
barplot(prop_sig, main="QC-FC p < .05 uncorrected connection",
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
