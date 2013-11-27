fname = "~/data/results/structural_v2/growth_MATCHDIFF_dsm5_ADHDvsNV_%s.txt"

thresh = .05
brain_data = c('thalamusL')

# trimmed down version of mni.compute.FDR
getFDR <- function (p.values, df = Inf, fdr = 0.05) {
    sorted.p.values <- sort(p.values, index.return = TRUE)
    q <- sorted.p.values$x/1:length(p.values) * length(p.values)
    q2 <- q <= fdr
    r <- sort(q2, decreasing = TRUE, index.return = TRUE)
    fdr.threshold <- qt(sorted.p.values$x[max(r$ix[r$x == TRUE])], df)
    q[sorted.p.values$ix] <- q
    return(fdr.threshold, q)
}

a = read.table(
    sprintf(fname, brain_data[1]),
    skip=3)
pvals = a[,2]
fvals = a[,1]
if (length(brain_data)>1) {
    for (b in 2:length(brain_data)) {
        a = read.table(
            sprintf(fname, brain_data[b]),
            skip=3)
        pvals = c(pvals, a[,2])
        fvals = c(fvals, a[,1])
    }
}
adj_pvals = p.adjust(pvals, method='fdr')
nverts = length(pvals)
# Dim = c(sqrt(nverts),sqrt(nverts))
# sFWHM = 5
# resels = prod(Dim/c(sFWHM,sFWHM))
# Z = seq(0,5,.01)
# expEC = (resels*(4*log(2))*((2*pi)^(-3/2))*Z)*exp((Z^2)*(-0.5))
# rft = Z[which(expEC<thresh)[2]]
# frft = min(fvals[pvals < 2*pnorm(-abs(rft))])
# qf(max(pvals[adj_pvals < thresh])/2, 1, 58)
cat('File: ', fname)
cat('\nThreshold: p <', thresh)
cat('\nMaximum F-val: ', max(abs(fvals)))
cat('\nGood uncorrected pvals:', sum(pvals<thresh), '/', length(pvals))
cat('\nMinimum uncorrected F-val:', min(abs(fvals[pvals<thresh])))
# cat('\nGood RFT pvals:', sum(abs(fvals)>frft), '/', length(fvals))
# cat('\nMinimum RFT F-val:', frft, '(Z score:', rft, ')')
cat('\nGood FDR pvals:', sum(adj_pvals<thresh), '/', length(adj_pvals))
cat('\nMinimum FDR F-val:', min(abs(fvals[adj_pvals<thresh])))