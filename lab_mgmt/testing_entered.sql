DECLARE @testingDate DATETIME
SET @testingDate = '2013-08-30'

--- DO NOT CHANGE BELOW HERE ---

DECLARE @ADHD_RATING TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @ADHD_RATING 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_ADHD Rating ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_ADHD Rating ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_ADHD Rating].[date_collected]=@testingDate
DECLARE @SNAP TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @SNAP 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_SNAP-IV ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_SNAP-IV ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_SNAP-IV ].[date_collected]=@testingDate
DECLARE @FES TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @FES 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Family Enviro Scale ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Family Enviro Scale ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Family Enviro Scale ].[date_collected]=@testingDate
DECLARE @CAARS TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @CAARS 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_CAARS Self Report ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_CAARS Self Report ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_CAARS Self Report ].[date_collected]=@testingDate
DECLARE @WENDERS TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @WENDERS 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Wenders ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Wenders ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Wenders ].[date_collected]=@testingDate
DECLARE @OLDCONNERS TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @OLDCONNERS 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Conners Self ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Conners Self ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Conners Self ].[date_collected]=@testingDate
DECLARE @BRIEFA TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @BRIEFA 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_BRIEF Adult Self],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_BRIEF Adult Self].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_BRIEF Adult Self].[date_collected]=@testingDate
DECLARE @ARI TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @ARI 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_ARI ],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_ARI ].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_ARI ].[date_collected]=@testingDate
DECLARE @APSD TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @APSD 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_APSD],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_APSD].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_APSD].[date_collected]=@testingDate
DECLARE @SRS TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @SRS 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_SRS],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_SRS].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_SRS].[date_collected]=@testingDate
DECLARE @ADULTSELF TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @ADULTSELF 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Adult Self-Report],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Adult Self-Report].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Adult Self-Report].[date_collected]=@testingDate
DECLARE @WTAR TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @WTAR 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_WTAR],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_WTAR].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_WTAR].[date_collected]=@testingDate
DECLARE @FLUENCY TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @FLUENCY 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Fluency (FAS + Animals)],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Fluency (FAS + Animals)].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Fluency (FAS + Animals)].[date_collected]=@testingDate
DECLARE @WJ TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @WJ 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Woodcock-Johnson],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Woodcock-Johnson].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Woodcock-Johnson].[date_collected]=@testingDate
DECLARE @Trails TABLE(id VARCHAR(100), res VARCHAR(1))
INSERT INTO @Trails 
SELECT DISTINCT [MART_SubjectInformation].[subject_code], 'X' 
FROM [MART_EX_FORM_Trails],[MART_SubjectInformation] 
WHERE [MART_EX_FORM_Trails].[subject_id]=[MART_SubjectInformation].[subject_id] AND [MART_EX_FORM_Trails].[date_collected]=@testingDate

SELECT DISTINCT Subject=[MART_SubjectInformation].[subject_full_name], WTAR=[@WTAR].[res], Trails=[@Trails].[res], SNAP=[@SNAP].[res], ADHD_RATING=[@ADHD_RATING].[res], FES=[@FES].[res], WJ=[@WJ].[res], Fluency=[@Fluency].[res], AdultSelf=[@ADULTSELF].[res], SRS=[@SRS].[res], APSD=[@APSD].[res], ARI=[@ARI].[res], BriefAdult=[@BRIEFA].[res], OldConners=[@OLDCONNERS].[res], Wenders=[@WENDERS].[res], CAARS=[@CAARS].[res]
FROM [MART_SubjectInformation]
   LEFT JOIN @WTAR ON [@WTAR].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @Trails ON [@Trails].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @SNAP ON [@SNAP].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @ADHD_RATING ON [@ADHD_RATING].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @FES ON [@FES].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @WJ ON [@WJ].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @Fluency ON [@Fluency].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @ADULTSELF ON [@ADULTSELF].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @SRS ON [@SRS].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @APSD ON [@APSD].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @ARI ON [@ARI].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @BRIEFA ON [@BRIEFA].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @OLDCONNERS ON [@OLDCONNERS].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @WENDERS ON [@WENDERS].[id] = [MART_SubjectInformation].[subject_code]
   LEFT JOIN @CAARS ON [@CAARS].[id] = [MART_SubjectInformation].[subject_code]
WHERE [@WTAR].[res]='X' OR [@Trails].[res]='X' OR [@SNAP].[res]='X' OR [@ADHD_RATING].[res]='X' OR [@FES].[res]='X' OR [@WJ].[res]='X' OR [@Fluency].[res]='X' OR [@ADULTSELF].[res]='X' OR [@SRS].[res]='X' OR [@APSD].[res]='X' OR [@ARI].[res]='X' OR [@BRIEFA].[res]='X' OR [@OLDCONNERS].[res]='X' OR [@WENDERS].[res]='X' OR [@CAARS].[res]='X'

                