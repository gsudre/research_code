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

subj_dir = '~/tmp/parsed/'
subjs = c(0677, 0584, 0447) #read.table(sprintf('%s/paul_parsed.txt', subj_dir))[,1]
data = c()
for (s in subjs) {
  print(s)
  subj_data = c()
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
  data = rbind(data, subj_data)
}
# rename it so that each row is a mask id
rownames(data) = sapply(subjs, function(x) sprintf('%04d', x))
