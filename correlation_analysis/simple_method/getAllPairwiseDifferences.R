source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
thresh=.05
hemi = 'R'
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
for (gr in groups) {
    cat('Checking groupwise r for', gr, '\n')
    if (time=='last' || time=='baseline') {
        idx = group==gr
        idx2 = visit==time
        x = tha[idx&idx2,]
        y = oth[idx&idx2,]
    } else {
        nobs = dim(tha)[1]
        x = tha[seq(2,nobs,2),] - tha[seq(1,nobs,2),]
        y = oth[seq(2,nobs,2),] - oth[seq(1,nobs,2),]
        my_group = group[seq(1,nobs,2)]
        idx = my_group==gr
        x = x[idx,]
        y = y[idx,]
    }
    # formulas from https://stat.ethz.ch/pipermail/r-help/2000-January/009758.html
    r = cor(x, y)
    dfr = dim(x)[1]-2
    Fstat = r^2 * dfr / (1 - r^2)
    p = 1 - pf(Fstat, 1, dfr)
    eval(parse(text=sprintf('rMask_%s = p<thresh', gr)))
    eval(parse(text=sprintf('r_%s = r', gr)))
}
eval(parse(text=sprintf('good_pairs = which(rMask_%s & rMask_%s & rMask_%s)', groups[1], groups[2], groups[3])))
print('Evaluating good pairs')
for (i in good_pairs) {
    nvVSper[i] = get_pval_from_Rs(r_NV[i],64,r_persistent[i],32)
    nvVSrem[i] = get_pval_from_Rs(r_NV[i],64,r_remission[i],32)
    perVSrem[i] = get_pval_from_Rs(r_persistent[i],32,r_remission[i],32)
}