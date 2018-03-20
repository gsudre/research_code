merge_func = function(id, df1, df2, my_ids, x.id, x.date, y.id, y.date) {
  eval(parse(text=sprintf('d1 = subset(df1, %s==id)', x.id)))
  eval(parse(text=sprintf('d2 = subset(df2, %s==id)', y.id)))
  # if the id is not in df2
  if (nrow(d2) == 0) {
    d3 = merge(d1,d2,by.x=x.id, by.y=y.id, all.x=T)
  } else {
    d1$indices <- sapply(d1[, eval(x.date)], function(d) which.min(abs(d2[, eval(y.date)] - d)))
    d2$indices <- 1:nrow(d2)
    d3 = merge(d1,d2,by.x=c(x.id,'indices'), by.y=c(y.id, 'indices'))
    d3$indices = NULL
  }
  if (x.date == y.date) {
    x.date = sprintf('%s.x', x.date)
    y.date = sprintf('%s.y', y.date)
  }
  d3$dateX.minus.dateY.months = as.numeric(d3[, eval(x.date)] - d3[, eval(y.date)]) / 30
  return(d3)
}

mergeOnClosestDate = function(df1, df2, my_ids, x.id='MRN', x.date='DOA', y.id='MRN', y.date='DOA') {
  # replace %Y format by %y to make reading it in easier (if needed)
  df1[, eval(x.date)] = gsub("[0-9]{2}([0-9]{2})$", "\\1", df1[, eval(x.date)]) 
  df2[, eval(y.date)] = gsub("[0-9]{2}([0-9]{2})$", "\\1", df2[, eval(y.date)])
  # convert from factors to dates
  df1[, eval(x.date)] = as.Date(df1[, eval(x.date)], format='%m/%d/%y')
  df2[, eval(y.date)] = as.Date(df2[, eval(y.date)], format='%m/%d/%y')
  
  # apply the merge function to all ids
  merged_ids <- lapply(my_ids, merge_func, df1, df2, my_ids, x.id, x.date, y.id, y.date)
  # bind by rows the ID-specific merged dataframes
  res_df = do.call(rbind, merged_ids)

  # reformat dates to be in the usual format, instead of separated by hyphens
  res_df[, eval(x.date)] = format(res_df[, eval(x.date)], format='%m/%d/%Y')
  res_df[, eval(y.date)] = format(res_df[, eval(y.date)], format='%m/%d/%Y')
  return(res_df)
}

# So, an example on how to run it would be:

# read in both files
df1 = read.csv('~/data/baseline_prediction/stripped/gf_clinical.csv')
df2 = read.table('~/Downloads/Results 1.txt', sep='\t', header=1)
# Select the set of unique IDs you want to merge
my_ids = unique(df1$MRN)  # or use the intersect of IDs of both dfs
# run the command, specifying the column names if different than MRN and DOA
df3 = mergeOnClosestDate(df1, df2, my_ids, y.id='Medical.Record...MRN', y.date='record.date.collected...GAS')
# write out the results
write.csv(df3, row.names=F, file='~/tmp/merged.csv')

