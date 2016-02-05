# run it only after massaging the data!
brain_data = c('thalamus','striatum','gp')
for (b in brain_data) {
    for (h in c('L', 'R')) {
        verts = read.table(sprintf('~/data/structural/labels/%s_%s_labels.txt',
                                      b, h))[[1]]
        rois = unique(verts)
        rois = rois[rois>2]
        mydata = array(dim=c(dim(thalamusR)[1],length(rois)))
        cnt = 1
        for (r in rois) {
            idx = rois==r
            eval(parse(text=sprintf('roiData=rowSums(%s%s[,idx])', b, h)))
            mydata[, cnt] = roiData
            cnt = cnt + 1
        }
        eval(parse(text=sprintf('%s%s = mydata', b, h)))
    }
}