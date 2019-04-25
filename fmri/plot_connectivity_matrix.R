# plots results form a connectivity matrix

con_col = 'phen'
val_col = 'h2r'
pval_col = 'h_pval'
df = read.csv('~/data/heritability_change/polygen_results_rsfmri_3min_n113_slopesZClean.csv')

rois = c()
for (r in df[, con_col]) {
    res = strsplit(as.character(r), split='.TO.')
    rois = c(rois, res[[1]][1], res[[1]][2])
}
rois = unique(rois)
nrois = length(rois)
cc.v = matrix(data=NA, nrow=nrois, ncol=nrois)
cc.p = matrix(data=NA, nrow=nrois, ncol=nrois)
colnames(cc.v) = rois
rownames(cc.v) = rois
colnames(cc.p) = rois
rownames(cc.p) = rois

for (r in 1:nrow(df)) {
    res = strsplit(as.character(df[r, con_col]), split='.TO.')
    cc.v[res[[1]][1], res[[1]][2]] = df[r, val_col]
    cc.v[res[[1]][2], res[[1]][1]] = df[r, val_col]
    cc.p[res[[1]][1], res[[1]][2]] = df[r, pval_col]
    cc.p[res[[1]][2], res[[1]][1]] = df[r, pval_col]
}

# examples in
# http://www.sthda.com/english/wiki/visualize-correlation-matrix-using-correlogram
corrplot(cc.v, type="upper", order="hclust", method='color',
         p.mat = cc.p, sig.level = 0.05, insig = "blank")