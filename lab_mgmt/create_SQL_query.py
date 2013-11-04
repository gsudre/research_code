# Script that makes it easier to create the annoyingly long SQL query to create reporting table

# output file
sql_file = '/Users/sudregp/tmp/test_report.sql'
adult = False
# list of lists. Each list contains a tuple that represents the variable names/column title, and the specific name of each form in the Labmatrix database

# NEED TO ADD NOTES, 

# all tables
tables = [['ADHDRating', 'ADHD Rating '], ['AdultSelfReport', 'Adult Self-Report'], ['APSD', 'APSD'], ['ARI', 'ARI '], ['AutismScreener', 'Autism Screener '], ['Beery', 'Beery VMI'], ['BRIEFAdultSelf', 'BRIEF Adult Self'], ['BRIEFChildrenSelf', 'BRIEF Children Self'], ['BRIEFParent', 'BRIEF Parent'], ['BRIEFTeacher', 'BRIEF Teacher'], ['CAADID', 'CAADID'], ['CAARS', 'CAARS Self Report '], ['CBCL', 'CBCL'], ['ConnersParent', 'Conners Parent Rev '], ['ConnersSelf', 'Conners Self '], ['OldConnersTeacher', 'Conners Teacher '], ['ConnersTeacher', 'Conners Teacher Rev '], ['DCDQ', 'DCDQ '], ['DICA', 'DICA'], ['FES', 'Family Enviro Scale '], ['Fluency', 'Fluency (FAS + Animals)'], ['MotorBattery11to16', 'Movement ABC 11-16yr'], ['MotorBattery3to6', 'Movement ABC 3-6yr'], ['MotorBattery7to10', 'Movement ABC 7-10yr'], ['NVInterview', 'NV Interview'], ['PreliminaryParentReport', 'Prelim. Parent Rpt '], ['SCID', 'SCID'], ['SES', 'SES'], ['SideEffectsRatingScale', 'Side effects rating scale'], ['SNAP', 'SNAP-IV'], ['SRS', 'SRS'], ['SymptomCount', 'Symptom Count'], ['Trails', 'Trails'], ['TRF', 'TRF'], ['WASI1', 'WASI-I'], ['WASI2', 'WASI-II'], ['Wenders', 'Wenders '], ['WISC', 'WISC'], ['WJ', 'Woodcock-Johnson'], ['WPPSI3', 'WPPSI-III'], ['WPPSI4', 'WPPSI-IV'], ['WTAR', 'WTAR']]

if adult:
    # adult-only tables
    tables = [['CAADID', 'CAADID'], ['SCID', 'SCID'], ['NVInterview', 'NV Interview'], ['SES', 'SES'], ['WTAR', 'WTAR'], ['Fluency', 'Fluency (FAS + Animals)'], ['WJ', 'Woodcock-Johnson'], ['Trails', 'Trails'], ['WISC', 'WISC'], ['ADHDRating', 'ADHD Rating '], ['FES', 'Family Enviro Scale '], ['CAARS', 'CAARS Self Report '], ['Wenders', 'Wenders '], ['BRIEFAdultSelf', 'BRIEF Adult Self'], ['APSD', 'APSD'], ['SRS', 'SRS'], ['AdultSelfReport', 'Adult Self-Report'], ['SideEffectsRatingScale', 'Side effects rating scale']]
else:
    # child-baseline tables
    tables = [['DICA', 'DICA'], ['NVInterview', 'NV Interview'], ['SES', 'SES'], ['WJ', 'Woodcock-Johnson'], ['MotorBattery11to16', 'Movement ABC 11-16yr'], ['MotorBattery3to6', 'Movement ABC 3-6yr'], ['MotorBattery7to10', 'Movement ABC 7-10yr'], ['Beery', 'Beery VMI'], ['WASI1', 'WASI-I'], ['WASI2', 'WASI-II'], ['WISC', 'WISC'], ['WPPSI3', 'WPPSI-III'], ['WPPSI4', 'WPPSI-IV'], ['BRIEFChildrenSelf', 'BRIEF Children Self'], ['BRIEFParent', 'BRIEF Parent'], ['BRIEFTeacher', 'BRIEF Teacher'], ['ConnersParent', 'Conners Parent Rev '], ['PreliminaryParentReport', 'Prelim. Parent Rpt '], ['ConnersTeacher', 'Conners Teacher Rev '], ['OldConnersTeacher', 'Conners Teacher '], ['CAARS', 'CAARS Self Report '], ['DCDQ', 'DCDQ '], ['CBCL', 'CBCL'], ['TRF', 'TRF'], ['APSD', 'APSD'], ['SRS', 'SRS'], ['Wenders', 'Wenders '], ['FES', 'Family Enviro Scale '], ['ADHDRating', 'ADHD Rating '], ['SideEffectsRatingScale', 'Side effects rating scale']]

fid = open(sql_file, 'w')
fid.write('DECLARE @testingDate DATETIME\nSET @testingDate = \'2013-08-30\'\n--- DO NOT CHANGE BELOW HERE ---\n')

