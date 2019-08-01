# creates files to run in SOLAR and R, using slopes of different AROMA pipelines
# 
# GS, 07/2019

pipelines = c('fc-36p_despike')
        #     c('AROMA', 'AROMA-p5', 'AROMA-p25', 'fc-36p_despike', 'fc-36p',
        #   'fc-36p_scrub_p25', 'fc-36p_scrub_p5', 'fc-36p_spkreg')
fd_thresh = c(10, .25, .1)
# mvmt_file = '/Volumes/Labs/AROMA_ICA/xcp_movement.csv'
mvmt_file = '~/data/rsfmri/power264/xcp_movement.csv'
make_plots = T
pos_only = T

# make sure this file includes only kids, with correct amount of time between
# scans, etc
# scans_file = '/Volumes/Labs/AROMA_ICA/filtered_minFD_2scans.csv'
scans_file = '~/data/rsfmri/power264/filtered_minFD_2scans.csv'
scans = read.csv(scans_file)
subjs = unique(as.character(scans$subj))

mvmt = read.csv(mvmt_file)
subjs = unique(as.character(mvmt$subj))

source('~/research_code/lab_mgmt/merge_on_closest_date.R')

clin = read.csv('~/data/heritability_change/clinical_06262019.csv')

out_dir = '~/data/heritability_change/'
today = format(Sys.time(), "%m%d%Y")

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

