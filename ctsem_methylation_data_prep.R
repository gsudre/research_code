# Converts a long-form dataset to a wide and wider (developmental) form dataset for use in ctsem
# Specifically, this script converts the methylation data into a 2-timepoint developmental time wider-form dataset

#When running on BW
#FILEPATH<-'/data/jungbt/ctsem_longitudinal_methylation/ctsem_processing/'
#When running locally
Sys.setenv(KMP_DUPLICATE_LIB_OK=TRUE)
FILEPATH<-'/Volumes/data/ctsem_longitudinal_methylation/ctsem_processing/'

#Load libraries and set filepaths
Sys.setenv(OMP_NUM_THREADS=parallel::detectCores())
library(ctsem)
library(parallel)
setwd(FILEPATH)

#Set time-independent, time-dependent variables, and other columns to extract from the dataset
TIs <- c('Sex','PC1','PC2','PC3','PC4','PC5','PC6','PC7','PC8','PC9','PC10','sample_type','batch')
TDs <- c('qc_bad','CD4T','NK','Bcell','Mono','Gran')
demo_cols <- c('id','time','SXIN','SXHI','SXTOT',TIs,TDs,'array.id')

#Load Long form
demo_df_path <- '../gf_long_ctsem_2obs_08072018.csv'
demo_df <- read.csv(demo_df_path, T)
demo_df <- demo_df[order(demo_df$array.id),] #alphabetize based on array.id (for agreement with probes)
#Rename a few columns so that ctsem doesn't get snippy
demo_df$time <- demo_df$ageACQ
demo_df$id <- demo_df$PersonID
demo_df$qc_bad <- demo_df$qc.bad
#Exclude columns of non-interest
demo_df <- demo_df[,demo_cols]

#Load methylation data
methylation_df <- readRDS('../m_info.rds')
# remove probes that don't correspond to a datapoint
arrays <- sort(intersect(colnames(methylation_df), demo_df$array.id)) 
methylation_df <- methylation_df[,arrays]
#Transpose the methylation data and append it to the demographic data
complete_df <- cbind(demo_df,t(methylation_df))





#Get probe names
probe_names <- names(complete_df)[(length(demo_cols)+1):dim(complete_df)[2]]
print(head(probe_names))
print(tail(probe_names))

# GS comment, otherwise it wouldn't run
# methylation_df <- t(methylation_df)

load('MNI_STATS.RData')
model <- mni.vertex.statistics(demo_df,'y ~ Sex + sample_type',methylation_df)
# GS comment: sig_df not used anywhere else in the code...
# for (probe in probe_names) {
#   reg <- summary(lm(sprintf('%s ~ Sex + sample_type',probe),data=complete_df))$coefficients[2:3,4]
#   sig_df[c,] <- c(probe,reg[2],reg[3])
#   c = c + 1
# }
save(model,file="mni_vertex_stats_model.RData")
rm(methylation_df)
#rename probe names to manifest names
manifest_names <- sprintf('Y%d',seq(1,length(probe_names)))
names(complete_df)[(length(demo_cols)+1):dim(complete_df)[2]] <- manifest_names

#Create manifest_names -> probe_names key
key_df <- data.frame(matrix(NA,nrow=length(probe_names),ncol=2))
colnames(key_df) <- c('code','key')
key_df$code <- manifest_names
key_df$key <- probe_names
write.csv(key_df,'methylation_long_form_ctsem_coded.csv',row.names=FALSE)

#Z-scale all continuous variables
#scaled_cols <- c(sprintf('PC%d',seq(1,10)),'CD4T','NK','Bcell','Mono','Gran',manifest_names)
#scale_parallel <- function(column) {
#  return(scale(complete_df[,column], center=TRUE, scale=TRUE))
#}
#This is taking to long, maybe parallelize the scaling?
#system.time({
#  for (col in scaled_cols){
#    print(col)
#    complete_df[,col] <- scale(complete_df[,col], center=TRUE, scale=TRUE)
#  }
#})
#system.time({
#  cores=detectCores()
#  results <- mclapply(scaled_cols, scale_parallel,mc.cores =cores)
#})
#Or maybe just use scale to scale all columns at once? (Nope R can't handle that)
#system.time({
#  complete_df[,scaled_cols] <- scale(complete_df[,scaled_cols], center=TRUE, scale=TRUE)
#})
# Ignore all above. Turns out it doesn't need to be scaled......

