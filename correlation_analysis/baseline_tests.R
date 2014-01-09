# checking difference between NVs and ADHDs at baseline
source('~/research_code/correlation_analysis/compile_baseline.R')

fnameRoot = '~/data/results/structural_v2/baselineTTest_ADHDvsNV'

# making sure there's no difference at baseline age and sex
print(t.test(gfBase$AGESCAN ~ as.factor(gfBase$DX)))
print(table(gfBase$DX,gfBase$SEX.x))

brain_data = c('thalamusLBase','thalamusRBase')
for (b in brain_data) {
    eval(parse(text=sprintf('data=%s', b)))
    num_voxels = dim(data)[2]
    tsLinear <- array(dim=c(num_voxels, 2))
    for (v in 1:num_voxels) {
        print(sprintf('%d / %d', v, num_voxels))
        d = data.frame(y=data[,v], dx=gfBase$DX)
        fit <- try(lm(y~dx, data=d), TRUE)
        if (length(fit) > 1) {  
            tsLinear[v,1] <- summary(fit)$coefficients[2,3]
            tsLinear[v,2] <- summary(fit)$coefficients[2,4]
        }
    }
    fname = sprintf('%s_%s.txt', fnameRoot, b)
    write_vertices(tsLinear, fname, c('Tval','pval'))
}


########## THE REST OF THIS CODE HAS NOT BEEN MODIFIED TO RUN WITH THE V2 DATA POOL! PROCEED CAREFULLY! #########

# now we run the omnibus test
# DEFINE ROI VARIABLE IN WORKSPACE FIRST
data = 'dtL_thalamus_1473Base'
a = read.table(sprintf("~/data/results/structural/baselineTTest_MATCH5_ADHDvsNV_%s.txt",
                       data), skip=3)
eval(parse(text=sprintf('data=%s', data)))
tvals = a[,1]


nperms=1000
library(ggplot2)
bootstrapCI <- function() 
{
    sa <- array(dim=c(nperms, 2))
    for (i in 1:nperms) {
        cnt = 1
        for (g in c('NV','ADHD')) {
            nsubjs = sum(gfBase$DX==g)
            labels = sample.int(nsubjs, replace = TRUE)
            gidx = which(gfBase$DX==g)[labels]
            sa[i,cnt] = sum(data[roi, gidx])
            cnt = cnt + 1
        }
    }
    cis = array(dim=c(2,2))
    # find out the CI for each slope
    for (s in 1:2) {
        sortedSAs = sort(sa[,s])
        cis[s,1] = sortedSAs[ceiling(.025*nperms)]
        cis[s,2] = sortedSAs[ceiling(.975*nperms)]
    }
    return(cis)
}
df = data.frame(group=c('NV','ADHD'))
df$sa = c(sum(data[roi,gfBase$DX=='NV']),sum(data[roi,gfBase$DX=='ADHD']))
ci = bootstrapCI()
df$lci = ci[,1]
df$uci = ci[,2]
p = ggplot() + geom_point(data = df, aes(x = group, y = sa), size=7) +
    geom_errorbar(data = df, aes(x = group, y=sa, ymin = lci, ymax = uci), colour = 'red', width = 0.4) +
    xlab("Group") +
    ylab(sprintf("Summed Surface area"))
print(p)


####################################
# predict outcome based on baseline
fnameRoot = '~/data/results/structural/baselineTTest_remVSper'
gf = read.csv('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_2to1.csv')
idx <- (gf$outcome.dsm5=="remission" | gf$outcome.dsm5=="persistent")
idx2 <- array(data=FALSE,dim=length(idx))
subjects = unique(gf[idx,]$PERSON.x) 
for (subj in subjects) {
    all_subj_scans <- which(gf$PERSON.x == subj)
    ages <- gf[all_subj_scans,]$AGESCAN
    ages <- sort(ages, index.return=TRUE)
    # makes the first scan true
    idx2[all_subj_scans[ages$ix][1]] = TRUE
}
idx <- idx & idx2
print(t.test(gf[idx,]$AGESCAN ~ as.factor(gf[idx,]$outcome.dsm5)))
print(table(gf[idx,]$outcome.dsm5,gf[idx,]$SEX.x))
brain_data = c('dtL_thalamus_1473','dtR_thalamus_1473')
for (b in brain_data) {
    eval(parse(text=sprintf('data=%s[,idx]', b)))
    num_voxels = dim(data)[1]
    tsLinear <- array(dim=c(num_voxels, 1))
    for (v in 1:num_voxels) {
        print(sprintf('%d / %d', v, num_voxels))
        d = data.frame(y=data[v,], dx=gf[idx,]$outcome.dsm5)
        fit <- try(lm(y~dx, data=d), TRUE)
        if (length(fit) > 1) {  
            tsLinear[v,] <- summary(fit)$coefficients[2,3]
        }
    }
    fname = sprintf('%s_%s.txt', fnameRoot, b)
    write_vertices(tsLinear, fname, c('Tval'))
}


