# Script to flag any irregularities in Biosamples Custom Data form in Labmatrix.
# Start by running a query that spits out ALL biosamples entries. Including the
# default columns is fine. Then, save as a CSV in Excel and run the script.
#
# Usage: Rscript ~/research_code/lab_mgmt/flag_labmatrix_biosamples_errors.R \
# /Users/sudregp/Downloads/Results.csv > ~/tmp/biosamples_report_01172019.txt
#
# GS, 01/2019

args <- commandArgs(trailingOnly = TRUE)
query_fname = args[1]

data = read.csv(query_fname)
options(width=1000)  # don't split rows when printing to screen

print_table = function(df) {
    s = sort(df[, 'NSB'], index.return=T)
    print(df[s$ix, ], row.names=F)
    cat(sprintf('Total: %d\n', nrow(df)))
    cat('========================\n\n')
}

cat('\nItems in inventory but have Date Out or Destination not blank. Are they really here?\n')
idx1 = data$Status == 'In Inventory'
idx2 = data$Date.Out != ''
idx3 = data$Destination != ''
idx = idx1 & (idx2 | idx3)
print_table(data[idx, c('NSB', 'Date.Out', 'Type', 'Destination', 'Location',
                        'Box', 'Position')])

cat('\nItems not in inventory but have no Date Out or Destination. Where are they? When were they sent?\n')
idx1 = data$Status != 'In Inventory'
idx2 = data$Date.Out == ''
idx3 = data$Destination == ''
idx = idx1 & (idx2 | idx3)
print_table(data[idx, c('NSB', 'Date.Out', 'Type', 'Destination', 'Notes')])

cat('\nSubject samples without a Date In. When were these samples collected?\n')
idx1 = data$Date.In == ''
idx2 = data$Source == 'Subject'
idx = idx1 & idx2
print_table(data[idx, c('NSB', 'Source', 'Date.Out', 'Type', 'Destination', 
                        'Notes')])

cat('\nOther items without a Date In. We should know when we received stuff!\n')
idx1 = data$Date.In == ''
idx2 = data$Source != 'Subject'
idx = idx1 & idx2
print_table(data[idx, c('NSB', 'Source', 'Date.Out', 'Type', 'Destination',
                        'Notes')])

cat('\nItems in inventory but no location information. Are they really here?\n')
idx1 = data$Status == 'In Inventory'
idx2 = data$Location == ''
idx3 = grepl(data$Type, pattern='Saliva')
idx4 = data$Box == ''
idx5 = data$Position == ''
idx = idx1 & (idx2 | (!idx3 & (idx4 | idx5)))
print_table(data[idx, c('NSB', 'Date.Out', 'Type', 'Destination', 'Location',
                        'Box', 'Position')])

# this will be needed by many queries...
nsbs = unique(data$NSB)

cat('\nNSBs changing tissue types. Which one is it?\n')
cnt = 0
bad = c()
# only the non-data entries
idx2 = grepl(data$Type, pattern='data')
for (i in nsbs) {
    idx1 = data$NSB == i
    idx = idx1 & !idx2
    if (sum(grepl(data[idx,]$Type, pattern='Saliva')) > 0) {
        if (sum(grepl(data[idx,]$Type, pattern='Blood')) > 0) {
            bad = rbind(bad, data[idx, ])
            cnt = cnt + 1
        }
    } else {
        if (sum(grepl(data[idx,]$Type, pattern='Saliva')) > 0) {
            bad = rbind(bad, data[idx, ])
            cnt = cnt + 1
        }
    }

}
print_table(bad[, c('NSB', 'Type')])

cat('\nExtracted DNA without volume or concentration. We need both for analysis!\n')
idx1 = grepl(data$Type, pattern='DNA')
idx2 = is.na(data$Volume)
idx3 = is.na(data$Concentration)
idx = idx1 & (idx2 | idx3)
print_table(data[idx, c('NSB', 'Source', 'Type', 'Location', 'Box', 'Position')])

cat('\nNSBs without a source == Subject entry. How do we know when it was collected?\n')
cnt = 0
bad = c()
for (i in nsbs) {
    idx = data$NSB == i
    idx1 = which(data[idx,]$Source == 'Subject')
    if (length(idx1) == 0) {
        bad = rbind(bad, data[idx, ])
        cnt = cnt + 1
    }
}
print_table(bad[, c('NSB', 'Source', 'Type')])

cat('\nItems with a Date Out not later than Date In. How is that even possible?\n')
idx1 = data$Date.In != ''
idx2 = data$Date.Out != ''
dated = data[idx1 & idx2, ]
date_in = as.Date(dated$Date.In, format='%m/%d/%Y')
date_out = as.Date(dated$Date.Out, format='%m/%d/%Y')
idx = date_out <= date_in
print_table(dated[idx, c('NSB', 'Date.In', 'Date.Out', 'Source', 'Destination',
                         'Type')])

cat('\nNSBs with different MRNs. One NSB should map to one and only one MRN!\n')
cnt = 0
bad = c()
for (i in nsbs) {
    idx = data$NSB == i
    subjs = unique(data[idx,]$subject.id)
    if (length(subjs) > 1) {
        bad = rbind(bad, data[idx, ])
        cnt = cnt + 1
    }
}
print_table(bad[, c('NSB', 'subject.id', 'Status', 'Notes')])

# TODO
# NSBs without complete history
# Upload DNA Genotek box, volumes and concentrations
# date ins and outs need to be chronological order
# add date in for processed stuff
# Change NSBs Steven PC cleaned himself to indicate that and create new record of old sample with in date
# Make sure all locations make sense
# Check that all unique boxes in the database actually exist, and vice-versa
# Add results and history for methyl data as well
# Correct date in for samples Steven cleaned (make sure they have originating samples first)
# check Blood_missing_MRNs Steven has in his folder
# maybe flag NSBs out of order with date in subject