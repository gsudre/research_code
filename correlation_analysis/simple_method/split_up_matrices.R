# splits up the files from create_matrices into smaller files per region
hemi = 'R'
other = c('gp','striatum','cortex')
time = c('baseline','last','delta','diff')
groups = c('remission', 'persistent', 'NV')

for (g in groups) {
    for (t in time) {
        cat(g,t,'\n')
        if (hemi=='R') {
            load(sprintf('~/data/results/structural_v2/es_%s_%s.RData',g,t))
        } else {
            load(sprintf('~/data/results/structural_v2/es_%s_%s_left.RData',g,t))
        }
        for (o in other) {
            eval(parse(text=sprintf('es = esThalamus%s%s%s',hemi,o,hemi)))
            save(es,file=sprintf('~/data/results/structural_v2/es%s_thalamus2%s_%s_%s.RData',
                                 hemi, o, t, g))
        }
    }
}
