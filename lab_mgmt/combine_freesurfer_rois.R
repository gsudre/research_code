# combines Freesurfer ROIs based on pre-defined regions
# GS, 10/2020

library(gdata)
# grab the brain data and ROIs file
xlsx_fname <- "~/OneDrive - National Institutes of Health/WES_phenotypes.xlsx"
out_fname <- "~/tmp/more_brain_data.csv"
brain_data <- read.xls(xlsx_fname, "anatomic")
rois <- read.csv("~/research_code/REGIONAL_ANALYSES_FREESURFER.csv")

for (mod in c("_thickness", "_area", "_volume")) {
    brain_vars <- colnames(brain_data)[grepl(colnames(brain_data),
                                       pattern = mod)]
    for (part in c("lobar", "sublobar", "theoryDriven")) {
        new_brain_vars = c()
        for (roi in unique(rois[, part])) {
            # grab all the labels for each ROI in this part
            labels = rois[which(rois[, part]==roi), 'region']
            to_avg = c()
            for (l in labels) {
                val = brain_vars[grepl(brain_vars, pattern=sprintf("^%s", l))]
                to_avg = c(to_avg, val)
            }
            # only use variable if it's selected initially and defined
            if (length(to_avg) > 0 && sum(is.na(brain_data[, to_avg])) == 0 &&
                nchar(roi) > 0) {
                roi_name <- sprintf("%s_%s", part, roi)
                if (length(to_avg) == 1) {
                    brain_data[, roi_name] <- brain_data[, to_avg]
                } else {
                    brain_data[, roi_name] <- rowMeans(brain_data[, to_avg])
                }
            }
        }
    }
}
write.csv(brain_data, file = out_fname, row.names = F)