#Z-scale the symptom scores
for (col in c('SXHI','SXIN','SXTOT')){
  print(col)
  complete_df[,col] <- scale(complete_df[,col], center=TRUE, scale=TRUE)
}


#1 Save long-form dataset
#save(complete_df, file = 'DATA_LONG_methylation_2obs_developmental_time.RData.gz',compress='gzip')

#Use all cores to save the CSVs for each individual swarms
save_parallel <- function(seq) {
  #Function for chopping the probes into distinct bits for swarming
  #Get info
  cur_probe <- cur_probe_list[seq]
  last_probe <- last_probe_list[seq]
  count <- count_list[seq]
  file_count <- file_count_list[seq]
  
  sprintf("Working on Y%d ... Y%d",cur_probe,last_probe)
  #Set limits on which probes ot analyze
  cur_probe <- cur_probe + (probe_start-1)
  last_probe <- last_probe + (probe_start-1)
  #Subset df
  data_long_subset <- complete_df[,c(seq(1,(probe_start-1)),seq(cur_probe,last_probe))]
  
  manifest_names <- c('SXIN','SXHI',names(complete_df[,seq(cur_probe,last_probe)]))
  
  #Convert long_form -> wide_form
  wide_resid_motion<-ctLongToWide(datalong=data_long_subset, id="id", time="time", manifestNames=manifest_names, 
                                  TIpredNames=TIs,TDpredNames=TDs) 
  #save(wide_resid_motion, file = sprintf("DATA_wide_methylation_2obs_developmental_time_%d_%d.RData.gz",count,file_count),compress='gzip')
  
  #Convert wide form -> wider_form
  wider_resid_motion<-ctIntervalise(datawide=wide_resid_motion, Tpoints=2, 
                                    n.manifest= length(manifest_names), manifestNames=manifest_names,
                                    n.TIpred  = length(TIs),            TIpredNames=TIs, 
                                    n.TDpred  = length(TDs),            TDpredNames=TDs,
                                    individualRelativeTime=FALSE)
  #write.csv(wider_resid_motion, 'DATA_wider_methylation_2obs_developmental_time.csv')
  sprintf("Saving DATA_wider_methylation_2obs_developmental_time_%d_%d.RData.gz",count,file_count)
  save(wider_resid_motion, file = sprintf("data/DATA_wider_methylation_2obs_developmental_time_%d_%d.RData.gz",count,file_count),compress='gzip')
}


ncond=length(probe_names);
bundle=64; #number of probes per swarm command
probe_start=26 #column where probes begin
#various counters:
cur_probe=1;
count=1
file_count=1
#empty lists for storage:
cur_probe_list=c()
last_probe_list=c()
count_list=c()
file_count_list=c()

#Generate lists for parallelization

# GS comment: need to create directories first
dir.create('swarms_reduced_cov')
dir.create('data')

while (cur_probe < ncond){
  last_probe <- min(cur_probe+bundle-1,ncond) 
  #Only add the entry if the file doesn't exist (saves time)
  if ( ! file.exists(sprintf("data/DATA_wider_methylation_2obs_developmental_time_%d_%d.RData.gz",count,file_count))) {
    cur_probe_list=c(cur_probe_list,cur_probe)
    last_probe_list=c(last_probe_list,last_probe)
    count_list=c(count_list,count)
    file_count_list=c(file_count_list,file_count)
  }
  #Write out swarm files for each analysis
  for (sx in c("SXIN", "SXHI")) {
    fileConn<-file(sprintf("swarms_reduced_cov/DATA_wider_methylation_2obs_developmental_time_%s_%d.swarm",sx,file_count),open="a")
    writeLines(c(sprintf("bash %s/run_ctsem_probe_parallel_net_reduced_cov.sh %s/data/DATA_wider_methylation_2obs_developmental_time_%d_%d.RData.gz %s %d %d %s/methylation_models_reduced_cov/",FILEPATH,FILEPATH,count,file_count,sx,cur_probe,last_probe,FILEPATH)), fileConn)
    close(fileConn)
  }
  #Swarm files can only contain 1000 commands before they start looping back, so create a new file every 1000 commands
  #Actually it complained about 1000, let's try 200
  if (count == 200){
    file_count=file_count+1
    count=1
  }  else {
    count = count + 1
  }
  cur_probe <- last_probe+1
}
#Process the datasets on all available cores (to save time)
#cores=detectCores()
cores <- 10
print(cores)

mclapply(seq(1,length(cur_probe_list)), save_parallel,mc.cores = cores)

#DONE!!!!!
