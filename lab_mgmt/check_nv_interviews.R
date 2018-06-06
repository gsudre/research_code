# checks the nv interviews for data corruption
# 

library(gdata)

seed_fname = '~/tmp/seed.xlsx'
df_seed = read.xls(seed_fname, sheet = 1, header = TRUE, colClasses='character')

mydir = '~/tmp/2018/philip'
fnames = dir(path=mydir)
for (fname in fnames) {
  print(fname)
  # df = read.xls(fname, sheet = 'philip_recode', header = TRUE, colClasses='character')
  df = read.xls(sprintf('%s/%s', mydir, fname), sheet = 2, header = TRUE, colClasses='character')
  nv1 = df[, c('Medical.Record...MRN...Subjects', 'record.date.collected...NV.Interview',
              'inattention.symptoms', 'HI.symptoms')]
  colnames(nv1) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')
  
  # # check if we have two of the same date for any subject
  # for (s in unique(nv1$MRN)) {
  #   for (d in unique(nv1[nv1$MRN==s, 'DOA'])) {
  #     idx = nv1$MRN==s & nv1$DOA==d
  #     if (sum(idx) > 1) {
  #       print(nv1[idx,])#sprintf('%s, %s', s, d))
  #     }
  #   }
  # }
  
  # check if all entries in seed file are still there
  for (r in 1:nrow(df_seed)) {
    idx = nv1$MRN==df_seed[r,'MRN'] & nv1$DOA==df_seed[r, 'DOA'] & nv1$SX_inatt==df_seed[r, 'SX_inatt'] & nv1$SX_hi==df_seed[r, 'SX_hi']
    if (sum(idx)==0) {
      print(sprintf('Cannot find seed %d', r))
      print(df_seed[r,])
    }
  }
  
}

# based on my tests, the biggest change happened form the 04232018 spreadsheet to 04/24/2018. So, let's see what the major differences are:
df = read.xls('~/tmp/2018/philip/nv_interviews_042318.xlsx', sheet = 'philip_recorde', header = TRUE, colClasses='character')
nv1 = df[, c('Medical.Record...MRN...Subjects', 'record.date.collected...NV.Interview',
             'inattention.symptoms', 'HI.symptoms')]
colnames(nv1) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')

df = read.xls('~/tmp/2018/philip/nv_interviews_060418.xlsx', sheet = 'philip_recode', header = TRUE, colClasses='character')
nv2 = df[, c('Medical.Record...MRN...Subjects', 'record.date.collected...NV.Interview',
             'inattention.symptoms', 'HI.symptoms')]
colnames(nv2) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')

print('These entries from 04/23 are different in current:')
for (r in 1:nrow(nv1)) {
  idx = nv2$MRN==nv1[r,'MRN'] & nv2$DOA==nv1[r, 'DOA'] & nv2$SX_inatt==nv1[r, 'SX_inatt'] & nv2$SX_hi==nv1[r, 'SX_hi']
  if (sum(idx)==0) {
    print(nv1[r,])
  }
}