for (p in pipelines) {
    pipe_dir = sprintf('~/data/rsfmri/power264/xcpengine_output_%s/', p)
    cat(sprintf('Reading connectivity data from %s\n', pipe_dir))
    for (t in fd_thresh) {
        fc = c()
        qc = c()
        sex = c()
        age = c()
        clean_subjs = c()
        # reading quality metric for all scans
        for (s in subjs) {
            midx = mvmt$subj==s & mvmt$pipeline==p
            # if scan was successfully processed in this pipeline
            if (sum(midx)>0 && mvmt[midx,]$power264 &&
                !any(is.na(mvmt[midx,]$meanFD < t))
                && mvmt[midx,]$meanFD < t) {
                clean_subjs = c(clean_subjs, s)
                fname = sprintf('%s/%s_power264_network.txt', pipe_dir, s)
                # fname = sprintf('%s/%s/fcon/power264/%s_power264_network.txt',
                #                 pipe_dir, s, s, s)
                data = read.table(fname)[, 1]
                fc = cbind(fc, data)
                qc = c(qc, mvmt[midx, 'meanFD'])
                sex = c(sex, scans[scans$subj == s, 'Sex'])
                age = c(age, scans[scans$subj == s, 'age_at_scan'])
            }
        }
        # grabbing which connections belong to each network
        fc = t(fc)
        cat(sprintf('Condensing data\n'))
        var_names = sapply(1:ncol(fc), function(x) sprintf('conn%d', x))
        colnames(fc) = var_names
        # set any negative correlations to NaN
        if (pos_only) {
            fc[fc < 0] = NaN
            pos_str = '_posOnly'
        } else {
            pos_str = ''
        }
        net_data = c()
        header = c()
        for (i in 1:nnets) {
            for (j in i:nnets) {
                cat(sprintf('Evaluating connections from %s to %s\n',
                            net_names[i], net_names[j]))
                idx = (conn_map[,2]==net_names[i] | conn_map[,2]==net_names[j] |
                    conn_map[,3]==net_names[i] | conn_map[,3]==net_names[j])
                res = apply(fc[, var_names[idx]], 1, mean, na.rm=T)
                net_data = cbind(net_data, res)
                res = apply(fc[, var_names[idx]], 1, median, na.rm=T)
                net_data = cbind(net_data, res)
                res = apply(fc[, var_names[idx]], 1, max, na.rm=T)
                net_data = cbind(net_data, res)
                for (op in c('Mean', 'Median', 'Max')) {
                    header = c(header, sprintf('conn%s_%sTO%s', op, net_names[i],
                                                net_names[j]))
                }
            }
        }
        header = gsub(' ', '', header)
        header = gsub('/', '', header)
        header = gsub('-', '', header)
        colnames(net_data) = header

        # keep only scans for the same subject
        cat(sprintf('Scans left at FD < %.2f (%d scans)\n', t, length(qc)))
        df = data.frame(clean_subjs, qc, net_data)
        m = merge(data.frame(clean_subjs), scans, by.x='clean_subjs',
                  by.y='subj')
        idx = which(table(m$Medical.Record...MRN)>1)
        long_subjs = names(table(m$Medical.Record...MRN))[idx]
        keep_me = c()
        for (i in 1:nrow(m)) {
            if (m[i, ]$Medical.Record...MRN %in% long_subjs) {
                keep_me = c(keep_me, i)
            }
        }
        m = m[keep_me,]
        m = merge(m, df, by='clean_subjs')

        # attaching clinicals
        df_var_names = colnames(m)[!grepl(colnames(m), pattern="^conn")]
        df = mergeOnClosestDate(m[, df_var_names], clin,
                                unique(m$Medical.Record...MRN),
                                x.date='record.date.collected...Scan',
                                x.id='Medical.Record...MRN')
        df2 = merge(df, m[, c('Mask.ID', header)], by='Mask.ID', all.x=F)

        # make sure we still have two scans for everyone
        rm_subjs = names(which(table(df2$Medical.Record...MRN)<2))
        rm_me = df2$Medical.Record...MRN %in% rm_subjs
        df2 = df2[!rm_me, ]
        mres = df2
        mres$SX_HI = as.numeric(as.character(mres$SX_hi))
        mres$SX_inatt = as.numeric(as.character(mres$SX_inatt))
        
        fname = sprintf('%s/rsfmri_%s_condensed%s_FD%.2f_scans%d_%s.csv',
                        out_dir, p, pos_str, t, nrow(mres), today)
        write.csv(mres, file=fname, row.names=F)

        if (make_plots) {
            dev.new()
            plot(sort(qc), main=sprintf('Sorted FD %s, thresh=%d', p, t))
            dev.new()
            mrns = unique(mres$Medical.Record...MRN)
            myvar = 'connMedian_DefaultmodeTODefaultmode'
            for (s in 1:length(mrns)) {
                idx = mres$Medical.Record...MRN==mrns[s]
                # if we still have 2 or more scans for this subject
                if (sum(idx > 2)) {
                    if (s == 1) {
                        plot(mres[idx, 'age_at_scan'],
                            mres[idx, myvar],
                            type='l',
                            xlim=c(min(mres$age_at_scan),
                                    max(mres$age_at_scan)),
                            ylim=c(min(mres[, myvar]), max(mres[, myvar])),
                            main=myvar, ylab='pearson r', xlab='age')
                    } else {
                        lines(mres[idx, 'age_at_scan'], mres[idx, myvar],
                              type='l')
                    }
                }
            }
        }
        # # create slopes
        # # for this to go fast, and taking advantage of just having 2 scans, we
        # # can just calculate the slopes manually
        # res = c()
        # for (s in unique(mres$Medical.Record...MRN)) {
        #     idx = which(mres$Medical.Record...MRN == s)
        #     row = c(s, unique(mres[idx, 'Sex']))
        #     phen_cols = c(conns, 'SX_inatt', 'SX_HI')
        #     y = mres[idx[2], phen_cols] - mres[idx[1], phen_cols]
        #     x = mres[idx[2], 'age_at_scan'] - mres[idx[1], 'age_at_scan']
        #     slopes = y / x
        #     row = c(row, slopes)

        #     # grabbing inatt and HI at baseline
        #     base_DOA = which.min(mres[idx, 'age_at_scan'])
        #     row = c(row, mres[idx[base_DOA], 'SX_inatt'])
        #     row = c(row, mres[idx[base_DOA], 'SX_HI'])
        #     # DX1 is DSMV definition, DX2 will make SX >=4 as ADHD
        #     if (mres[idx[base_DOA], 'age_at_scan'] < 16) {
        #         if ((row[length(row)] >= 6) || (row[length(row)-1] >= 6)) {
        #             DX = 'ADHD'
        #         } else {
        #             DX = 'NV'
        #         }
        #     } else {
        #         if ((row[length(row)] >= 5) || (row[length(row)-1] >= 5)) {
        #             DX = 'ADHD'
        #         } else {
        #             DX = 'NV'
        #         }
        #     }
        #     if ((row[length(row)] >= 4) || (row[length(row)-1] >= 4)) {
        #         DX2 = 'ADHD'
        #     } else {
        #         DX2 = 'NV'
        #     }
        #     row = c(row, DX)
        #     row = c(row, DX2)
        #     res = rbind(res, row)
        #     print(nrow(res))
        # }
        # colnames(res) = c('ID', 'sex', conns, c('SX_inatt', 'SX_HI',
        #                                             'inatt_baseline',
        #                                             'HI_baseline', 'DX', 'DX2'))
        
        # # and we do a shortened version in the residualized data
        # res_resid = res
        # cnt = 1
        # for (s in unique(res$ID)) {
        #     idx = which(m_resids$Medical.Record...MRN == s)
        #     y = m_resids[idx[2], conns] - m_resids[idx[1], conns]
        #     x = m_resids[idx[2], 'age_at_scan'] - m_resids[idx[1],
        #                                                    'age_at_scan']
        #     slopes = y / x
        #     res_resid[cnt, conns] = slopes
        #     cnt = cnt + 1
        # }

        # cat(sprintf('Writing association files to disk\n'))

        # fname = sprintf('%s/rsfmri_AROMA%s_FD%.2f_slopes_n%d_%s.csv',
        #                 out_dir, p, t, nrow(res), today)
        # write.csv(res, file=fname, row.names=F)
        # fname = sprintf('%s/rsfmri_AROMA%s_FD%.2f_residSlopes_n%d_%s.csv',
        #                 out_dir, p, t, nrow(res), today)
        # write.csv(res_resid, file=fname, row.names=F)

        # # special dataset for SOLAR, containing only people with relatives
        # # make sure every family has at least two people
        # good_nuclear = names(table(m$Nuclear.ID...FamilyIDs))[table(m$Nuclear.ID...FamilyIDs) >= 4]
        # good_extended = names(table(m$Extended.ID...FamilyIDs))[table(m$Extended.ID...FamilyIDs) >= 4]
        # keep_me = c()
        # for (f in good_nuclear) {
        #     keep_me = c(keep_me, m[which(m$Nuclear.ID...FamilyIDs == f),
        #                             'Medical.Record...MRN'])
        # }
        # for (f in good_extended) {
        #     keep_me = c(keep_me, m[which(m$Extended.ID...FamilyIDs == f),
        #                             'Medical.Record...MRN'])
        # }
        # keep_me = unique(keep_me)

        # fam_subjs = c()
        # for (s in keep_me) {
        #     fam_subjs = c(fam_subjs, which(res[, 'ID'] == s))
        # }
        # res2 = res[fam_subjs, ]
        # res2_resid = res_resid[fam_subjs, ]

        # cat(sprintf('Writing family files to disk\n'))
        
        # fname = sprintf('%s/rsfmri_AROMA%s_FD%.2f_slopesFam_n%d_%s.csv',
        #                 out_dir, p, t, nrow(res2), today)
        # write.csv(res2, file=fname, row.names=F, na='', quote=F)

        # fname = sprintf('%s/rsfmri_AROMA%s_FD%.2f_residSlopesFam_n%d_%s.csv',
        #                 out_dir, p, t, nrow(res2), today)
        # write.csv(res2_resid, file=fname, row.names=F, na='', quote=F)        
    }
}



