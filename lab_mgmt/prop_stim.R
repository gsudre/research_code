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
db_file = '~/Downloads/stim_durations_02282019.csv'

# for each entry in main file
# figure out all DB entries for the person
# yell if the user is not in the database!
# calculate how many days that interval represents for the person
# check how many days in that interval the person was taking medication