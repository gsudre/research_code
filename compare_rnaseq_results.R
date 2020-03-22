args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    fname1 = args[1]
    fname1 = args[2]
} else {
    fname1 = 'resPOPnoPH_ACC_pLT0.10_Diagnosis.csv'
    fname2 = 'resWNHnoPH_ACC_pLT0.10_Diagnosis.csv'
}

min_pval = .001

p_str = 'p.value'
if (grepl(pattern='ACC', fname1) || grepl(pattern='Caudate', fname2)) {
    p_str = 'Pr...t..'
}

res1 = read.csv(fname1)
res2 = read.csv(fname2)

# check all rows with DX predictors
check_me = unique(res1$predictor)[grepl(unique(res1$predictor),
                                  pattern='DiagnosisControl')]
for (p in 1:length(check_me)) {
    pred = check_me[p]
    my_res1 = res1[as.character(res1$predictor)==pred, ]
    pvals1 = my_res1[, p_str]
    my_res2 = res2[as.character(res2$predictor)==pred, ]
    pvals2 = my_res2[, p_str]

    x = seq(from=min_pval, to=min(c(pvals1, pvals2)), by=-.00005)
    y1 = sapply(1:length(x), function(k) sum(pvals1<x[k]))
    y2 = sapply(1:length(x), function(k) sum(pvals2<x[k]))
    y3 = vector(length=length(x))
    for (k in 1:length(x)) {
        list1 = my_res1[pvals1 < x[k], 'dep_var']
        list2 = my_res2[pvals2 < x[k], 'dep_var']
        y3[k] = length(intersect(list1, list2))
    }

    # get adjusted p-values
    pvals1.adj = p.adjust(pvals1, method='fdr')
    p1_qp05 = min(pvals1[pvals1.adj < .05])
    p1_qp1 = min(pvals1[pvals1.adj < .1])
    pvals2.adj = p.adjust(pvals2, method='fdr')
    p2_qp05 = min(pvals2[pvals2.adj < .05])
    p2_qp1 = min(pvals2[pvals2.adj < .1])

    dev.new(width=6, height=5, unit="in")
    plot(x, y1, type="l", lwd=2, col="blue", ylim=c(0, max(c(y1, y2))),
         xlab='p-value', ylab=sprintf('Sig genes for %s', pred),
         main=sprintf('%s VS %s', fname1, fname2),
         cex.lab=.75, cex.main=.7)
    lines(x, y2, lwd=2, col="red")
    lines(x, y3, lwd=2, col="black")
    if (p1_qp05 < min_pval) {
        abline(v=p1_qp05, lwd=1, col='blue')
    }
    if (p1_qp1 < min_pval) {
        abline(v=p1_qp1, lwd=1, col='blue')
    }
    if (p2_qp05 < min_pval) {
        abline(v=p2_qp05, lwd=1, col='red')
    }
    if (p2_qp1 < min_pval) {
        abline(v=p2_qp1, lwd=1, col='red')
    }
    legend('topleft', legend=c(fname1, fname2, 'intersect'),
            col=c('blue', 'red', 'black'),
            cex=.8, lty=1, lwd=2)
}

# qs