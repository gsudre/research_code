# Venn diagrams
thresh = .5
hemi = 'L'
other = 'striatum'
groups = c('remission', 'persistent', 'NV')
pct = .99
file = 'diff'

require(VennDiagram)
for (g in groups) {
    fname = sprintf('~/data/results/simple/%sthalamus2%s_%s_thresh0.50_%s.txt', 
                    hemi, other, f, g)
    res = read.table(fname, skip=3)
    conn_thresh = get_min_connectivity(other, f, hemi, pct, thresh)
    eval(parse(text=sprintf('%s = res[,1]>conn_thresh',g)))        
}
cat(conn_thresh, '\n')
fname = sprintf('~/data/results/simple/venn_%sthalamus2%s_%s_thresh0.50_nvVSper.tiff', 
                hemi, other, file)
venn.plot <- venn.diagram(list(NV = which(NV), persistent = which(persistent)), 
                               euler.d=TRUE, fill=c('green','red'), fname)
fname = sprintf('~/data/results/simple/venn_%sthalamus2%s_%s_thresh0.50_nvVSrem.tiff', 
                hemi, other, file)
venn.plot <- venn.diagram(list(NV = which(NV), remission = which(remission)), 
                          euler.d=TRUE, fill=c('green','blue'), fname)
fname = sprintf('~/data/results/simple/venn_%sthalamus2%s_%s_thresh0.50_perVSrem.tiff', 
                hemi, other, file)
venn.plot <- venn.diagram(list(persistent = which(persistent), remission = which(remission)), 
                          euler.d=TRUE, fill=c('red','blue'), fname)
fname = sprintf('~/data/results/simple/venn_%sthalamus2%s_%s_thresh0.50_all.tiff', 
                hemi, other, file)
venn.plot <- venn.diagram(list(NV = which(NV), persistent = which(persistent), 
                               remission = which(remission)), euler.d=TRUE, 
                          fill=c('green','red', 'blue'), fname)
