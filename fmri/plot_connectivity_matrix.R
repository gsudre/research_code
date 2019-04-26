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
# LEft and RightVentralDC, Brainstem
rm_set = c(-82, -73, -1)
cc.v = cc.v[rm_set, ]
cc.p = cc.p[rm_set, ]
cc.v = cc.v[, rm_set]
cc.p = cc.p[, rm_set]

# examples in
# http://www.sthda.com/english/wiki/visualize-correlation-matrix-using-correlogram
corrplot(cc.v, type="upper", method='color',
         p.mat = cc.p, sig.level = .05/43.15, insig = "blank", is.corr=F, tl.cex=.5)