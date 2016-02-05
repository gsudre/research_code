fname_root = 'correlationMS_thalamusR_FROMgpRstriatumR_matchedDiffDSM5_2to1_perVSnv'

# combine all the data ot get approximated MACACC strength
brain_data = c('gpR','gpL','striatumL','striatumR')
txt = sprintf('%s[idx_base | idx_last,]', brain_data[1])
for (i in 2:length(brain_data)) {
    txt = sprintf('%s, %s[idx_base | idx_last,]', txt, brain_data[i])
}
eval(parse(text=sprintf('data=cbind(%s)', txt)))

# get approximate vector for all subjects and time points
approx = rowMeans(data)

brain_data = c('thalamusR', 'thalamusL')
nverts = 0
for (i in brain_data) {
    v = eval(parse(text=sprintf('dim(%s)[2]', i)))
    nverts = nverts + v
}
baseCorr = array(dim=c(nverts, 2))
lastCorr = array(dim=c(nverts, 2))
deltaCorr = array(dim=c(nverts, 2))
cnt = 1
for (i in brain_data) {
    cat('Working on ', i, '\n')
    eval(parse(text=sprintf('data=%s[idx_base | idx_last,]', i)))
    nverts = dim(data)[2]
    # do all the necessary tests
    for (v in 1:nverts) {
        cat('\t', v, ' / ', nverts, '\n')
        baseCorr[cnt,1] = cor(approx[idx_base & group==g1], data[idx_base & group==g1, v])
        lastCorr[cnt,1] = cor(approx[idx_last & group==g1], data[idx_last & group==g1, v])
        baseCorr[cnt,2] = cor(approx[idx_base & group==g2], data[idx_base & group==g2, v])
        lastCorr[cnt,2] = cor(approx[idx_last & group==g2], data[idx_last & group==g2, v])
        # making sure they're in the same subject order before subtracting
        if (sum(subject[idx_last]!=subject[idx_base]) == 0) {
            deltaCorr[cnt,1] = cor(approx[idx_last & group==g1]-approx[idx_base & group==g1],
                                 data[idx_last & group==g1, v]-data[idx_base & group==g1, v])
            deltaCorr[cnt,2] = cor(approx[idx_last & group==g2]-approx[idx_base & group==g2],
                                 data[idx_last & group==g2, v]-data[idx_base & group==g2, v])
        }
        cnt = cnt + 1
    }
}

getZs <- function (rs1, rs2, n1, n2) {
    zbar1 = 0.5 * (log(1+rs1) - log(1-rs1))
    zbar2 = 0.5 * (log(1+rs2) - log(1-rs2))
    zs = (zbar1 - zbar2) / sqrt(1/(n1-3) + 1/(n2-3))
    return(zs)
}

showSummary <- function (zs) { 
    pvals = 2*pnorm(-abs(zs))
    adj_pvals = p.adjust(pvals, method='fdr')
    cat('\nMaximum Z: ', max(abs(zs)))
    cat('\nGood uncorrected pvals:', sum(pvals<.05), '/', length(pvals))
    cat('\nMinimum uncorrected Z:', min(abs(zs[pvals<.05])))
    cat('\nGood FDR pvals:', sum(adj_pvals<.1), '/', length(adj_pvals))
    cat('\nMinimum FDR Z:', min(abs(zs[adj_pvals<.1])))
}

cat('\nBaseline')
showSummary(getZs(baseCorr[,1], baseCorr[,2], 64, 32))
cat('\nFollow-up')
showSummary(getZs(lastCorr[,1], lastCorr[,2], 64, 32))
cat('\nDelta')
showSummary(getZs(deltaCorr[,1], deltaCorr[,2], 64, 32))