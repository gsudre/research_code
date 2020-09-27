args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    out_dir = args[1]
    file_root = args[2]
    rnd_seed = as.numeric(args[3])
} else {
    out_dir = '~/tmp'
    file_root = 'WNH_WNHBoth'
    rnd_seed = 42
}

# start with RNAseq proper
myregion = 'ACC'
data = readRDS('~/data/rnaseq_derek/complete_rawCountData_05132020.rds')
rownames(data) = data$submitted_name  # just to ensure compatibility later
# remove obvious outlier that's NOT caudate labeled as ACC
rm_me = rownames(data) %in% c('68080')
data = data[!rm_me, ]
data = data[data$Region==myregion, ]
more = readRDS('~/data/rnaseq_derek/data_from_philip_POP_and_PCs.rds')
more = more[!duplicated(more$hbcc_brain_id),]
data = merge(data, more[, c('hbcc_brain_id', 'comorbid', 'comorbid_group',
                            'substance', 'substance_group')],
             by='hbcc_brain_id', all.x=T, all.y=F)
data = data[data$Sex=='M',]
imWNH = which(data$C1 > 0 & data$C2 < -.065)
data = data[imWNH, ]

grex_vars = colnames(data)[grepl(colnames(data), pattern='^ENS')]
count_matrix = t(data[, grex_vars])
data = data[, !grepl(colnames(data), pattern='^ENS')]
id_num = sapply(grex_vars, function(x) strsplit(x=x, split='\\.')[[1]][1])
rownames(count_matrix) = id_num
dups = duplicated(id_num)
id_num = id_num[!dups]
count_matrix = count_matrix[!dups, ]

# library(biomaRt)
# mart <- useDataset("hsapiens_gene_ensembl", useMart("ensembl"))
# G_list0 <- getBM(filters= "ensembl_gene_id", attributes= c("ensembl_gene_id",
#                  "hgnc_symbol", "chromosome_name"),values=id_num,mart= mart)
G_list0 = readRDS('~/data/rnaseq_derek/mart_rnaseq.rds')
G_list <- G_list0[!is.na(G_list0$hgnc_symbol),]
G_list = G_list[G_list$hgnc_symbol!='',]
G_list <- G_list[!duplicated(G_list$ensembl_gene_id),]
imnamed = rownames(count_matrix) %in% G_list$ensembl_gene_id
count_matrix = count_matrix[imnamed, ]
data$POP_CODE = as.character(data$POP_CODE)
data[data$POP_CODE=='WNH', 'POP_CODE'] = 'W'
data[data$POP_CODE=='WH', 'POP_CODE'] = 'W'
data$POP_CODE = factor(data$POP_CODE)
data$Individual = factor(data$hbcc_brain_id)
data[data$Manner.of.Death=='Suicide (probable)', 'Manner.of.Death'] = 'Suicide'
data[data$Manner.of.Death=='unknown', 'Manner.of.Death'] = 'natural'
data$MoD = factor(data$Manner.of.Death)
data$batch = factor(as.numeric(data$run_date))

library(caret)
pp_order = c('zv', 'nzv')
pp = preProcess(t(count_matrix), method = pp_order)
X = predict(pp, t(count_matrix))
geneCounts = t(X)
G_list2 = merge(rownames(geneCounts), G_list, by=1)
colnames(G_list2)[1] = 'ensembl_gene_id'
imautosome = which(G_list2$chromosome_name != 'X' &
                   G_list2$chromosome_name != 'Y' &
                   G_list2$chromosome_name != 'MT')
geneCounts = geneCounts[imautosome, ]
G_list2 = G_list2[imautosome, ]

# shuffle Diagnosis if requested
if (rnd_seed > 0) {
    set.seed(rnd_seed)
    rnd_idx = sample(1:nrow(data), nrow(data), replace=F)
    data$Diagnosis = data[rnd_idx,]$Diagnosis
}

library(edgeR)
isexpr <- filterByExpr(geneCounts, group=data$Diagnosis)
genes = DGEList( geneCounts[isexpr,], genes=G_list2[isexpr,] ) 