# extra bit about specimen
fid.write('\nDECLARE @Specimen TABLE(id VARCHAR(100), res VARCHAR(20))\nINSERT INTO @Specimen\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'Saliva\'\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Visit].[date_collected]=@testingDate\n\tAND [MART_EX_FORM_Visit].[Saliva]>0')
fid.write('\nINSERT INTO @Specimen\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'Blood\'\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Visit].[date_collected]=@testingDate\n\tAND [MART_EX_FORM_Visit].[Blood]=\'Yes\'')
fid.write('\nINSERT INTO @Specimen\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'BloodAndSaliva\'\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Visit].[date_collected]=@testingDate\n\tAND [MART_EX_FORM_Visit].[Blood]=\'Yes\' AND [MART_EX_FORM_Visit].[Saliva]>0')

# and about visit note
fid.write('\nDECLARE @Note TABLE(id VARCHAR(100), res VARCHAR(255))\nINSERT INTO @Note\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_Visit].[Note]\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Visit].[date_collected]=@testingDate')

# ARI and SNAP specific tables
fid.write('\nDECLARE @SNAPon TABLE(id VARCHAR(100), res VARCHAR(1))\nINSERT INTO @SNAPon\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'X\'\nFROM [MART_EX_FORM_SNAP-IV],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_SNAP-IV].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_SNAP-IV].[date_collected]=@testingDate AND [MART_EX_FORM_SNAP-IV].[Meds] = \'Yes\'')
fid.write('\nDECLARE @SNAPoff TABLE(id VARCHAR(100), res VARCHAR(1))\nINSERT INTO @SNAPoff\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'X\'\nFROM [MART_EX_FORM_SNAP-IV],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_SNAP-IV].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_SNAP-IV].[date_collected]=@testingDate AND [MART_EX_FORM_SNAP-IV].[Meds] = \'No\'')
fid.write('\nDECLARE @ARIself TABLE(id VARCHAR(100), res VARCHAR(1))\nINSERT INTO @ARIself\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'X\'\nFROM [MART_EX_FORM_ARI],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_ARI].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_ARI].[date_collected]=@testingDate AND [MART_EX_FORM_ARI].[000_ARI_Form_type] = \'S\'')
if not adult:
    fid.write('\nDECLARE @ARIparent TABLE(id VARCHAR(100), res VARCHAR(1))\nINSERT INTO @ARIparent\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'X\'\nFROM [MART_EX_FORM_ARI],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_ARI].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_ARI].[date_collected]=@testingDate AND [MART_EX_FORM_ARI].[000_ARI_Form_type] = \'P\'')

# creating a variable for each remaining table
for table in tables:
    fid.write('\nDECLARE @%s TABLE(id VARCHAR(100), res VARCHAR(1))\nINSERT INTO @%s\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], \'X\'\nFROM [MART_EX_FORM_%s],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_%s].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_%s].[date_collected]=@testingDate\n' % (table[0], table[0], table[1], table[1], table[1]))

# column headers
fid.write('\nSELECT DISTINCT Subject=[MART_SubjectInformation].[subject_full_name]')
for table in tables:
    fid.write(', %s=[@%s].[res]' % (table[0], table[0]))
fid.write(', SNAPon=[@SNAPon].[res], SNAPoff=[@SNAPoff].[res], ARIself=[@ARIself].[res]')
if not adult:
    fid.write(', ARIparent=[@ARIparent].[res]')
fid.write(', Specimen=[@Specimen].[res], Note=[@Note].[res]')

# joining tables
fid.write('\nFROM [MART_SubjectInformation]\n')
for table in tables:
    fid.write('\tLEFT JOIN @%s ON [@%s].[id] = [MART_SubjectInformation].[subject_code]\n' % (table[0], table[0]))

# add special columns as well
fid.write('\tLEFT JOIN @SNAPon ON [@SNAPon].[id] = [MART_SubjectInformation].[subject_code]\n')
fid.write('\tLEFT JOIN @SNAPoff ON [@SNAPoff].[id] = [MART_SubjectInformation].[subject_code]\n')
fid.write('\tLEFT JOIN @ARIself ON [@ARIself].[id] = [MART_SubjectInformation].[subject_code]\n')
if not adult:
    fid.write('\tLEFT JOIN @ARIparent ON [@ARIparent].[id] = [MART_SubjectInformation].[subject_code]\n')
fid.write('\tLEFT JOIN @Specimen ON [@Specimen].[id] = [MART_SubjectInformation].[subject_code]\n')
fid.write('\tLEFT JOIN @Note ON [@Note].[id] = [MART_SubjectInformation].[subject_code]\n')

# I might need to add the special cases here in the future... if they are ever the only positive in the row
fid.write('WHERE [@%s].[res]=\'X\'' % tables[0][0])
for f in range(1, len(tables)):
    fid.write(' OR [@%s].[res]=\'X\'' % tables[f][0])
fid.close()