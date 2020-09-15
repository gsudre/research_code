# adds columns to the compiled sx spreadsheet
sx_fname = '~/tmp/clinical_09142020.csv'
dob_fname = '~/data/DOBs.csv'

# adding DOB so we can compute age
df = read.csv(sx_fname)
dobs = read.csv(dob_fname)

# there are some old records that we won't have DOB in Labmatrix. 
data = merge(df, dobs, by='MRN', all.x=T, all.y=F)
data$DX_dsm5 = NA

# records in Philip's files and childhood CAADIA records are special
idx = which(data$source=='PhilipsOldFiles')
data[idx, 'DX_dsm5'] = data[idx, 'other_dx']
idx = which(data$DOA=='child')


today = format(Sys.time(), "%m%d%Y")
write.csv(sx, file=sprintf('~/tmp/augmented_clinical_%s.csv', today), row.names=F)
