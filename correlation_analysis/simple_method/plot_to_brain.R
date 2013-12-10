thresh=.4
str = 'esThalamusRstriatumR'
time = 'delta'
g1 = 'remission'
g2 = 'persistent'

for (g in c('remission','persistent')) {
    load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,f,time))
    eval(parse(text=sprintf('%s = %s',g,str)))
    eval(parse(text=sprintf('%s[%s<thresh] = 0',g,g)))
    eval(parse(text=sprintf('%s[%s>=thresh] = 1',g,g)))
}

eval(parse(text=sprintf('m = %s - %s', g1, g2))) # in g1 but not in g2
eval(parse(text=sprintf('m = %s - %s', g2, g1))) # in g2 but not in g1
eval(parse(text=sprintf('m = %s == %s', g1, g2))) # in g1 and g2

# first dimension is the thalamus, so assign colors to it
paint_voxels = which(rowSums(m)>0)
data = vector(mode='numeric',length=dim(m)[1])
data[paint_voxels] = 1
write_vertices(data, '~/data/results/structural_v2/test_thalamus.txt', c('val'))

# then only plot the other region for parts connected to a specific roi in the thalamus
roi = paint_voxels[paint_voxels<2200 & paint_voxels>1800]
paint_voxels = which(colSums(m[roi,])>0)
data = vector(mode='numeric',length=dim(m)[2])
data[paint_voxels] = 1
write_vertices(data, '~/data/results/structural_v2/test_striatum.txt', c('val'))