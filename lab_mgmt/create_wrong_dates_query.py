# Script that makes it easier to create the annoyingly long SQL query for wrongly formatted dates (i.e. blanks and DOBs)

# output file
sql_file = '/Users/sudregp/tmp/test_report.sql'

# all tables
tables = ['ADHD Rating ', 'Adult Self-Report', 'APSD', 'ARI ', 'Autism Screener ', 'Beery VMI', 'BRIEF Adult Self', 'BRIEF Children Self', 'BRIEF Parent', 'BRIEF Teacher', 'CAADID', 'CAARS Self Report ', 'CBCL', 'CBCL 1.5-5 y.o.', 'ClinicianAdministeredSX', 'Conners Parent Rev ', 'Conners Self ', 'Conners Teacher ', 'Conners Teacher Rev ', 'ConsentFormGenetics', 'CPT', 'DCDQ ', 'DICA', 'Family Enviro Scale ', 'Fluency (FAS + Animals)', 'Medication Log', 'Movement ABC 11-16yr', 'Movement ABC 3-6yr', 'Movement ABC 7-10yr', 'NV Interview', 'Prelim. Parent Rpt ', 'Scan', 'SCID', 'Side effects rating scale', 'SNAP-IV', 'SRS', 'Symptom Count', 'Trails', 'TRF', 'TRF 1.5-5 y.o.', 'Visit', 'WASI-I', 'WASI-II', 'Wenders ', 'WISC', 'Woodcock-Johnson', 'WPPSI-III', 'WPPSI-IV', 'WTAR']

fid = open(sql_file, 'w')
fid.write('DECLARE @Collector TABLE(name VARCHAR(100), mrn VARCHAR(100), curDate DATE, cdf VARCHAR(100))')

for table in tables:
    fid.write('\nINSERT INTO @Collector\nSELECT DISTINCT [MART_SubjectInformation].[subject_full_name], [MART_SubjectInformation].[medical_record], [MART_EX_FORM_%s].[date_collected], \'%s\'\nFROM [MART_EX_FORM_%s],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_%s].[subject_id]=[MART_SubjectInformation].[subject_id] AND (DATEPART("year",[MART_EX_FORM_%s].[date_collected])<=DATEPART("year",[MART_SubjectInformation].[birth_date]) OR DATEPART("year",ISNULL([MART_EX_FORM_%s].[date_collected], \'\'))=1900)' % (table, table, table, table, table, table))

# column headers
fid.write('\nSELECT name AS SubjectName, mrn AS MRN, curDate AS Date, cdf AS CustomDataForm FROM @Collector')

fid.close()