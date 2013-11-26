# Script that makes it easier to create the annoyingly long SQL query to create reporting table

# output file
sql_file = '/Users/sudregp/tmp/test_report.sql'
adult = False
# list of lists. Each list contains a tuple that represents the variable names/column title, and the specific name of each form in the Labmatrix database

# all tables
tables = [['ADHDRating', 'ADHD Rating '], ['AdultSelfReport', 'Adult Self-Report'], ['APSD', 'APSD'], ['ARI', 'ARI '], ['AutismScreener', 'Autism Screener '], ['Beery', 'Beery VMI'], ['BRIEFAdultSelf', 'BRIEF Adult Self'], ['BRIEFChildrenSelf', 'BRIEF Children Self'], ['BRIEFParent', 'BRIEF Parent'], ['BRIEFTeacher', 'BRIEF Teacher'], ['CAADID', 'CAADID'], ['CAARS', 'CAARS Self Report '], ['CBCL', 'CBCL'], ['ConnersParent', 'Conners Parent Rev '], ['ConnersSelf', 'Conners Self '], ['OldConnersTeacher', 'Conners Teacher '], ['ConnersTeacher', 'Conners Teacher Rev '], ['DCDQ', 'DCDQ '], ['DICA', 'DICA'], ['FES', 'Family Enviro Scale '], ['Fluency', 'Fluency (FAS + Animals)'], ['MotorBattery11to16', 'Movement ABC 11-16yr'], ['MotorBattery3to6', 'Movement ABC 3-6yr'], ['MotorBattery7to10', 'Movement ABC 7-10yr'], ['NVInterview', 'NV Interview'], ['PreliminaryParentReport', 'Prelim. Parent Rpt '], ['SCID', 'SCID'], ['SES', 'SES'], ['SideEffectsRatingScale', 'Side effects rating scale'], ['SNAP', 'SNAP-IV'], ['SRS', 'SRS'], ['SymptomCount', 'Symptom Count'], ['Trails', 'Trails'], ['TRF', 'TRF'], ['WASI1', 'WASI-I'], ['WASI2', 'WASI-II'], ['Wenders', 'Wenders '], ['WISC', 'WISC'], ['WJ', 'Woodcock-Johnson'], ['WPPSI3', 'WPPSI-III'], ['WPPSI4', 'WPPSI-IV'], ['WTAR', 'WTAR']]

if adult:
    # adult-only tables
    tables = [['CAADID', 'CAADID'], ['SCID', 'SCID'], ['NVInterview', 'NV Interview'], ['WTAR', 'WTAR'], ['Fluency', 'Fluency (FAS + Animals)'], ['WJ', 'Woodcock-Johnson'], ['Trails', 'Trails'], ['WISC', 'WISC'], ['ADHDRating', 'ADHD Rating '], ['FES', 'Family Enviro Scale '], ['CAARS', 'CAARS Self Report '], ['Wenders', 'Wenders '], ['BRIEFAdultSelf', 'BRIEF Adult Self'], ['APSD', 'APSD'], ['SRS', 'SRS'], ['AdultSelfReport', 'Adult Self-Report'], ['SideEffectsRatingScale', 'Side effects rating scale'], ['Scanned','Scan']]
else:
    # child-baseline tables
    tables = [['DICA', 'DICA'], ['NVInterview', 'NV Interview'], ['WJ', 'Woodcock-Johnson'], ['Beery', 'Beery VMI'], ['WASI1', 'WASI-I'], ['WASI2', 'WASI-II'], ['WISC', 'WISC'], ['WPPSI3', 'WPPSI-III'], ['WPPSI4', 'WPPSI-IV'], ['BRIEFChildrenSelf', 'BRIEF Children Self'], ['BRIEFParent', 'BRIEF Parent'], ['BRIEFTeacher', 'BRIEF Teacher'], ['ConnersParent', 'Conners Parent Rev '], ['ConnersTeacher', 'Conners Teacher Rev '], ['CAARS', 'CAARS Self Report '], ['DCDQ', 'DCDQ '], ['CBCL', 'CBCL'], ['TRF', 'TRF'], ['APSD', 'APSD'], ['SRS', 'SRS'], ['Wenders', 'Wenders '], ['FES', 'Family Enviro Scale '], ['ADHDRating', 'ADHD Rating '], ['SideEffectsRatingScale', 'Side effects rating scale'], ['Scanned','Scan']]

# some tables that are true for all subjects, and that don't use X
subjInfo = [['Race', 'race'], ['Ethnicity', 'ethnicity'], ['DX', 'attribute_1'], ['Gender', 'sex']]

