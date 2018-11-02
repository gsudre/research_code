# Generates different network metrics given a matrix file
# Matrix file should be a csv in the format maskid by connection, where
# connection is x_TO_y.
# 
# Metrics inspired by "Complex brain networks: graph theoretical analysis of
# structural and functional systems", by Bullmore and Sporns.
# 
# GS, 11/2018


fname = '~/data/baseline_prediction/rsfmri/binaryP05_aparc.a2009s_pearson.csv'
# define any vertices that shouldn't be part of the network
rm_vertices = c('CSF', 'Ventricle$', 'Pallidum$', 'Brain.Stem',
                'Accumbens.area$', 'VentralDC$', 'vessel$', 'Cerebral',
                'choroid', 'Lat.Vent$', 'White.Matter$', 'hypointensities',
                '^CC', 'unknown$', 'Chiasm$', 'Cerebellum.Cortex$')


library(igraph)
library(moments)

data = read.csv(fname, row.names=1)

from = sapply(colnames(data), function(x) strsplit(x, '_TO_')[[1]][1])
to = sapply(colnames(data), function(x) strsplit(x, '_TO_')[[1]][2])
rm_me = c()
for (v in rm_vertices) {
    rm_me = c(rm_me, which(grepl(v, from)))
    rm_me = c(rm_me, which(grepl(v, to)))
}
rm_me = unique(rm_me)

apl = c()
density = c()
assor = c()
kur = c()
ske = c()
summaries = c()
mot3 = c()
mot4 = c()
fgre_lev = c()
fgre_mod = c()
lou_lev = c()
lou_mod = c()

# each mask id in the file is an individual network
for (m in 1:nrow(data)) {
    d = data.frame(to=to, from=from)
    keep_me = setdiff(1:nrow(d), rm_me)
    d = d[keep_me, ]
    d$weight = t(data[m, keep_me])
    d = d[d$weight != 0, ]
    g = graph_from_data_frame(d, directed=F)
    apl = c(apl, average.path.length(g))
    density = c(density, edge_density(g))
    assor = c(assor, assortativity.degree(g))
    ddist = degree.distribution(g)
    kur = c(kur, kurtosis(ddist))
    ske = c(ske, skewness(ddist))
    summaries = rbind(summaries, summary(ddist))
    mot3 = c(mot3, count_motifs(g, size=3))
    mot4 = c(mot4, count_motifs(g, size=4))
    fgre_lev = c(fgre_lev, length(cluster_fast_greedy(g)))
    fgre_mod = c(fgre_mod, modularity(cluster_fast_greedy(g)))
    lou_lev = c(lou_lev, length(cluster_louvain(g)))
    lou_mod = c(lou_mod, modularity(cluster_louvain(g)))
}
res = data.frame(maskid=rownames(data),
                 average_path_length=apl,
                 connection_density=density,
                 assortativity=assor,
                 motifs3=mot3,
                 motifs4=mot4,
                 levels_greedy=fgre_lev,
                 modularity_greedy=fgre_mod,
                 levels_louvain=lou_lev,
                 modularity_louvain=lou_mod,
                 degree_dist_kurtosis=kur,
                 degree_dist_skewness=ske)
colnames(summaries) = c('degree_dist_min', 'degree_dist_1stQ',
                        'degree_dist_median', 'degree_dist_mean',
                        'degree_dist_3rdQ', 'degree_dist_max')
res = cbind(res, summaries)
out_fname = gsub('.csv', '_net_props.csv', fname)
write.csv(res, file=out_fname, row.names=F)

# TODO: 
# hub score : one per vertex?
# clustering coefficient?
# centrality: alpha? kleinbergs? betweeness? closeness? one per vertex too
# robustness? 