genes = calcNormFactors( genes)
form = ~ Diagnosis + scale(RINe) + scale(PMI) + scale(Age) + MoD + C1 + C2 + C3 + C4 + C5
design = model.matrix( form, data)
vobj_tmp = voom( genes, design, plot=FALSE)
dupcor <- duplicateCorrelation(vobj_tmp, design, block=data$batch)
vobj = voom( genes, design, plot=FALSE, block=data$batch,
             correlation=dupcor$consensus)
fit <- lmFit(vobj, design, block=data$batch, correlation=dupcor$consensus)
fitDC <- eBayes( fit )
resDC = topTable(fitDC, coef='DiagnosisControl', number=Inf)

get_enrich_order2 = function( res, gene_sets ){
  if( !is.null(res$z.std) ){
    stat = res$z.std
  }else if( !is.null(res$F.std) ){
    stat = res$F.std
  }else if( !is.null(res$t) ){
    stat = res$t
  }else{
    stat = res$F
  }
  names(stat) = res$hgnc_symbol
  stat = stat[!is.na(names(stat))]
  # print(head(stat))
  index = ids2indices(gene_sets, names(stat))
  cameraPR( stat, index )
}
load('~/data/rnaseq_derek/adhd_genesets_philip.RDATA')
load('~/data/rnaseq_derek/c5_gene_sets.RData')
load('~/data/rnaseq_derek/brain_disorders_gene_sets.RData')
load('~/data/rnaseq_derek/data_for_alex.RData')
co = .9 
idx = anno$age_category==1 & anno$cutoff==co
genes_overlap = unique(anno[idx, 'anno_gene'])
for (s in 2:5) {
  idx = anno$age_category==s & anno$cutoff==co
  g2 = unique(anno[idx, 'anno_gene'])
  genes_overlap = intersect(genes_overlap, g2)
}
genes_unique = list()
for (s in 1:5) {
  others = setdiff(1:5, s)
  idx = anno$age_category==s & anno$cutoff==co
  g = unique(anno[idx, 'anno_gene'])
  for (s2 in others) {
    idx = anno$age_category==s2 & anno$cutoff==co
    g2 = unique(anno[idx, 'anno_gene'])
    rm_me = g %in% g2
    g = g[!rm_me]
  }
  genes_unique[[sprintf('dev%s_c%.1f', s, co)]] = unique(g)
}
genes_unique[['overlap']] = unique(genes_overlap)

adhd_dream_cameraDC = get_enrich_order2( resDC, t2 ) 
c5_dream_cameraDC = get_enrich_order2( resDC, c5_all)
dis_dream_cameraDC = get_enrich_order2( resDC, disorders)
dev_dream_cameraDC = get_enrich_order2( resDC, genes_unique )

# looking at imputation data now
a = readRDS('~/data/expression_impute/results/NCR_v3_ACC_1KG_mashr.rds')
iid2 = sapply(a$IID, function(x) strsplit(x, '_')[[1]][2])
a$IID = iid2
pcs = read.csv('~/data/expression_impute/pop_pcs.csv')
imp_data = merge(a, pcs, by='IID', all.x=F, all.y=F)
gf = read.csv('~/data/expression_impute/gf_823_09152020_onePerFamily.csv')

gf$Diagnosis = gf$everADHD_nv012
gf = gf[!is.na(gf$Diagnosis), ]

imp_data = merge(imp_data, gf, by.x='IID', by.y='Subject.Code...Subjects', all.x=F, all.y=F)
grex_vars = colnames(imp_data)[grepl(colnames(imp_data), pattern='^ENS')]
keep_me = imp_data$PC01 < 0 & imp_data$PC02 > 0
imp_data = imp_data[keep_me, ]
library(caret)
set.seed(42)
pp_order = c('zv', 'nzv')
pp = preProcess(imp_data[, grex_vars], method = pp_order)
X = predict(pp, imp_data[, grex_vars])
grex_vars = colnames(X)
imp_data = imp_data[, !grepl(colnames(imp_data), pattern='^ENS')]
id_num = sapply(grex_vars, function(x) strsplit(x=x, split='\\.')[[1]][1])
colnames(X) = id_num
dups = duplicated(id_num)
id_num = id_num[!dups]
grex_vars = id_num
X = t(X[, !dups])