fid = open(sql_file, 'w')
fid.write('DECLARE @familyName VARCHAR(100)\nSET @familyName = \'BEINS\'\n\n--- DO NOT CHANGE BELOW HERE ---\n')

# extra bit about specimen
fid.write('\nDECLARE @Specimen TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(20))\nINSERT INTO @Specimen\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_Visit].[date_collected], \'Saliva\'\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName\n\tAND [MART_EX_FORM_Visit].[Saliva]>0')
fid.write('\nINSERT INTO @Specimen\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_Visit].[date_collected], \'Blood\'\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName\n\tAND [MART_EX_FORM_Visit].[Blood]=\'Yes\'')
fid.write('\nINSERT INTO @Specimen\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_Visit].[date_collected], \'BloodAndSaliva\'\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName\n\tAND [MART_EX_FORM_Visit].[Blood]=\'Yes\' AND [MART_EX_FORM_Visit].[Saliva]>0')

# and about visit note
fid.write('\nDECLARE @Note TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(255))\nINSERT INTO @Note\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_Visit].[date_collected], [MART_EX_FORM_Visit].[Note]\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName')

# computing age variable
fid.write('\nDECLARE @Age TABLE(id VARCHAR(100), vDate DATE, res FLOAT)\nINSERT INTO @Age\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_Visit].[date_collected], \ndateDiff("m", [MART_SubjectInformation].[birth_date], [MART_EX_FORM_Visit].[date_collected]) / 12.0\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName')

# concatenating family variables family
fid.write('\nDECLARE @Family TABLE(id VARCHAR(100), res VARCHAR(100))\nINSERT INTO @Family\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_SubjectInformation].[family_name]+\' (\'+[MART_SubjectInformation].[family_code]+\')\'\nFROM [MART_SubjectInformation], [MART_EX_FORM_Visit]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName')

# # looking for SES
fid.write('\nDECLARE @SES TABLE(id VARCHAR(100), res INTEGER)\nINSERT INTO @SES\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_SES].[Status]\nFROM [MART_SubjectInformation], [MART_EX_FORM_SES]\nWHERE [MART_EX_FORM_SES].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName')

# # adding subject info
for rec in subjInfo:
    fid.write('\nDECLARE @%s TABLE(id VARCHAR(100), res VARCHAR(100))\nINSERT INTO @%s\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_SubjectInformation].[%s]\nFROM [MART_SubjectInformation], [MART_EX_FORM_Visit]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName' % (rec[0],rec[0],rec[1]))

# # ARI, MotorBattery, and SNAP specific tables
fid.write('\nDECLARE @SNAPon TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(1))\nINSERT INTO @SNAPon\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_SNAP-IV].[date_collected], \'X\'\nFROM [MART_EX_FORM_SNAP-IV],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_SNAP-IV].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName AND [MART_EX_FORM_SNAP-IV].[Meds] = \'Yes\'')
fid.write('\nDECLARE @SNAPoff TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(1))\nINSERT INTO @SNAPoff\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_SNAP-IV].[date_collected], \'X\'\nFROM [MART_EX_FORM_SNAP-IV],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_SNAP-IV].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName AND [MART_EX_FORM_SNAP-IV].[Meds] = \'No\'')
fid.write('\nDECLARE @ARIself TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(1))\nINSERT INTO @ARIself\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_ARI].[date_collected], \'X\'\nFROM [MART_EX_FORM_ARI],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_ARI].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName AND [MART_EX_FORM_ARI].[000_ARI_Form_type] = \'S\'')
if not adult:
    fid.write('\nDECLARE @ARIparent TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(1))\nINSERT INTO @ARIparent\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_ARI].[date_collected], \'X\'\nFROM [MART_EX_FORM_ARI],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_ARI].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName AND [MART_EX_FORM_ARI].[000_ARI_Form_type] = \'P\'')
    fid.write('\nDECLARE @MotorBatteryTMP TABLE(id INTEGER, date_collected DATE)\nINSERT INTO @MotorBatteryTMP\nSELECT subject_id, date_collected from [MART_EX_FORM_Movement ABC 3-6yr]\nUNION\nSELECT subject_id, date_collected from [MART_EX_FORM_Movement ABC 7-10yr]\nUNION\nSELECT subject_id, date_collected from [MART_EX_FORM_Movement ABC 11-16yr]\nDECLARE @MotorBattery TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(1))\nINSERT INTO @MotorBattery\nSELECT DISTINCT [@MotorBatteryTMP].[id], [@MotorBatteryTMP].[date_collected], \'X\'\nFROM @MotorBatteryTMP,[MART_SubjectInformation]\nWHERE [@MotorBatteryTMP].[id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName\n')

