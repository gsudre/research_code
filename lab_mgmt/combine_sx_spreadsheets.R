library(gdata)

dir_name = '/Volumes/Shaw/Clinical_Interviews/'
caadid_fname = sprintf('%s/CAADID data 5-9-18.xlsx', dir_name)
nv_fname = sprintf('%s/nv_interviews_051418.xlsx', dir_name)
dica_fname = sprintf('%s/DICA 5-8-18.xlsx', dir_name)
caadidS_fname = sprintf('%s/Simplex/CAADID data simplex.xlsx', dir_name)
nvS_fname = sprintf('%s/Simplex/nv_interviews_simplex.xlsx', dir_name)
dicaS_fname = sprintf('%s/Simplex/DICA simplex.xlsx', dir_name)
# all simplex stuff, old papers



# cleaning up CAADID
print(caadid_fname)
df = read.xls(caadid_fname, sheet = 1, header = TRUE)
print(sprintf('Found %d records.', nrow(df)))
caadid = df[, c('MRN', 'date.collected', 'inatt.as.adult', 'hi.as.adult')]
colnames(caadid) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')
caadid$source = 'CAADID'
other_dx = c("Other.dx", "Other.dx2", "Other.dx3", "Other.dx4", "Other.dx5")
caadid$other_dx = do.call(paste, df[, other_dx])

# cleaning up NV interviews
print(nv_fname)
df = read.xls(nv_fname, sheet = 1, header = TRUE)
print(sprintf('Found %d records.', nrow(df)))
nv = df[, c('Medical.Record...MRN...Subjects', 'record.date.collected...NV.Interview',
            'inattention.symptoms', 'HI.symptoms')]
colnames(nv) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')
nv$source = 'NV_interview'
other_dx = c("DX1...NV.Interview", "DX2...NV.Interview", "DX3...NV.Interview")
nv$other_dx = do.call(paste, df[, other_dx])

sx = rbind(caadid, nv)

# cleaning up DICA interviews
print(dica_fname)
df = read.xls(dica_fname, sheet = 1, header = TRUE)
print(sprintf('Found %d records.', nrow(df)))
dica = df[, c('ID', 'Date', 'X..of.inatten', 'X..H.I', 'Comments', 'Meds')]
# keep all entries off medication
dica_off = dica[grepl('off', dica$Meds, ignore.case=T), 1:5]
dica_off$source = 'DICA_off'
# for the on meds, just keep them if there isn't an off meds entry yet
dica_on = dica[grepl('on', dica$Meds, ignore.case=T), 1:5]
dica_on$source = 'DICA_on'
keep_me = c()
for (i in 1:nrow(dica_on)) {
  idx = dica_off$ID==dica_on[i,]$ID & dica_off$Date==dica_on[i,]$Date
  if (sum(idx) == 0) {
    keep_me = c(keep_me, i)
  }
}
dica_clean = rbind(dica_off, dica_on[keep_me,])
print(sprintf('Cleaned to %d records.', nrow(dica_clean)))
colnames(dica_clean) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi', 'other_dx', 'source')
sx = rbind(sx, dica_clean)

# cleaning up CAADID simplex
print(caadidS_fname)
df = read.xls(caadidS_fname, sheet = 1, header = TRUE)
print(sprintf('Found %d records.', nrow(df)))
caadidS = df[, c('MRN', 'date.collected', 'inatt.as.adult', 'hi.as.adult')]
colnames(caadidS) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')
caadidS$source = 'CAADID_simplex'
other_dx = c("SCID.dx1", "SCID.dx2", "SCID.dx3")
caadidS$other_dx = do.call(paste, df[, other_dx])
sx = rbind(sx, caadidS)

# cleaning up NV interviews simplex
print(nvS_fname)
df = read.xls(nvS_fname, sheet = 1, header = TRUE)
print(sprintf('Found %d records.', nrow(df)))
nvS = df[, c('Medical.Record...MRN...Subjects', 'record.date.collected...NV.Interview',
            'inattention.symptoms', 'HI.symptoms')]
colnames(nvS) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi')
nvS$source = 'NV_interview_simplex'
other_dx = c("DX1...NV.Interview", "DX2...NV.Interview", "DX3...NV.Interview")
nvS$other_dx = do.call(paste, df[, other_dx])
sx = rbind(sx, nvS)

# cleaning up DICA interviews simplex
print(dicaS_fname)
df = read.xls(dicaS_fname, sheet = 'DICA', header = TRUE)
print(sprintf('Found %d records.', nrow(df)))
dicaS = df[, c('MR', 'Date', 'X..of.inatten', 'X..H.I', 'Comments', 'Meds')]
# keep all entries off medication
dicaS_off = dicaS[grepl('off', dicaS$Meds, ignore.case=T), 1:5]
dicaS_off$source = 'DICA_off'
# for the on meds, just keep them if there isn't an off meds entry yet
dicaS_on = dicaS[grepl('on', dicaS$Meds, ignore.case=T), 1:5]
dicaS_on$source = 'DICA_on'
keep_me = c()
for (i in 1:nrow(dicaS_on)) {
  idx = dicaS_off$ID==dicaS_on[i,]$ID & dicaS_off$Date==dicaS_on[i,]$Date
  if (sum(idx) == 0) {
    keep_me = c(keep_me, i)
  }
}
dicaS_clean = rbind(dicaS_off, dicaS_on[keep_me,])
print(sprintf('Cleaned to %d records.', nrow(dicaS_clean)))
colnames(dicaS_clean) = c('MRN', 'DOA', 'SX_inatt', 'SX_hi', 'other_dx', 'source')
sx = rbind(sx, dicaS_clean)

# convert the different date formats across sheets
idx = grepl('-', x)
x = as.character(sx$DOA)
new_date = vector(length=length(sx$DOA))
new_date[idx] = format(as.Date(x[idx], format='%Y-%m-%d'), format='%m/%d/%Y')
idx = grepl('/', x)
new_date[idx] = format(as.Date(x[idx], format='%m/%d/%y'), format='%m/%d/%Y')
sx$DOA = new_date
# remove any errors
sx = sx[which(new_date~=F), ]