# library(biomaRt)
# mart <- useDataset("hsapiens_gene_ensembl", useMart("ensembl"))
# G_list0 <- getBM(filters= "ensembl_gene_id", attributes= c("ensembl_gene_id",
#                  "hgnc_symbol", "chromosome_name"),values=id_num,mart= mart)
G_list0 = readRDS('~/data/expression_impute/mart_imp.rds')
G_list <- G_list0[!is.na(G_list0$hgnc_symbol),]
G_list = G_list[G_list$hgnc_symbol!='',]
G_list <- G_list[!duplicated(G_list$ensembl_gene_id),]
imnamed = rownames(X) %in% G_list$ensembl_gene_id
X = X[imnamed, ]
grex_vars = grex_vars[imnamed]
G_list2 = merge(G_list, X, by.x=1, by.y=0)
imautosome = which(G_list2$chromosome_name != 'X' &
                   G_list2$chromosome_name != 'Y' &
                   G_list2$chromosome_name != 'MT')
G_list2 = G_list2[imautosome, ]
X = G_list2[, 4:ncol(G_list2)]
rownames(X) = G_list2$ensembl_gene_id
grex_vars = G_list2$ensembl_gene_id

# shuffle Diagnosis if requested
if (rnd_seed > 0) {
    set.seed(rnd_seed)
    rnd_idx = sample(1:nrow(imp_data), nrow(imp_data), replace=F)
    imp_data$Diagnosis = imp_data[rnd_idx,]$Diagnosis
}

nzeros = rowSums(X==0)
keep_me = nzeros < (ncol(X)/2)
good_grex = grex_vars[keep_me]
mydata = cbind(imp_data, t(X))
stats = lapply(good_grex,
                  function(x) {
                    fm_str = sprintf('%s ~ Diagnosis + Sex...Subjects + sample_type + PC01 + PC02 + PC03 + PC04 + PC05', x)
                    fit = lm(as.formula(fm_str), data=mydata)
                    return(summary(fit)$coefficients[2, c(3,4)])})
imp_res = cbind(G_list2[keep_me, 1:2], do.call(rbind, stats))
colnames(imp_res)[3] = 'F'  # quick hack to work with function

adhd_imp_camera = get_enrich_order2( imp_res, t2 )
c5_imp_camera = get_enrich_order2( imp_res, c5_all)
dis_imp_camera = get_enrich_order2( imp_res, disorders)
dev_imp_camera = get_enrich_order2( imp_res, genes_unique )

gs05_int = intersect(rownames(c5_dream_cameraDC)[c5_dream_cameraDC$PValue<.05],
                     rownames(c5_imp_camera)[c5_imp_camera$PValue<.05])
gs01_int = intersect(rownames(c5_dream_cameraDC)[c5_dream_cameraDC$PValue<.01],
                     rownames(c5_imp_camera)[c5_imp_camera$PValue<.01])
ig05_int = intersect(resDC[resDC$P.Value<.05, 'hgnc_symbol'],
                     imp_res[imp_res[, 4]<.05, 'hgnc_symbol'])
ig01_int = intersect(resDC[resDC$P.Value<.01, 'hgnc_symbol'],
                     imp_res[imp_res[, 4]<.01, 'hgnc_symbol'])
print(sprintf('GO intersect .05: %d', length(gs05_int)))
print(sprintf('GO intersect .01: %d', length(gs01_int)))
print(sprintf('Individual gene intersect .05: %d', length(ig05_int)))
print(sprintf('Individual gene intersect .01: %d', length(ig01_int)))


# saving output
fname = sprintf('%s/%s_rnd%.4d.rData', out_dir, file_root, rnd_seed)
save('resDC', 'imp_res', 'c5_dream_cameraDC', 'c5_imp_camera', file='~/tmp/some_res.rdata')