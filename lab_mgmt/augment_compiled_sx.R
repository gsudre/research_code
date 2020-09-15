# adds columns to the compiled sx spreadsheet
sx_fname = '~/tmp/clinical_09142020.csv'
dob_fname = '~/data/DOBs.csv'

# adding DOB so we can compute age
df = read.csv(sx_fname)
dobs = read.csv(dob_fname)

# there are some old records that we won't have DOB in Labmatrix. 
data = merge(df, dobs, by='MRN', all.x=T, all.y=F)
data$DX_dsm5 = NA
data$age_at_clinical = NA

# records in Philip's files and childhood CAADIA records are special
idx = which(data$source=='PhilipsOldFiles')
data[idx, 'DX_dsm5'] = data[idx, 'other_dx']
data[which(data$DX_dsm5 == 'ADD'), 'DX_dsm5'] = 'ADHD'
data[which(data$DX_dsm5 == 'ADT'), 'DX_dsm5'] = 'ADHD'
data[which(data$DX_dsm5 == 'ADT(unaffected)'), 'DX_dsm5'] = 'ADHD'
data[which(data$DX_dsm5 == 'NV(ADDsib)'), 'DX_dsm5'] = 'NV'
other_dx = c('EMOTIOANL_DYSREG' ,'LD', 'Psychosis_NOS', 'XNV')
idx = which(data$DX_dsm5 %in% other_dx)
data[idx, 'DX_dsm5'] = 'other'
idx = which(data$DOA=='child')
for (i in idx) {
    if (data[i, 'SX_inatt'] >= 6 || data[i, 'SX_hi'] >= 6) {
        data[i, 'DX_dsm5'] = 'ADHD'
    } else {
        data[i, 'DX_dsm5'] = 'NV'
    }
    data[i, 'age_at_clinical'] = 'child'
}

# calculating age at assessment and DX whenever possible
for (i in 1:nrow(data)) {
    if (!is.na(data[i, 'DOB']) && is.na(data[i, 'DX_dsm5'])) {
        doa = as.Date(data[i, 'DOA'], format='%m/%d/%y')
        dob = as.Date(data[i, 'DOB'], format='%m/%d/%Y')
        data[i, 'age_at_clinical'] = as.numeric(doa - dob)/365.25
        # some people from old papers don't have DOA
        if (is.na(data[i, 'age_at_clinical'])) {
            data[i, 'DX_dsm5'] = data[i, 'other_dx']
        } else {
            if (data[i, 'age_at_clinical'] >= 17) {
                threshold = 5
            } else {
                threshold = 6
            }
            if (data[i, 'SX_inatt'] >= threshold ||
                data[i, 'SX_hi'] >= threshold) {
                data[i, 'DX_dsm5'] = 'ADHD'
            } else {
                data[i, 'DX_dsm5'] = 'NV'
            }
        }
    }
}



today = format(Sys.time(), "%m%d%Y")
write.csv(sx, file=sprintf('~/tmp/augmented_clinical_%s.csv', today), row.names=F)
