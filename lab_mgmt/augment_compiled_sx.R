# adds columns to the compiled sx spreadsheet
sx_fname = '~/tmp/clinical_09152020.csv'
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

# marking ever ADHD across observations
data$everADHD_dsm5 = NA
for (s in unique(data$MRN)) {
    idx = which(data$MRN==s)
    sdata = data[idx,]
    if (any(sdata$DX_dsm5=='other')) {
        data[idx, 'everADHD_dsm5'] = 'other'
    } else if (any(sdata$DX_dsm5=='ADHD')) {
        data[idx, 'everADHD_dsm5'] = 'yes'
    } else {
        data[idx, 'everADHD_dsm5'] = 'no'
    }
}

# marking outcome for adults only
data$outcome_dsm5 = NA
for (s in unique(data$MRN)) {
    idx = which(data$MRN==s)
    # we need at least two measurement to call outcome
    if (length(idx) > 1) {
        sdata = data[idx,]
        sage = sort(sdata$age_at_clinical, index.return=T, decreasing=T)
        if (any(sdata$DX_dsm5=='other')) {
            data[idx, 'outcome_dsm5'] = 'other'
        # kids don't count as outcome
        } else if (sage$x[1] < 17) {
            data[idx, 'outcome_dsm5'] = NA
        # adult is only NV if always NV
        } else if (all(sdata$DX_dsm5 == 'NV')) {
            data[idx, 'outcome_dsm5'] = 'NV'
        # if last observation is ADHD, then it persists
        } else if (sdata[sage$ix[1], 'DX_dsm5'] == 'ADHD') {
            data[idx, 'outcome_dsm5'] = 'persistent'
        } else {
            data[idx, 'outcome_dsm5'] = 'remission'
        }
    }
}

# mark only people for whom we have SX, where NV needs to be 0, 1 or 2 only.
# ADHD needs to meet criteria, leaving a good amount of 'others'
data$DX_nv012 = NA
for (i in 1:nrow(data)) {
    if (!is.na(data[i, 'age_at_clinical']) &&
        !any(is.na(data[i, c('SX_inatt', 'SX_hi')]))) {
        # some people from old papers don't have DOA
        if (data[i, 'age_at_clinical'] >= 17) {
            threshold = 5
        } else {
            threshold = 6
        }
        if (data[i, 'SX_inatt'] >= threshold ||
            data[i, 'SX_hi'] >= threshold) {
            data[i, 'DX_nv012'] = 'ADHD'
        } else if (data[i, 'SX_inatt'] <= 2 && data[i, 'SX_hi'] <= 2) {
            data[i, 'DX_nv012'] = 'NV'
        }
    }
}
# marking ever ADHD across observations
data$everADHD_nv012 = NA
for (s in unique(data$MRN)) {
    idx = which(data$MRN==s)
    sdata = data[idx,]
    if (any(is.na(sdata$DX_nv012))) {
        data[idx, 'everADHD_nv012'] = NA
    } else if (any(sdata$DX_nv012=='ADHD')) {
        data[idx, 'everADHD_nv012'] = 'yes'
    } else {
        data[idx, 'everADHD_nv012'] = 'no'
    }
}

today = format(Sys.time(), "%m%d%Y")
write.csv(data,
          file=sprintf('~/tmp/augmented_clinical_%s.csv', today), row.names=F)
