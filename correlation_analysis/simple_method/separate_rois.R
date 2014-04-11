thresh=.5
hemi = 'R'
other = 'gp'
time = 'baseline'
g1 = 'remission'
g2 = 'persistent'
g3 = 'NV'
conn_thresh=.39

mat = readMat('~/Documents/surfaces/IMAGING_TOOLS/thalamus.mat')
if (hemi=='R') {
    coordT = t(mat[[6]])
    nbr = mat[[7]]
} else {
    coordT = t(mat[[2]])
    nbr = mat[[3]]
}
mat = readMat(sprintf('~/Documents/surfaces/IMAGING_TOOLS/%s.mat',other))
if (hemi=='R') {
    coordO = t(mat[[6]])
} else {
    coordO = t(mat[[2]])
}

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

# the idea is to assign a number to each cluster of continuous good voxels.
# then we can remove the clusters with smallest number of voxels
fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh0.50_%sOnly.txt', 
                hemi, other, time, g1)
res = read.table(fname, skip=3)
roi = res[,1]>conn_thresh

clusters = vector(mode='numeric', length=length(roi))
clusters[roi] = -1 # everything -1 needs to be painted
cl = 1
while (sum(clusters<0)>0) {
    v = which(clusters<0)[1]
    clusters[v] = cl
    paint_nbrs = intersect(nbr[v,],which(roi))
    fresh_nbrs = paint_nbrs[clusters[paint_nbrs]<0]
    while (length(fresh_nbrs) > 0) {
        clusters[fresh_nbrs] = cl
        v = fresh_nbrs
        paint_nbrs = intersect(nbr[v,],which(roi))
        fresh_nbrs = paint_nbrs[clusters[paint_nbrs]<0]
    }
    cl = cl + 1
}

# now we paint the top X clusters
num_clusters = 5
cl_rois = vector(mode='numeric', length=length(roi))
sorted_clusters = sort(table(clusters),index.return=T,decreasing=T)
print(sorted_clusters)
for (i in 2:(num_clusters+1)) {
    cl_rois[clusters==as.numeric(names(sorted_clusters)[i])] = i-1
}
# fname = sprintf('~/data/results/simple/%sthalamus2%s_ROIs_%s_thresh%.2f_%s.txt', 
#                 hemi, other, time, thresh, g1)
fname = sprintf('~/data/results/simple/%sthalamus2%s_ROIs_%s_thresh%.2f_%sOnly.txt', hemi, other, time, thresh, g1)
write_vertices(cl_rois, fname, c(g1))

# finally, for each roi, create the a file for its connections
cnt = 1
for (g in c(g1, g2, g3)) {
    load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                 hemi, other, time, g))
    eval(parse(text=sprintf('es%d = abs(es)',cnt)))
    eval(parse(text=sprintf('bes%d = binarize(es%d,thresh)',cnt, cnt)))
    cnt = cnt + 1
}
m = matrix(data=F, nrow=dim(es1)[1], ncol=dim(es1)[2])
conn_diff = setdiff(which(bes1),union(which(bes2),which(bes3)))
m[conn_diff] = T
# m = bes1
for (i in 1:num_clusters) {
    myroi = which(cl_rois==i)
    paint_voxels = which(colSums(m[myroi,])>0)
    data = vector(mode='numeric',length=dim(m)[2])
    for (v in 1:length(paint_voxels)) {
       data[paint_voxels[v]] = sum(m[myroi, paint_voxels[v]])/length(myroi)
    }
    # fname = sprintf('~/data/results/simple/%s%s_ROI%d_%s_thresh%.2f_%s.txt', 
    #                 hemi, other, i, time, thresh, g1)
    fname = sprintf('~/data/results/simple/%s%s_ROI%d_%s_thresh%.2f_%sOnly.txt', hemi, other, i, time, thresh, g1)
    write_vertices(data, fname, c(g1))
}