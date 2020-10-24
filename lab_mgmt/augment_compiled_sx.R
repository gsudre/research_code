# adds columns to the compiled sx spreadsheet
sx_fname = '~/tmp/clinical_10242020.csv'
dob_fname = '~/data/MRNs_DOBs_SIDs.csv'

# adding DOB so we can compute age
df = read.csv(sx_fname)
dobs = read.csv(dob_fname)

# there are some old records that we won't have DOB in Labmatrix.
data = merge(df, dobs, by='MRN', all.x=T, all.y=F)
if (sum(is.na(data$SID) & data$source!='PhilipsOldFiles') > 0) {
    print('Found people without SID not in PhilipsOldFiles!')
}
if (class(data$SX_inatt) != 'integer') {
    print('Could not convert SX_inatt to numeric!')
}
if (class(data$SX_hi) != 'integer') {
    print('Could not convert SX_hi to numeric!')
}
dxs = c('dsm', 'nv012')
for (dx in dxs) {
    data[, sprintf('DX_%s', dx)] = NA
}
data$age_clin = NA

# records in Philip's files and childhood CAADID records are special
idx = which(data$source=='PhilipsOldFiles')
for (dx in dxs) {
    dx_str = sprintf('DX_%s', dx)
    data[idx, dx_str] = data[idx, 'other_dx']
    data[which(data[, dx_str] == 'ADD'), dx_str] = 'ADHD'
    data[which(data[, dx_str] == 'ADT'), dx_str] = 'ADHD'
    data[which(data[, dx_str] == 'ADT(unaffected'), dx_str] = 'ADHD'
    data[which(data[, dx_str] == 'ADT(unaffected)'), dx_str] = 'ADHD'
    data[which(data[, dx_str] == 'NV(ADDsib)'), dx_str] = 'NV'
    other_dx = c('EMOTIOANL_DYSREG' ,'LD', 'Psychosis_NOS', 'XNV')
    idx = which(data[, dx_str] %in% other_dx)
    data[idx, dx_str] = 'other'
}
# working on CAADID child record now
idx = which(data$DOA=='child')
# DX starts as NA
for (i in idx) {
    if (all(!is.na(data[i, c('SX_inatt', 'SX_hi')]))) {
        if (data[i, 'SX_inatt'] >= 6 || data[i, 'SX_hi'] >= 6) {
            data[i, 'DX_dsm'] = 'ADHD'
            data[i, 'DX_nv012'] = 'ADHD'
        } else {
            data[i, 'DX_dsm'] = 'NV'
            if (data[i, 'SX_inatt'] <= 2 && data[i, 'SX_hi'] <= 2) {
                data[i, 'DX_nv012'] = 'NV'
            } 
        }
    }
    data[i, 'age_clin'] = 'child'
}

# CAADID entries that are NA for child sx are not informative
rm_child_sx = data$DOA=='child' & is.na(data$SX_inatt) & is.na(data$SX_hi)
data = data[which(!rm_child_sx), ]

# calculating age at assessment and DX whenever possible
for (i in 1:nrow(data)) {
    if (!is.na(data[i, 'DOB']) && !is.na(data[i, 'DOA']) &&
        data[i, 'DOA'] != 'child') {
        doa = as.Date(data[i, 'DOA'], format='%m/%d/%Y')
        dob = as.Date(data[i, 'DOB'], format='%m/%d/%Y')
        data[i, 'age_clin'] = as.numeric(doa - dob)/365.25
        # some people from old papers don't have DOA
        if (is.na(data[i, 'age_clin']) ||
            any(is.na(data[i, c('SX_inatt', 'SX_hi')])) &&
            data[i, 'source'] != 'PhilipsOldFiles') {
            data[i, 'DX_dsm'] = 'other'
        } else {
            if (data[i, 'age_clin'] >= 17) {
                threshold = 5
            } else {
                threshold = 6
            }
            if (is.na(data[i, 'DX_dsm'])) {
                if (data[i, 'SX_inatt'] >= threshold ||
                    data[i, 'SX_hi'] >= threshold) {
                    data[i, 'DX_dsm'] = 'ADHD'
                } else {
                    data[i, 'DX_dsm'] = 'NV'
                }
            }
            # for nv012 we need actual symptoms
            if (is.na(data[i, 'DX_nv012']) && !is.na(data[i, 'SX_inatt']) &&
                !is.na(data[i, 'SX_hi'])) {
                if (data[i, 'SX_inatt'] >= threshold ||
                    data[i, 'SX_hi'] >= threshold) {
                    data[i, 'DX_nv012'] = 'ADHD'
                } else if (data[i, 'SX_inatt'] <= 2 &&
                        data[i, 'SX_hi'] <= 2) {
                        data[i, 'DX_nv012'] = 'NV'
                }
            }
        }
    }
} 