# adding visits variable so we can store names and dates together
fid.write('DECLARE @Visits TABLE(id VARCHAR(100), full_name VARCHAR(100), vDate DATE)\nINSERT INTO @Visits\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_SubjectInformation].[subject_full_name], [MART_EX_FORM_Visit].[date_collected]\nFROM [MART_EX_FORM_Visit],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_Visit].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName')

# creating a variable for each remaining table
for table in tables:
    fid.write('\nDECLARE @%s TABLE(id VARCHAR(100), vDate DATE, res VARCHAR(1))\nINSERT INTO @%s\nSELECT DISTINCT [MART_SubjectInformation].[subject_code], [MART_EX_FORM_%s].[date_collected], \'X\'\nFROM [MART_EX_FORM_%s],[MART_SubjectInformation]\nWHERE [MART_EX_FORM_%s].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_SubjectInformation].[family_name]=@familyName\n' % (table[0], table[0], table[1], table[1], table[1]))

# column headers
fid.write('\nSELECT DISTINCT Subject=[@Visits].[full_name],Date=[@Visits].[vDate],Age=[@Age].[res],Family=[@Family].[res],SES=[@SES].[res]')
for rec in subjInfo:
    fid.write(', %s=[@%s].[res]' % (rec[0], rec[0]))
for table in tables:
    fid.write(', %s=[@%s].[res]' % (table[0], table[0]))
fid.write(', SNAPon=[@SNAPon].[res], SNAPoff=[@SNAPoff].[res], ARIself=[@ARIself].[res]')
if not adult:
    fid.write(', ARIparent=[@ARIparent].[res]')
    fid.write(', MotorBattery=[@MotorBattery].[res]')
fid.write(', Specimen=[@Specimen].[res], Note=[@Note].[res]')

# joining tables
fid.write('\nFROM @Visits\n')
for table in tables:
    fid.write('\tLEFT JOIN @%s ON [@%s].[id] = [@Visits].[id] AND [@%s].[vDate] = [@Visits].[vDate]\n' % (table[0], table[0], table[0]))
for rec in subjInfo:
    fid.write('\tLEFT JOIN @%s ON [@%s].[id] = [@Visits].[id]\n' % (rec[0], rec[0]))
# add special columns as well
fid.write('\tLEFT JOIN @SNAPon ON [@SNAPon].[id] = [@Visits].[id] AND [@SNAPon].[vDate] = [@Visits].[vDate]\n')
fid.write('\tLEFT JOIN @SNAPoff ON [@SNAPoff].[id] = [@Visits].[id] AND [@SNAPoff].[vDate] = [@Visits].[vDate]\n')
fid.write('\tLEFT JOIN @ARIself ON [@ARIself].[id] = [@Visits].[id] AND [@ARIself].[vDate] = [@Visits].[vDate]\n')
if not adult:
    fid.write('\tLEFT JOIN @ARIparent ON [@ARIparent].[id] = [@Visits].[id] AND [@ARIparent].[vDate] = [@Visits].[vDate]\n')
    fid.write('\tLEFT JOIN @MotorBattery ON [@MotorBattery].[id] = [@Visits].[id] AND [@MotorBattery].[vDate] = [@Visits].[vDate]\n')
fid.write('\tLEFT JOIN @Specimen ON [@Specimen].[id] = [@Visits].[id] AND [@Specimen].[vDate] = [@Visits].[vDate]\n')
fid.write('\tLEFT JOIN @Note ON [@Note].[id] = [@Visits].[id] AND [@Note].[vDate] = [@Visits].[vDate]\n')
fid.write('\tLEFT JOIN @Age ON [@Age].[id] = [@Visits].[id] AND [@Age].[vDate] = [@Visits].[vDate]\n')
fid.write('\tLEFT JOIN @Family ON [@Family].[id] = [@Visits].[id]\n')
fid.write('\tLEFT JOIN @SES ON [@SES].[id] = [@Visits].[id]\n')

# I might need to add the special cases here in the future... if they are ever the only positive in the row
fid.write('WHERE ([@%s].[res]=\'X\'' % tables[0][0])
for f in range(1, len(tables)):
    fid.write(' OR [@%s].[res]=\'X\'' % tables[f][0])
fid.write(' OR LEN([@Specimen].[res])>0)')
if adult:
    fid.write(' AND ([@Age].[res]>=18)')
else:
    fid.write(' AND ([@Age].[res]<18)')
fid.close()