# Similar to compile_baseline, but compiles follow-up values from matched dataset and then the remaining ones from the original data

# Star with the original data.
cat('Fetching all original follow-up data\n')
gf = read.csv('~/data/structural/gf_1473_dsm45.csv')
load('~/data/structural/GP_1473.RData')
load('~/data/structural/DATA_1473.RData')
brain_data = c('dtL_thalamus_1473', 'dtR_thalamus_1473',
               'dtL_gp', 'dtR_gp',
               'dtL_striatum_1473', 'dtR_striatum_1473')
brain_data_gm = c('thalamusL', 'thalamusR',
                  'gpL', 'gpR',
                  'striatumL', 'striatumR')
idx <- (gf$DX=="ADHD" | gf$DX=="NV") & gf$MATCH5==1
idx2 <- array(data=FALSE,dim=length(idx))
subjects = unique(gf[idx,]$PERSON.x) 
for (subj in subjects) {
    all_subj_scans <- which(gf$PERSON.x == subj)
    ages <- gf[all_subj_scans,]$AGESCAN
    ages <- sort(ages, index.return=TRUE, decreasing=T)
    # makes the last scan true
    idx2[all_subj_scans[ages$ix][1]] = TRUE
}
idx <- idx & idx2
gfLast = gf[idx,]
for (b in brain_data) {
    eval(parse(text=sprintf('%sLast = %s', b, b)))
    eval(parse(text=sprintf('%sLast = %sLast[,idx]', b, b)))
}

# replace the data for all ADHD subjects that have a scan in the matchdiff data
cat('Replacing data for ADHD subject by matched scans\n')
gfm = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_2to1_v2.csv', dsm))
load(sprintf('~/data/structural/all_data_gf_1473_dsm%d_matchedDiff_on18_2to1_v2.RData', dsm))
for (s in 1:dim(gfLast)[1]) {
    subjIdx = which(gfm$subject==gfLast[s,]$PERSON.x)
    if (length(subjIdx)>1) {
        # get the follow-up data for this subject
        sortedAges = sort(gfm[subjIdx,]$age, index.return=T, decreasing=T)
        idx = subjIdx[sortedAges$ix[1]] 
        if (gfm[idx,]$group=='NV') {
            gfLast[s,]$DX = 'NV'
        }
        else {
            gfLast[s,]$DX = 'ADHD'
        }
        gfLast[s,]$AGESCAN = gfm[idx,]$age
        for (b in 1:length(brain_data)) {
            eval(parse(text=sprintf('%sLast[,s] = %s[,idx]', 
                                    brain_data[b], brain_data_gm[b])))
        }
    }
}

# swap NV subjects that are in the matchdiff data but not in the original data
cat('Swapping NV subjects that were not in original data\n')
nvsInMatch = unique(gfm[gfm$group=='NV',]$subject)
nvsInLast = unique(gfLast[gfLast$DX=='NV',]$PERSON.x)
# people in match that are not in last
subjects2add = setdiff(nvsInMatch,nvsInLast)
# people in last that need to be replaced by a data point from match
subjects2replace = intersect(nvsInMatch,nvsInLast)
# people we can remove in place of someone from match
disposableSubjects = setdiff(nvsInLast,nvsInMatch)

# start by swapping data from last by their data in match
for (s in subjects2replace) {
    lastIdx = which(gfLast$PERSON.x==s)
    matchIdx = which(gfm$subject==s)[1]
    gfLast[lastIdx,]$AGESCAN = gfm[matchIdx,]$age
    for (b in 1:length(brain_data)) {
        eval(parse(text=sprintf('%sLast[,lastIdx] = %s[,matchIdx]', 
                                brain_data[b], brain_data_gm[b])))
    }
}
# now add any subjects from match that are not in last
csv = read.csv('~/data/structural/15T_ADD_ADT_OCD_NV_scans_2011_06_27_clean.csv')
for (s in subjects2add) {
    subjSex = unique(csv[csv$ID==s,]$SEX)
    # find a disposable subject of the same sex
    found = F
    cnt = 1
    while (!found) {
        lastIdx = which(gfLast$PERSON.x==disposableSubjects[cnt])
        if (gfLast[lastIdx,]$SEX.x==subjSex) {
            found = T
            disposableSubjects = disposableSubjects[disposableSubjects!=disposableSubjects[cnt]]
        }
        else {
            cnt = cnt + 1
        }
    }
    matchIdx = which(gfm$subject==s)[1]
    gfLast[lastIdx,]$PERSON.x = gfm[matchIdx,]$subject
    gfLast[lastIdx,]$AGESCAN = gfm[matchIdx,]$age
    gfLast[lastIdx,]$SEX.x = subjSex
    for (b in 1:length(brain_data)) {
        eval(parse(text=sprintf('%sLast[,lastIdx] = %s[,matchIdx]', 
                                brain_data[b], brain_data_gm[b])))
    }
    cnt = cnt + 1
}

# finally, rename everything to their more descriptive names
cat('Renaming and transposing matrices\n')
for (b in 1:length(brain_data)) {
    eval(parse(text=sprintf('%sLast = t(%sLast)', 
                            brain_data_gm[b], brain_data[b])))
}