# marking ever ADHD across observations
data$everADHD_dsm = NA
data$everADHD_nv012 = NA
for (s in unique(data$MRN)) {
    idx = which(data$MRN==s)
    for (dx in dxs) {
        sdata = data[idx,]
        dx_str = sprintf('DX_%s', dx)
        # we can't do much with DX == NA
        sdata = sdata[!is.na(sdata[, dx_str]), ]
        if (nrow(sdata) > 0) {
            if (any(sdata[, dx_str]=='ADHD')) {
                data[idx, sprintf('everADHD_%s', dx)] = 'yes'
            } else if (any(sdata[, dx_str] == 'other')) {
                data[idx, sprintf('everADHD_%s', dx)] = 'other'
            } else {
                data[idx, sprintf('everADHD_%s', dx)] = 'no'
            }
        }
    }
}

# marking outcome for adults only
for (dx in dxs) {
    out_str = sprintf('outcome_%s', dx)
    dx_str = sprintf('DX_%s', dx)
    data[, out_str] = NA
    for (s in unique(data$MRN)) {
        idx = which(data$MRN==s)
        # we need at least two measurement to call outcome
        if (length(idx) > 1) {
            sdata = data[idx,]
            # just for this analysis we replace 'child' by 0 so it's sorted
            # properly
            sdata[sdata$DOA=='child', 'age_clin'] = 0
            sage = sort(sdata$age_clin, index.return=T, decreasing=T)
            if (all(!is.na(sdata[, dx_str])) &&
                any(sdata[, dx_str]=='other')) {
                data[idx, out_str] = 'other'
            # kids don't count as outcome
            } else if (sage$x[1] < 17) {
                data[idx, out_str] = NA
            }
            # if any observations were NA dx, we cannot determine outcome
            else if (any(is.na(sdata[, dx_str]))) {
                data[idx, out_str] = NA
            } # adult is only NV if always NV
            else if (all(sdata[, dx_str] == 'NV')) {
                data[idx, out_str] = 'NV'
            # if last observation is ADHD, then it persists
            } else if (sdata[sage$ix[1], dx_str] == 'ADHD') {
                data[idx, out_str] = 'persistent'
            } else {
                data[idx, out_str] = 'remission'
            }
        }
    }
}

# let's add max ADHD symptoms
data$maxOverTimeSX_inatt = NA
data$maxOverTimeSX_hi = NA
for (s in unique(data$MRN)) {
    idx = which(data$MRN==s)
    sdata = data[idx,]
    if (!all(is.na(sdata$SX_inatt))) {
        data[idx, 'maxOverTimeSX_inatt'] = max(sdata$SX_inatt, na.rm=T)
    }
    if (!all(is.na(sdata$SX_hi))) {
        data[idx, 'maxOverTimeSX_hi'] = max(sdata$SX_hi, na.rm=T)
    }
}

# shaping it to a nicer column order
data = data[, c('MRN', 'SID', 'DOA', 'DOB', 'age_clin', 'SX_inatt',
                'SX_hi', 'source', 'DX_dsm', 'everADHD_dsm', 'outcome_dsm',
                'DX_nv012', 'everADHD_nv012', 'outcome_nv012',
                'maxOverTimeSX_inatt', 'maxOverTimeSX_hi', 'other_dx')]
data_anon = data
data_anon$MRN = data_anon$SID
data_anon$SID = NULL
colnames(data_anon)[1] = 'SID'
# removing people that don't have SIDs in Labmatrix 
rm_me = is.na(data_anon$SID)
data_anon = data_anon[!rm_me, ]
data_anon$DOA = NULL
data_anon$DOB = NULL

today = format(Sys.time(), "%m%d%Y")
write.csv(data,
          file=sprintf('~/tmp/augmented_clinical_%s.csv', today), row.names=F)
write.csv(data_anon,
          file=sprintf('~/tmp/augmented_anon_clinical_%s.csv', today), row.names=F)
