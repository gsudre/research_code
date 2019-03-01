# Calculates the proportion of time a person was using stimulants

# check_file: mrn, date start, date end to be assessed
# db_file: mrn, date start, date end. BE AWARE that he DB file has several caveats...
# much of the DB file is estimated. So, if a year is in the end column, it means
# taken prior to that year. If a year is in the start column, it means some time
# that year. Be aware of keywords such as none, before_study, and current
# for the start date, let's take it as first of January in the year to make sure
# we capture the visit. For the end date, do the same thing, as we want the
# entire period up to the start of that year.
check_file = '~/tmp/check_me.csv'
db_file = '~/Documents/stim_duration_03012019.csv'
out_file = '~/tmp/prop_stim.csv'

data = read.csv(check_file, colClasses='character')
stim_dur = read.csv(db_file, colClasses='character')

data$prop_stim = NA

# for each entry in main file
for (r in 1:nrow(data)) {
    mrn = data[r, 'MRN']
    # figure out all DB entries for the person
    db_entries = stim_dur[stim_dur$MRN == mrn, ]
    # yell if the user is not in the database!
    if (nrow(db_entries) == 0) {
        print(sprintf('%s not in medication database!', mrn))
    } else {
        # calculate how many days that interval represents for the person
        check_date1 = as.Date(data[r, 2], format='%m/%d/%y')
        check_date2 = as.Date(data[r, 3], format='%m/%d/%y')
        delta_days = as.numeric(check_date2 - check_date1)
        
        # now check how many of the periods in the medication database overlap
        # with the period being analyzed
        days_stim = 0
        for (dbr in 1:nrow(db_entries)) {
            if (db_entries[dbr, 'Start.date'] == 'none') {
                days_stim = 0
            } else {
                if (db_entries[dbr, 'Start.date'] == 'before_study') {
                    db_date1 = check_date1
                } else {
                    if (nchar(db_entries[dbr, 'Start.date']) == 4) {
                        db_date1 = as.Date(sprintf('1/1/%s', db_entries[dbr, 'Start.date']),
                                     format='%m/%d/%Y')
                    } else {
                        db_date1 = as.Date(db_entries[dbr, 'Start.date'], format='%m/%d/%y')
                    }
                }
                if (db_entries[dbr, 'End.date'] == 'current') {
                    db_date2 = check_date2
                } else {
                    if (nchar(db_entries[dbr, 'End.date']) == 4) {
                        last_year = as.numeric(db_entries[dbr, 'End.date']) - 1
                        db_date2 = as.Date(sprintf('12/31/%s', last_year),
                                     format='%m/%d/%Y')
                    } else {
                        db_date2 = as.Date(db_entries[dbr, 'End.date'], format='%m/%d/%y')
                    }
                }
                # now that I have all dates in Date format, let's do some
                # operations
                if (db_date1 > check_date2 || db_date2 < check_date1) {
                    days_stim = days_stim + 0
                } else if (db_date1 >= check_date1 && db_date2 <= check_date2) {
                    days_stim = days_stim + as.numeric(db_date2 - db_date1)
                } else if (db_date1 < check_date1 && db_date2 <= check_date2) {
                    days_stim = days_stim + as.numeric(db_date2 - check_date1)
                } else if (db_date1 < check_date1 && db_date2 > check_date2) {
                    days_stim = days_stim + as.numeric(check_date2 - check_date1)
                } else {
                    print('not sure what to do')
                    print(data[r, ])
                    print(db_entries[, 1:3])
                    print(db_date1)
                    print(db_date2)
                    print(check_date1)
                    print(check_date2)
                }
            }
            data[r, 'prop_stim'] = days_stim / delta_days
        }
    }
}

write.csv(data, file=out_file, row.names=F)