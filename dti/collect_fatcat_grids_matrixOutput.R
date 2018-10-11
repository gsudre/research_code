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
# GS 10/2018

subj_dir = '~/ayaka/parsed/'
subjs = as.numeric(read.table(sprintf('%s/done.txt', subj_dir))[,1])

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
        # read in the actual data
        a = read.table(fpath)
        header = t(titles[1, ])
        write.table(a, file=sprintf('%s/%s_%04d.tsv', subj_dir, dtype, s),
                  row.names=F, col.names=F)   
    }
    # output column names
    write.table(header, file=sprintf('%s/rois_%04d.tsv', subj_dir, s), row.names=F,
                col.names=F, quote=F)
}