comp = data.frame(subjs=mres_36p$clean_subjs, P36=NA, P36_despike=NA,
                  P36_spkreg=NA, P36_scrub_p5=NA, P36_despike_posonly=NA, P36_scrub_p25=NA, aroma=NA)
for (s in comp$subjs) {
    idx = mres_36p$clean_subjs==s
    comp[comp$subjs==s, ]$P36 = mres_36p[idx,
                                         'connMedian_DefaultmodeTODefaultmode']
    idx = mres_36p_despike$clean_subjs==s
    if (sum(idx) > 0) {
        comp[comp$subjs==s, ]$P36_despike = mres_36p_despike[idx,
                                      'connMedian_DefaultmodeTODefaultmode']
    }
    idx=mres_36p_spkreg$clean_subjs==s
    if (sum(idx) > 0) {
        comp[comp$subjs==s, ]$P36_spkreg = mres_36p_spkreg[idx,
                                     'connMedian_DefaultmodeTODefaultmode']
    }
    idx=mres_36p_scrub_p5$clean_subjs==s
    if (sum(idx) > 0) {
        comp[comp$subjs==s, ]$P36_scrub_p5 = mres_36p_scrub_p5[idx,
                                     'connMedian_DefaultmodeTODefaultmode']
    }
    idx=mres_36p_scrub_p25$clean_subjs==s
    if (sum(idx) > 0) {
        comp[comp$subjs==s, ]$P36_scrub_p25 = mres_36p_scrub_p25[idx,
                                     'connMedian_DefaultmodeTODefaultmode']
    }
    idx=mres_36p_despike_posonly$clean_subjs==s
    if (sum(idx) > 0) {
        comp[comp$subjs==s, ]$P36_despike_posonly = mres_36p_despike_posonly[idx,
                                     'connMedian_DefaultmodeTODefaultmode']
    }
    idx=mres_aroma$clean_subjs==s
    if (sum(idx) > 0) {
        comp[comp$subjs==s, ]$aroma = mres_aroma[idx,
                                     'connMedian_DefaultmodeTODefaultmode']
    }
}
library(tidyr)
comp_long = gather(comp, pipeline, pearsonr, P36:aroma)
dev.new()
ggplot(comp_long, aes(x=pipeline, y=pearsonr, color=subjs)) + geom_point() + theme(legend.position='none')