# Condense the 264 x 264 matrix using max, mean, and median for each network, so
# that we have a within and across network final matrix.
#
# GS 07/2019

args <- commandArgs(trailingOnly = TRUE)
fname = args[1]

today = format(Sys.time(), "%m%d%Y")

m = read.csv(fname)
var_names = colnames(m)[grepl(colnames(m), pattern="conn")]

fname_root = sub('.csv', '', fname)

nets = read.csv('~/research_code/fmri/Neuron_consensus_264.csv')
net_names = as.character(unique(nets$system))
nnets = length(net_names)

# figure out which connection goes to which network
nverts = nrow(nets)
cnt = 1
conn_map = c()
for (i in 1:(nverts-1)) {
    for (j in (i+1):nverts) {
        conn = sprintf('conn%d', cnt)
        conn_map = rbind(conn_map, c(conn, as.character(nets$system[i]),
                                     as.character(nets$system[j])))
    }
}

# grabbing which connections belong to each network
net_data = c()
header = c()
for (i in 1:nnets) {
    for (j in i:nnets) {
        cat(sprintf('Evaluating connections from %s to %s\n',
                    net_names[i], net_names[j]))
        idx = (conn_map[,2]==net_names[i] | conn_map[,2]==net_names[j] |
               conn_map[,3]==net_names[i] | conn_map[,3]==net_names[j])
        res = apply(m[, var_names[idx]], 1, mean, na.rm=T)
        net_data = cbind(net_data, res)
        res = apply(m[, var_names[idx]], 1, median, na.rm=T)
        net_data = cbind(net_data, res)
        res = apply(m[, var_names[idx]], 1, max, na.rm=T)
        net_data = cbind(net_data, res)
        for (op in c('Mean', 'Median', 'Max')) {
            header = c(header, sprintf('conn%s_%sTO%s', op, net_names[i],
                                        net_names[j]))
        }
    }
}

# cleaning up weird phenotype names
header = gsub(' ', '', header)
header = gsub('/', '', header)
header = gsub('-', '', header)
colnames(net_data) = header
other_var_names = colnames(m)[!grepl(colnames(m), pattern="conn")]
data = cbind(m[, other_var_names], net_data)

fname = sprintf('%sCondensed.csv', fname_root)
write.csv(data, file=fname, row.names=F)
