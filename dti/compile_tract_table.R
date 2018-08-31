# Takes the mean over the whole DTI tract so we can condense the DTI data to one number per tract
tract_names = c('left_cst', 'left_ifo', 'left_ilf', 'left_slf', 'left_unc', 'right_cst', 'right_ifo', 'right_ilf', 'right_slf', 'right_unc', 'cc')
var_names = c('FA', 'AD', 'RD')#, 'MO')

subj_file = '~/data/tmp/base_subjs.txt'
data_dir = '~/data/tmp/'
in_fname = 'mean_sampling.gzip'
# out_fname = 'dti_max_phenotype_cleanedWithinTract3sd.csv'
out_fname = 'dti_mean_phenotype.csv'

load(sprintf('%s/%s',data_dir,in_fname))
subjs = read.table(subj_file)
res = as.data.frame(subjs)
titles = c('file')

rm_me = c()
# take the mean over all voxels
for (tract in tract_names) {
    # compute mode of anisotropy for the tract
    #eval(parse(text=sprintf('eig1 = eig1_%s', tract)))
    #eval(parse(text=sprintf('eig2 = eig2_%s', tract)))
    #eval(parse(text=sprintf('eig3 = eig3_%s', tract)))
    #data = ((-eig1-eig2+2*eig3) * (2*eig1-eig2-eig3) * (-eig1+2*eig2-eig3)) /
    #       2*sqrt((eig1**2+eig2**2+eig3**2-eig1*eig2-eig2*eig3-eig3*eig1)**3)
    #eval(parse(text=sprintf('MO_%s = data', tract)))
    for (var in var_names) {
        eval(parse(text=sprintf('data = %s_%s', var, tract)))
        this_title = sprintf('%s_%s', var, tract)
        titles = c(titles, this_title)
        tract_data = colMeans(data)

        # identifying outliers
        ul = mean(tract_data) + 3 * sd(tract_data)
        ll = mean(tract_data) - 3 * sd(tract_data)
        bad_subjs = c(which(tract_data<ll),which(tract_data>ul))
        rm_me = c(rm_me, bad_subjs)

        # remove within-tract outliers
        #tract_data[bad_subjs] = NA

        res = cbind(res,tract_data)
    }
}
# keeping only mask ids in the first column
res[,1] = as.character(res[,1])
cnt=1
for (subj in res[,1]) {
    res[cnt,1] = unlist(strsplit(subj,'_'))[1]
    cnt = cnt + 1
}

# # removing outliers (very strict!)
# res = res[-unique(rm_me),]

# # scale the data
# nfeats = dim(res)[2]
# res[,2:nfeats] = scale(res[,2:nfeats])

colnames(res)=titles
write.csv(res, file=sprintf('%s/%s',data_dir,out_fname),row.names=FALSE,na='')
