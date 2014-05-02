source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
thresh=.05
hemi = 'L'
other = 'cortex'
time = 'diff'
groups = c('NV', 'persistent', 'remission')

get_pval_from_Rs <- function(r1, n1, r2, n2) {
    b1 = 1/2*log((1+r1)/(1-r1))
    b2 = 1/2*log((1+r2)/(1-r2))
    z = (b1-b2)/sqrt(1/(n1-3)+1/(n2-3))
    return(2*pnorm(-abs(z)))
}

eval(parse(text=sprintf('tha = thalamus%s', hemi)))
eval(parse(text=sprintf('oth = %s%s', other, hemi)))

ntha = dim(tha)[2]
noth = dim(oth)[2]
nvVSper = matrix(nrow=ntha, ncol=noth)
nvVSrem = matrix(nrow=ntha, ncol=noth)
perVSrem = matrix(nrow=ntha, ncol=noth)
for (i in 1:ntha) {
    cat(i,'\n')
    for (j in 1:noth) {
        rs = vector()
        for (gr in groups) {
            idx = group==gr
            x = tha[idx, i]
            y = oth[idx, j]
            if (time=='diff') {
                x = x[seq(2,length(x),2)] - x[seq(1,length(x),2)]
                y = y[seq(2,length(y),2)] - y[seq(1,length(y),2)]
            } else if (time=='baseline') {
                x = x[seq(1,length(x),2)]
                y = y[seq(1,length(y),2)]
            } else {
                x = x[seq(2,length(x),2)]
                y = y[seq(2,length(y),2)]
            }
            my_r = cor.test(y,x)
            if (my_r$p.value < thresh) {
                rs = c(rs, my_r$estimate)
            }
        }
        # if we have as many good tests as the number of groups
        if (length(rs)==length(groups)) {
            nvVSper[i,j] = get_pval_from_Rs(rs[1],64,rs[2],32)
            nvVSrem[i,j] = get_pval_from_Rs(rs[1],64,rs[3],32)
            perVSrem[i,j] = get_pval_from_Rs(rs[2],32,rs[3],32)
        } else {
            nvVSper[i,j] = NA
            nvVSrem[i,j] = NA
            perVSrem[i,j] = NA
        }
    }
}