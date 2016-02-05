gf_data = read.csv('~/data/motor/ABC_cerebellum_sublobar.csv')
ce_data = read.csv('~/data/motor/ABC_cerebellum_sublobar.csv')
co_data = read.csv('~/data/motor/ABC_cerebellum_sublobar.csv')

# all variables in each array to be used
ce_vars = 174:179
co_vars = 95:147
gf_vars = c(21, 24, 27, 30)

# which subjects to use
idx = 1:dim(gf_data)[1]

pvals = array(dim=c(length(gf_vars),length(co_vars),length(ce_vars)))
for (g in 1:length(gf_vars)) {
    cat(g,'\n')
    for (e in 1:length(ce_vars)) {
        for (o in 1:length(co_vars)) {
            fit = lm(gf_data[idx,gf_vars[g]] ~ 
                         co_data[idx,co_vars[o]]*ce_data[idx,ce_vars[e]])
            pvals[g, o, e] = summary(fit)$coefficients[4,4]
        }
    }
}
