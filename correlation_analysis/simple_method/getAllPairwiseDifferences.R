source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
thresh=.5
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

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

for (g in groups) {
    print(g)
    load(sprintf('~/data/results/simple/es%s_thalamus2%s_%s_%s.RData',
                 hemi, other, time, g))
    es = abs(es)
    eval(parse(text=sprintf('bes_%s = binarize(es,thresh)', tolower(g))))
}

eval(parse(text=sprintf('tha = thalamus%s', hemi)))
eval(parse(text=sprintf('oth = %s%s', other, hemi)))

# first dimension is thalamus
nthal = dim(es)[1]
nvVSper = matrix(nrow=nthal, ncol=dim(es)[2])
nvVSrem = matrix(nrow=nthal, ncol=dim(es)[2])
perVSrem = matrix(nrow=nthal, ncol=dim(es)[2])
for (i in 1:nthal) {
    cat(i,'\n')
    for (j in 1:dim(es)[2]) {
        if (bes_nv[i,j] && bes_persistent[i,j] && bes_remission[i,j]) {
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
                my_r = cor.test(y,x)$estimate
                rs = c(rs, my_r)
            } 
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