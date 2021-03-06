write_vertices <- function (data, filename, cnames)
    # data is voxels X vars, filename is a string, cnames is a list of column names 
{
    write("<header>", file = filename)
    write("</header>", file = filename, append = TRUE)
    data[is.na(data)] = 0
    write.table(data, file = filename, append = TRUE, 
                quote = FALSE, row.names = FALSE, col.names = cnames)
}

load('~/data/structural/GP_1473.RData')
load('~/data/structural/DATA_1473.RData')

# use only subjects with more than one scan
dsm = 4
g1 = '"NV"'
g2 = '"NV"'
g3 = '"persistent"'
gf_1473 = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm%d_diff.csv', dsm))
eval(parse(text=sprintf('idx = gf_1473$outcomedsm%d==g1 | gf_1473$outcomedsm%d==g2 | gf_1473$outcomedsm%d==g3', dsm, dsm, dsm)))
idx_base <- array(data=F,dim=length(idx))
idx_last <- array(data=F,dim=length(idx))
# get rid of scans that don't pass our QC or that haven't been matched
idx = idx & (gf_1473$qc_civet<3.5 & gf_1473$qc_sub1=='"PASS"' & gf_1473$match_outcome==1)
# find out all scans for each unique subject
subjects = unique(gf_1473[idx,]$personx)  # only look at subjects that obeyed previous criteria
for (subj in subjects) {
    good_subj_scans <- which((gf_1473$personx == subj) & idx)
    # only use subjects with one scan < 18 and another after 18
    ages <- gf_1473[good_subj_scans,]$agescan
    if ((min(ages)<18) && (max(ages) > 18)) {
        ages <- sort(ages, index.return=T)
        # makes the first scan true
        idx_base[good_subj_scans[ages$ix][1]] = T
        # makes the last scan true
        idx_last[tail(good_subj_scans[ages$ix], n=1)] = T
    }
}
idx_base = idx & idx_base
idx_last = idx & idx_last

# later scripts will need this for compatibility
brain_data = c('dtL_thalamus_1473', 'dtR_thalamus_1473', 
               'dtL_striatum_1473', 'dtR_striatum_1473',
               'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473',
               'dtL_gp', 'dtR_gp')
group = as.factor(gf_1473[idx_last | idx_base,]$outcomedsm4)
subject = as.factor(gf_1473[idx_last | idx_base,]$personx)
age = gf_1473[idx_last | idx_base,]$agescan
for (i in brain_data) {
    print(sprintf('Cleaning up %s', i))
    eval(parse(text=sprintf('data = %s[,idx_base | idx_last]', i)))
    eval(parse(text=sprintf('%s = t(data)', i)))
}

# now we need to massage the idx, because we changed the data order
idx = array(data=0,dim=length(idx))
idx[idx_base] = 1
idx[idx_last] = 2
idx = idx[idx>0]
idx_base = idx==1
idx_last = idx==2