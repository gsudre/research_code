b1 = thalamusR
b2 = gpR
roi1 = c(629,642,635)
roi2 = c(573,458,169,158)
nperms = 100
groups = c('NV','remission','persistent')

bootstrapCI <- function() 
{
    Rs <- array(data=0, dim=c(nperms, 3))
    for (p in 1:nperms) {
        cnt = 1
        for (g in groups) {
            nsubjs = sum(group==g & visit=='baseline')
            blabels = sample.int(nsubjs, replace = TRUE)
            gidxb = which(group==g & visit=='baseline')[blabels]
            gidxf = which(group==g & visit=='last')[blabels]
            s1 = rowSums(b1[,roi1])
            s2 = rowSums(b2[,roi2])
            Rs[p, cnt] = cor(s1[gidxf],s2[gidxf]) - cor(s1[gidxb],s2[gidxb])
            cnt = cnt + 1
        }
    }
    cis = array(dim=c(3,2))
    # find out the CI for each slope
    for (s in 1:3) {
        sortedRs = sort(Rs[,s])
        cis[s,1] = sortedRs[ceiling(.025*nperms)]
        cis[s,2] = sortedRs[ceiling(.975*nperms)]
    }
    return(cis)
}

# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
Rs = vector(mode='numeric', length=length(groups))
for (g in 1:length(groups)) {
    s1 = rowSums(b1[,roi1])
    s2 = rowSums(b2[,roi2])
    idx_base = group==groups[g] & visit=='baseline'
    idx_last = group==groups[g] & visit=='last'
    Rs[g] = cor(s1[idx_last],s2[idx_last]) - cor(s1[idx_base],s2[idx_base])
}

library(ggplot2)
df = data.frame(group=groups)
df$Rs = Rs
ci = bootstrapCI()
df$lci = ci[,1]
df$uci = ci[,2]
pd = position_dodge(.1)
p = ggplot(df, aes(x=group, y=Rs)) + 
    geom_errorbar(aes(ymin=lci, ymax=uci), colour="black", width=.001, position=pd) +
    geom_point(size=8, position=pd) +
    theme_bw() + theme(text = element_text(size=32)) + labs(x=NULL, y=NULL) +
    theme(legend.justification=c(1,0), legend.position=c(0.6,0))
print(p) 