thresh=.5
hemi = 'R'
other = 'striatum'
time = 'baseline'
g1 = 'remission'
g2 = 'persistent'
g3 = 'NV'

str = sprintf('esThalamus%s%s%s',hemi,other,hemi)
for (g in c(g1, g2, g3)) {
    load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,f,time))
    eval(parse(text=sprintf('%s = %s',g,str)))
    eval(parse(text=sprintf('%s[%s<thresh] = 0',g,g)))
    eval(parse(text=sprintf('%s[%s>=thresh] = 1',g,g)))
}

# eval(parse(text=sprintf('m = %s - %s', g3, g2))) # only in the first group (out of 2)
eval(parse(text=sprintf('m = %s - %s - %s', g1, g2, g3))) # g1 only
# eval(parse(text=sprintf('m = %s == %s', g1, g2))) # in g1 and g2

# first dimension is the thalamus, so assign colors to it
paint_voxels = which(rowSums(m)>0)
data = vector(mode='numeric',length=dim(m)[1])
# paint each vertex in the thalamus with how many voxels it connects to
# this way we can get a sense of how sparse out plot willl be for the other brain region
for (v in 1:length(paint_voxels)) {
    data[paint_voxels[v]] = sum(m[paint_voxels[v],])/dim(m)[2]
}
fname = sprintf('~/data/results/structural_v2/%sthalamus2%s_%s_%sOnly.txt', hemi, other, time, g1)
write_vertices(data, fname, c('val'))

# then only plot the other region for parts connected to a specific roi in the thalamus
roi = which(data>.1)
paint_voxels = which(colSums(m[roi,])>0)
data = vector(mode='numeric',length=dim(m)[2])
for (v in 1:length(paint_voxels)) {
    data[paint_voxels[v]] = sum(m[roi, paint_voxels[v]])/length(roi)
}
fname = sprintf('~/data/results/structural_v2/%s%s_%s_%sOnly.txt', hemi, other, time, g1)
write_vertices(data, fname, c('val'))