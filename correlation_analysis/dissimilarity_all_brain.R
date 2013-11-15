# This one allows for connections between hemispheres
# g1 = 'NV'
# g2 = 'persistent'
# g3 = 'remission'
nperms = 1000
# gf = read.csv('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_1to1.csv')
# dataRoot = '~/data/structural/roisSum_%s%s_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_1to1.csv'
brain = c('striatum', 'thalamus', 'gp')
hemi = c('L', 'R')
for (b in brain) {
#     for (h in hemi) {
#         eval(parse(text=sprintf('%s%s=read.csv("%s")', 
#                                 b, h, sprintf(dataRoot, b, h))))    
#     }
    eval(parse(text=sprintf('%s=cbind(%s%s,%s%s)', b, b, h, b, h)))
}

permuteCorrDelta <- function(data1B, data1L, data2B, data2L, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    all_dataB = rbind(data1B, data2B)
    all_dataL = rbind(data1L, data2L)
    n1 = dim(data1B)[1]
    n2 = dim(data2B)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(n1+n2, replace = FALSE)
        perm_dataB <- all_dataB[perm_labels, ]
        perm_dataL <- all_dataL[perm_labels, ]
        pmat1b = perm_dataB[1:n1, ]
        pmat2b = perm_dataB[(n1+1):(n1+n2), ]
        pmat1l = perm_dataL[1:n1, ]
        pmat2l = perm_dataL[(n1+1):(n1+n2), ]
        cor1b = cor(pmat1b)
        cor2b = cor(pmat2b)
        cor1l = cor(pmat1l)
        cor2l = cor(pmat2l)
        deltaCor1 = cor1l - cor1b
        deltaCor2 = cor2l - cor2b
        ds[i] = 1-cor(deltaCor1[upper.tri(deltaCor1)], deltaCor2[upper.tri(deltaCor2)], method="spearman")
    }
    return(ds)
}

permuteCorr <- function(data1, data2, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    all_data = rbind(data1, data2)
    n1 = dim(data1)[1]
    n2 = dim(data2)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(all_data)[1], replace = FALSE)
        perm_data <- all_data[perm_labels, ]
        pmat1 = perm_data[1:n1, ]
        pmat2 = perm_data[(n1+1):(n1+n2), ]
        cor1 = cor(pmat1)
        cor2 = cor(pmat2)
        ds[i] = 1-cor(cor1[upper.tri(cor1)], cor2[upper.tri(cor2)], method="spearman")
    }
    return(ds)
}

# idx = gf$group==g1 | gf$group==g2 | gf$group==g3
# idx_base <- array(data=F,dim=length(idx))
# idx_last <- array(data=F,dim=length(idx))
# subjects = unique(gf[idx,]$subject)  # only look at subjects that obeyed previous criteria
# for (subj in subjects) {
#     good_subj_scans <- which((gf$subject == subj) & idx)
#     ages <- gf[good_subj_scans,]$age
#     if ((min(ages)<18) && (max(ages) > 18)) {
#         ages <- sort(ages, index.return=T)
#         # makes the first scan true
#         idx_base[good_subj_scans[ages$ix][1]] = T
#         # makes the last scan true
#         idx_last[tail(good_subj_scans[ages$ix], n=1)] = T
#     }
# }
# idx_base = idx & idx_base
# idx_last = idx & idx_last

# creating data and correlation matrices
for (i in 1:3) {
    eval(parse(text=sprintf('idx%g=group==g%g & idx_base', i, i)))
    txt = sprintf('%s[idx%g,]', brain[1], i)
    for (b in brain) {
        txt = sprintf('%s,%s[idx%g,]', txt, b, i)
    }
    eval(parse(text=sprintf('mat%gb=cbind(%s)', i, txt)))
    eval(parse(text=sprintf('cor%gb=cor(mat%gb)', i, i)))
}
# computing distances
for (i in 1:3) {
    for (j in i:3) {
        if (i != j) {
            eval(parse(text=sprintf(
                'd%g%gb=1-cor(cor%gb[upper.tri(cor%gb)], cor%gb[upper.tri(cor%gb)], method="spearman")',
                i, j, i, i, j, j)))
        }
    }
}

# getting p-value for distances
for (i in 1:3) {
    for (j in i:3) {
        if (i != j) {
            eval(parse(text=sprintf('tmp=permuteCorr(mat%gb, mat%gb, nperms)>d%g%gb',
                                    i, j, i, j)))
            pval = sum(tmp)/nperms
            pval = min(pval,1-pval)
            eval(parse(text=sprintf('pval%g%gb=pval', i, j)))
            cat(sprintf('Baseline: %s vs %s: p = %f\n', 
                        eval(parse(text=sprintf('g%g', i))), 
                        eval(parse(text=sprintf('g%g', j))), 
                        pval))
        }
    }
}

# doing the same as above, but now for follow up data
for (i in 1:3) {
    eval(parse(text=sprintf('idx%g=gf$group==g%g & idx_last', i, i)))
    txt = sprintf('%s[idx%g,]', brain[1], i)
    for (b in brain) {
        txt = sprintf('%s,%s[idx%g,]', txt, b, i)
    }
    eval(parse(text=sprintf('mat%gf=cbind(%s)', i, txt)))
    eval(parse(text=sprintf('cor%gf=cor(mat%gf)', i, i)))
}
for (i in 1:3) {
    for (j in i:3) {
        if (i != j) {
            eval(parse(text=sprintf(
                'd%g%gf=1-cor(cor%gf[upper.tri(cor%gf)], cor%gf[upper.tri(cor%gf)], method="spearman")',
                i, j, i, i, j, j)))
        }
    }
}
for (i in 1:3) {
    for (j in i:3) {
        if (i != j) {
            eval(parse(text=sprintf('tmp=permuteCorr(mat%gf, mat%gf, nperms)>d%g%gf',
                                    i, j, i, j)))
            pval = sum(tmp)/nperms
            pval = min(pval,1-pval)
            eval(parse(text=sprintf('pval%g%gf=pval', i, j)))
            cat(sprintf('Follow-up: %s vs %s: p = %f\n', 
                        eval(parse(text=sprintf('g%g', i))), 
                        eval(parse(text=sprintf('g%g', j))), 
                        pval))
        }
    }
}

# now we look at FU-baseline differences
for (i in 1:3) {
    eval(parse(text=sprintf('deltaCor%g=cor%gf-cor%gb', i, i, i)))
}
for (i in 1:3) {
    for (j in i:3) {
        if (i != j) {
            eval(parse(text=sprintf(
                'd%g%gd=1-cor(deltaCor%g[upper.tri(deltaCor%g)], 
                            deltaCor%g[upper.tri(deltaCor%g)], method="spearman")',
                i, j, i, i, j, j)))
        }
    }
}
for (i in 1:3) {
    for (j in i:3) {
        if (i != j) {
            eval(parse(text=sprintf('tmp=permuteCorrDelta(mat%gb, mat%gf, mat%gb, mat%gf, nperms)>d%g%gd',
                                    i, i, j, j, i, j)))
            pval = sum(tmp)/nperms
            pval = min(pval,1-pval)
            eval(parse(text=sprintf('pval%g%gd=pval', i, j)))
            cat(sprintf('Delta: %s vs %s: p = %f\n', 
                        eval(parse(text=sprintf('g%g', i))), 
                        eval(parse(text=sprintf('g%g', j))), 
                        pval))
        }
    }
}