# Collect the results from the different grids in FATCAT's output. Assumes
# tables have already been split with something like this:
#
# for f in `/bin/ls -1 *grid`; do
#      s=`echo $f | cut -d"." -f 1`;
#      echo $s;
#      csplit --quiet --prefix=${s}. ${s}.pr00_000.grid /^#/ {*};
#      mv ${s}.?? parsed/;
# done
#
# GS 07/2018

subj_dir = '~/data/fatcat/parsed/'
subjs = as.numeric(read.table(sprintf('%s/paul_parsed.txt', subj_dir))[,1])
expected_rois = 87

library(plyr)  # for rbind.fill

data = c()
for (s in subjs) {
  print(s)
  subj_data = c(s)
  # file numbers with the data matrices
  files = 4:18
  # read in the ROI labels
  titles = read.table(sprintf('%s/%04d.03', subj_dir, s),
                      stringsAsFactors=F)[1,]
    for (f in files) {
        fpath = sprintf('%s/%04d.%02d', subj_dir, s, f)
        # figure out the type of data in the matrix
        title.line <- readLines(fpath, n=1)
        dtype = substring(title.line, 3)
        # read in the actual data and get just the upper triangle
        a = read.table(fpath)
        b = a[upper.tri(a, diag=TRUE)]
        # format a header for the vectorized version of the table
        w = which(upper.tri(a, diag=TRUE), arr.ind = TRUE)
        header = sapply(1:length(b),
                        function(i) sprintf('%s:%s.TO.%s', dtype,
                                            titles[1, w[i,1]], titles[1,w[i,2]]))
        names(b) = header
        # concatenate vectorized matrices for the same mask id in the same row
        subj_data = c(subj_data, b)    
    }
    # stack each mask id vector onto each other as rows
    names(subj_data)[1] = 'mask.id'
  if (length(titles) == expected_rois) {
    data = rbind(data, subj_data)
} else {
	# this is much slower than regular bind, so we only do it when needed
    print(sprintf('Different number of ROIs (%d): filling missing with NA', length(titles)))
	data = rbind.fill(as.data.frame(data), as.data.frame(t(subj_data)))
}
}
# rename it so that each row is a mask id
save(data, file=sprintf('%s/output.RData', subj_dir))
write.csv(data, file=sprintf('%s/output.csv', subj_dir), row.names=F)
