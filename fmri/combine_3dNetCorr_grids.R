# Collect the results of 3dNetCorr, and combines them based on different
# networks. Note that this is more applicable to the Power atlas that Luke has
# suggested we should use.
#
# GS 05/2019

subj_dir = '/Volumes/Shaw/Gustavo/desktop_backup/data/heritability_change/fmri_corr_tables/'
subjs = read.csv(sprintf('%s/../rsfmri_3min_assoc_n462.csv', subj_dir))[,'Mask.ID']
# removing subjects/scans with not all ROIs
subjs = subjs[subjs!=1361]
subjs = subjs[subjs!=1828]
subjs = subjs[subjs!=2130]
subjs = subjs[subjs!=1988]

nets = read.csv('~/data/heritability_change/fmri_same_space/Neuron_consensus_264.csv')
nets = nets[nets$net_num>=0,]
nnets = length(unique(nets$net_num))
net_names = c()
for (i in 1:nnets) {
    net_names = c(net_names,
                  unique(as.character(nets[nets$net_num==i, 'net_name'])))
}
for (parc in c('power')) {
    data = c()
    for (s in subjs) {
        print(s)
        a = read.table(sprintf('%s/%04d_%s_000.netcc', subj_dir, s, parc),
                       header=1)
        # remove weird integer row
        b = a[2:nrow(a),]
        # split matrix into first set of rows as Rs, second set as Zs
        rs = b[1:ncol(b),]
        zs = b[(ncol(b)+1):nrow(b),]

        # grabbing which connections belong to each network
        net_data = as.data.frame(matrix(nrow=nnets, ncol=nnets))
        for (i in 1:nnets) {
            for (j in 1:nnets) {
                # note that we're doing this only for Rs, but we could as easily do it for Zs!
                conn = rs[nets[nets$net_num == i, 1], nets[nets$net_num == j, 1]]
                if (i == j) {
                    net_data[i, j] = mean(conn[upper.tri(conn, diag=F)])
                } else {
                    net_data[i, j] = mean(rowMeans(conn))
                }
            }
        }
        rownames(net_data) = net_names
        colnames(net_data) = net_names
    
        b.tri = net_data[upper.tri(net_data, diag=T)]
        # format a header for the vectorized version of the table
        w = which(upper.tri(net_data, diag=T), arr.ind = TRUE)
        header = sapply(1:length(b.tri),
                        function(i) sprintf('%s.TO.%s', net_names[w[i,1]],
                                                        net_names[w[i,2]]))
        # concatenate vectorized matrices for the same mask id in the same row
        subj_data = c(s, b.tri)
        names(subj_data) = c('mask.id', header)  

        data = rbind(data, subj_data)
    }
    # rename it so that each row is a mask id
    write.csv(data, file=sprintf('%s/pearson_3min_n462_%s.csv', subj_dir, parc),
              row.names=F)
}
