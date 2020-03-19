args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    fname = args[1]
} else {
    fname = 'resPOP_pLT0.10_DiagnosisAge.csv'
}

p_str = 'Pr...t..'
if (grepl(pattern='ACC', fname)) {
    meff = 44.26
} else if (grepl(pattern='Caudate', fname)) {
    meff = 47.54
} else {
    meff = 77.70
    p_str = 'p.value'
}

print(fname)
res = read.csv(fname)

froot = gsub(x=fname, pattern='.csv', '')

# check all rows with DX predictors
check_me = unique(res$predictor)[grepl(unique(res$predictor),
                                 pattern='DiagnosisControl')]
for (p in 1:length(check_me)) {
    pred = check_me[p]
    my_res = res[res$predictor==pred, ]
    pvals = my_res[, p_str]
    pvals2 = p.adjust(pvals, method='fdr')
    print(sprintf('Tests with %s p < .05: %d', pred, sum(pvals<.05)))
    print(sprintf('Tests with %s p < .01: %d', pred, sum(pvals<.01)))
    
    # spit out some lists
    out_fname = sprintf('grexlist_%s_%s_pLEp01.txt', froot, pred)
    idx = which(pvals<.01)
    write.table(my_res[idx, 'dep_var'], file=out_fname, col.names=F,
                row.names=F, quote=F)
    print(sprintf('Tests with %s p < Meff: %d', pred, sum(pvals<(.05/meff))))
    out_fname = sprintf('grexlist_%s_%s_Meff.txt', froot, pred)
    idx = which(pvals<(.05/meff))
    write.table(my_res[idx, 'dep_var'], file=out_fname, col.names=F,
                row.names=F, quote=F)
    
    print(sprintf('Tests with %s q < .05: %d', pred, sum(pvals2<.05)))
    print(sprintf('Tests with %s q < .1: %d', pred, sum(pvals2<.1)))
    eval(parse(text=sprintf('pvals_%d = pvals', p)))
}
# combine results
if (length(check_me) > 1) {
    dx_str = paste(check_me, collapse=' and ')
    for (pt in c(.05, .01)) {
        sum_me = c()
        for (p in 1:length(check_me)) {
            eval(parse(text=sprintf('p%d_good = pvals_%d < %f', p, p, pt)))
            sum_me = c(sum_me, sprintf('p%d_good', p))
        }
        sum_str = paste(sum_me, collapse=' & ')
        eval(parse(text=sprintf('my_count = sum(%s)', sum_str)))
        print(sprintf('Tests with %s p < %.2f: %d', dx_str, pt, my_count))
    }
}
