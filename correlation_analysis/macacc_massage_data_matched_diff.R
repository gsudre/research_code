write_vertices <- function (data, filename, cnames)
    # data is voxels X vars, filename is a string, cnames is a list of column names 
{
    write("<header>", file = filename)
    write("</header>", file = filename, append = TRUE)
    data[is.na(data)] = 0
    write.table(data, file = filename, append = TRUE, 
                quote = FALSE, row.names = FALSE, col.names = cnames)
}


library(nlme)

# use only subjects with more than one scan
dsm = 5
g1 = 'NV'
g2 = 'remission'
g3 = 'persistent'
load(sprintf('~/data/structural/all_data_gf_1473_dsm%d_matchedDiff_on18_2to1_v2.RData', dsm))
gf = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm%d_diff_2to1_v2.csv', dsm))
idx = gf$group==g1 | gf$group==g2 | gf$group==g3
idx_base <- array(data=F,dim=length(idx))
idx_last <- array(data=F,dim=length(idx))

# find out all scans for each unique subject
subjects = unique(gf[idx,]$subject)  # only look at subjects that obeyed previous criteria
for (subj in subjects) {
    good_subj_scans <- which((gf$subject == subj) & idx)
    # only use subjects with one scan < 18 and another after 18
    ages <- gf[good_subj_scans,]$age
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
brain_data = c('thalamusL', 'thalamusR', 'striatumL', 'striatumR',
               'gpL', 'gpR', 'cortexL', 'cortexR')
group = as.factor(gf[idx_last | idx_base,]$group)
subject = as.factor(gf[idx_last | idx_base,]$subject)
age = gf[idx_last | idx_base,]$age
maskid = gf[idx_last | idx_base,]$maskid
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