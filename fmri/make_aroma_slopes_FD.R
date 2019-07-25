# creates files to run in SOLAR and R, using slopes of different AROMA pipelines
# 
# GS, 07/2019

pipelines = c('')#, '-gsr')
fd_thresh = c(1)#, .2)
mvmt_file = '/Volumes/Labs/AROMA_ICA/xcp_movement.csv'

# make sure this file includes only kids, with correct amount of time between
# scans, etc
scans_file = '/Volumes/Labs/AROMA_ICA/filtered_minFD_2scans.csv'
scans = read.csv(scans_file)
subjs = unique(as.character(scans$subj))

mvmt = read.csv(mvmt_file)

source('~/research_code/lab_mgmt/merge_on_closest_date.R')

clin = read.csv('~/data/heritability_change/clinical_06262019.csv')

out_dir = '~/data/heritability_change/'
today = format(Sys.time(), "%m%d%Y")

for (p in pipelines) {
    pipe_dir = sprintf('~/data/AROMA_ICA/connectivity/xcpengine_output_AROMA%s/', pipeline)
    cat(sprintf('Reading connectivity data from %s\n', pipe_dir))
    for (t in fd_thresh) {
        fc = c()
        qc = c()
        sex = c()
        age = c()
        clean_subjs = c()
        # reading quality metric for all scans
        for (s in subjs) {
            midx = mvmt$subj==s & mvmt$pipeline==pipeline
            # if scan was successfully processed in this pipeline
            if (mvmt[midx,]$fcon && mvmt[midx,]$meanFD < t) {
                clean_subjs = c(clean_subjs, s)
                fname = sprintf('%s/%s_power264_network.txt', pipe_dir, s)
                data = read.table(fname)[, 1]
                fc = cbind(fc, data)
                qc = c(qc, mvmt[midx, 'meanFD'])
                sex = c(sex, scans[scans$subj == s, 'Sex'])
                age = c(age, scans[scans$subj == s, 'age_at_scan'])
            }
        }
        fc = t(fc)
        colnames(fc) = sapply(1:ncol(fc), function(x) sprintf('conn%d', x))
        # keep only scans for the same subject
        cat(sprintf('Scans left at FD < %.2f (%d scans)\n', t, length(qc)))
        df = data.frame(clean_subjs, qc, fc)
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
        cat(sprintf('Residualizing %d scans after longitudinal filter\n',
                    nrow(m)))
        m_resids = m
        conns = colnames(m)[grepl(colnames(m), pattern='^conn')]
        for (conn in conns) {
            m_resids[, conn] = residuals(lm(m[, conn] ~ m$qc,
                                            na.action=na.exclude))
        }

        # attaching clinicals
        df_var_names = colnames(m)[!grepl(colnames(m), pattern="^conn")]
        df = mergeOnClosestDate(m[, df_var_names], clin,
                                unique(m$Medical.Record...MRN),
                                x.date='record.date.collected...Scan',
                                x.id='Medical.Record...MRN')
        df2 = merge(df, m[, c('Mask.ID', conns)], by='Mask.ID', all.x=F)

        # make sure we still have two scans for everyone
        rm_subjs = names(which(table(df2$Medical.Record...MRN)<2))
        rm_me = df2$Medical.Record...MRN %in% rm_subjs
        df2 = df2[!rm_me, ]
        mres = df2
        mres$SX_HI = as.numeric(as.character(mres$SX_hi))
        mres$SX_inatt = as.numeric(as.character(mres$SX_inatt))
        
        # create slopes
        # for this to go fast, and taking advantage of just having 2 scans, we
        # can just calculate the slopes manually
        res = c()
        for (s in unique(mres$Medical.Record...MRN)) {
            idx = which(mres$Medical.Record...MRN == s)
            row = c(s, unique(mres[idx, 'Sex']))
            phen_cols = c(conns, 'SX_inatt', 'SX_HI')
            y = mres[idx[2], phen_cols] - mres[idx[1], phen_cols]
            x = mres[idx[2], 'age_at_scan'] - mres[idx[1], 'age_at_scan']
            slopes = y / x
            row = c(row, slopes)

            # grabbing inatt and HI at baseline
            base_DOA = which.min(mres[idx, 'age_at_scan'])
            row = c(row, mres[idx[base_DOA], 'SX_inatt'])
            row = c(row, mres[idx[base_DOA], 'SX_HI'])
            # DX1 is DSMV definition, DX2 will make SX >=4 as ADHD
            if (mres[idx[base_DOA], 'age_at_scan'] < 16) {
                if ((row[length(row)] >= 6) || (row[length(row)-1] >= 6)) {
                    DX = 'ADHD'
                } else {
                    DX = 'NV'
                }
            } else {
                if ((row[length(row)] >= 5) || (row[length(row)-1] >= 5)) {
                    DX = 'ADHD'
                } else {
                    DX = 'NV'
                }
            }
            if ((row[length(row)] >= 4) || (row[length(row)-1] >= 4)) {
                DX2 = 'ADHD'
            } else {
                DX2 = 'NV'
            }
            row = c(row, DX)
            row = c(row, DX2)
            res = rbind(res, row)
            print(nrow(res))
        }
        colnames(res) = c('ID', 'sex', conns, c('SX_inatt', 'SX_HI',
                                                    'inatt_baseline',
                                                    'HI_baseline', 'DX', 'DX2'))
        
        # and we do a shortened version in the residualized data
        res_resid = res
        cnt = 1
        for (s in unique(res$ID)) {
            idx = which(m_resids$Medical.Record...MRN == s)
            y = m_resids[idx[2], conns] - mres[idx[1], conns]
            x = m_resids[idx[2], 'age_at_scan'] - m_resids[idx[1],
                                                           'age_at_scan']
            slopes = y / x
            res_resid[cnt, conns] = slopes
            cnt = cnt + 1
        }

        fname = sprintf('%s/rsfmri_AROMA%s_FD%.2f_slopes_n%d_%s.csv',
                        out_dir, p, t, nrow(res), today)
        write.csv(res, file=fname, row.names=F)
        fname = sprintf('%s/rsfmri_AROMA%s_FD%.2f_residSlopes_n%d_%s.csv',
                        out_dir, p, t, nrow(res), today)
        write.csv(res_resid, file=fname, row.names=F)

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
        # res2_clean = res_clean[fam_subjs, ]

        # fname = sprintf('%sFamsSlopes_n%d_%s.csv', fname_root, nrow(res2), today)
        # write.csv(res2, file=fname, row.names=F, na='', quote=F)

        # fname = sprintf('%sFamsSlopesClean_n%d_%s.csv', fname_root, nrow(res2_clean), today)
        # write.csv(res2_clean, file=fname, row.names=F, na='', quote=F)        
    }
}
