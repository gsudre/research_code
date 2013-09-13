# Script that makes it easier to create the annoyingly long SQL query to create reporting table

# output file
sql_file = '/Users/sudregp/tmp/test_report.sql'
# list of lists. Each list contains a tuple that represents the variable names/column title, and the specific name of each form in the Labmatrix databse
tables = [['ADHDRating', 'ADHD Rating '], ['AdultSelfReport', 'Adult Self-Report'], ['APSD', 'APSD'], ['ARI', 'ARI '], ['AutismScreener', 'Autism Screener '], ['Beery', 'Beery VMI'], ['BRIEFAdultSelf', 'BRIEF Adult Self'], ['BRIEFChildrenSelf', 'BRIEF Children Self'], ['BRIEFParent', 'BRIEF Parent'], ['BRIEFTeacher', 'BRIEF Teacher'], ['CAADID', 'CAADID'], ['CAARS', 'CAARS Self Report '], ['CBCL', 'CBCL'], ['ConnersParent', 'Conners Parent Rev '], ['ConnersSelf', 'Conners Self '], ['OldConnersTeacher', 'Conners Teacher '], ['ConnersTeacher', 'Conners Teacher Rev '], ['DCDQ', 'DCDQ '], ['DICA', 'DICA'], ['FES', 'Family Enviro Scale '], ['Fluency', 'Fluency (FAS + Animals)'], ['MotorBattery11to16', 'Movement ABC 11-16yr'], ['MotorBattery3to6', 'Movement ABC 3-6yr'], ['MotorBattery7to10', 'Movement ABC 7-10yr'], ['NVInterview', 'NV Interview'], ['PreliminaryParentReport', 'Prelim. Parent Rpt '], ['SCID', 'SCID'], ['SES', 'SES'], ['SideEffectsRatingScale', 'Side effects rating scale'], ['SNAP', 'SNAP-IV'], ['SRS', 'SRS'], ['SymptomCount', 'Symptom Count'], ['Trails', 'Trails'], ['TRF', 'TRF'], ['WASI1', 'WASI-I'], ['WASI2', 'WASI-II'], ['Wenders', 'Wenders '], ['WISC', 'WISC'], ['WJ', 'Woodcock-Johnson'], ['WPPSI3', 'WPPSI-III'], ['WPPSI4', 'WPPSI-IV'], ['WTAR', 'WTAR']]

fid = open(sql_file, 'w')
fid.write('DECLARE @testingDate DATETIME\nSET @testingDate = \'2013-08-30\'\n--- DO NOT CHANGE BELOW HERE ---\n')
for table in tables:
    fid.write('DECLARE @%s TABLE(id VARCHAR(100), res VARCHAR(1))\nINSERT INTO @%s\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'X\'\nFROM [MART_EX_FORM_%s],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_%s].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_%s].[date_collected]=@testingDate\n' % (table[0], table[0], table[1], table[1], table[1]))
fid.write('\nSELECT DISTINCT Subject=[MART_SubjectInformation].[subject_full_name]')
for table in tables:
    fid.write(', %s=[@%s].[res]' % (table[0], table[0]))
fid.write('\nFROM [MART_SubjectInformation]\n')
for table in tables:
    fid.write('\tLEFT JOIN @%s ON [@%s].[id] = [MART_SubjectInformation].[subject_code]\n' % (table[0], table[0]))
fid.write('WHERE [@%s].[res]=\'X\'' % tables[0][0])
for f in range(1, len(tables)):
    fid.write(' OR [@%s].[res]=\'X\'' % tables[f][0])
fid.close()