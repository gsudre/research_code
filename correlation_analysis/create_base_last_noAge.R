load('~/data/structural/SA_data_noAge_matched_on18_dsm4.RData')
fname_suffix = '_noAge_SA_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_on18_dsm4.csv'
brain_data = c('dt%s_thalamus_1473', 'dt%s_striatum_1473', 'dt%s_gp', 'dt%s_cortex_SA_1473')
brain_names = c('thalamus', 'striatum', 'gp', 'cortex')
cnt = 1
for (i in brain_data) {
    cat('Working on', brain_names[cnt], '\n')
    for (h in c('L', 'R')) {
        for (g in c('NV', 'remission', 'persistent')) {
            idx = which(idx_base[group==sprintf('"%s"',g)])
            eval(parse(text=sprintf('mytable=t(%s[idx,])', sprintf(i, h))))
            print(dim(mytable))
            write.csv(mytable,file=sprintf('~/data/structural/base_%s%s_%s%s',
                                           brain_names[cnt], h, g, fname_suffix))
            idx = which(idx_last[group==sprintf('"%s"',g)])
            eval(parse(text=sprintf('mytable=t(%s[idx,])', sprintf(i, h))))
            print(dim(mytable))
            write.csv(mytable,file=sprintf('~/data/structural/last_%s%s_%s%s',
                                           brain_names[cnt], h, g, fname_suffix))
        }
    }
    cnt = cnt + 1
}
