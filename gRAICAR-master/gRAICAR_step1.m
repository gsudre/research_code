
function [status, exeption] = gRAICAR_step1(settings)

status = 1;
exeption = [];
try
%%%%%%%%% load user settings %%%%%%%%%%%%%%%
% rootdir: the path of directory in which the entire analysis is runing
rootDir = settings.workdir;

% outdir: the name of directory for the output of gRAICAR (!!!!relative to the rootDir, instead of full path!!!!)
outDir = settings.outDir;

% taskName: name of the analysis task, will be used as the prefix of the configFile that stores information about the analysis.
taskName = settings.taskname;

% pathSbList: path to the subject list file (!!!!relative to the rootDir, instead of full path!!!!)
% the subject list file contains a list (column) of subject names. The data for each subject are under the directory with the listed subject name
pathSbList = settings.pathSbList;

% icaPrefix: name of the Melodic ICA file
icaPrefix = settings.icaPrefix;

% icaDir: path of the ICA directory (!!!!relative to the subject directory, instead of full path!!!!)
icaDir= settings.icaDir;

% maskPath: path of the mask file (!!!!relative to the rootDir, instead of full path!!!!)
maskPath = settings.maskPath;

%%%%%%%%%% end of user settings %%%%%%%%%%%%%%%%%%%

fprintf ('\n-------------------------\n');
fprintf (' setting up gRAICAR \n');
fprintf ('-------------------------\n');

rootDir

pathSbList

% load the subject list
fid = fopen ([rootDir, pathSbList]);
tmp = textscan (fid,'%s');
len = length (tmp{1});
fclose(fid);

sbList = cell(len,1);
fid = fopen ([rootDir, pathSbList], 'r');
for i=1:len
    sbList{i} = fgetl (fid);
end
fclose(fid);

candidates = []; % candiate components
% check if use RAICAR
if settings.useRAICAR == 1
    candidates = gRAICAR_callRAICAR(settings, sbList);
    icaPrefix = sprintf ('%s_aveMap.nii.gz', settings.icaPrefix);
    fn = sprintf ('%s/RAICAR_candiates.mat', settings.outdir);
    save (fn, 'candidates');
%     load(fn);
end

% setup analysis
obj = gRAICAR_setup_singleMelodic (rootDir, sbList, outDir, taskName, icaDir, icaPrefix, maskPath, candidates);

% bin the ICA maps
fprintf ('\n-------------------------\n');
fprintf (' bining IC maps \n');
fprintf ('-------------------------\n');

obj = gRAICAR_prepareData (obj,1:length(sbList));

% prepare for NMI computation
if exist ([rootDir, outDir]) ~= 7
    mkdir ([rootDir, outDir])
end
if exist([rootDir, outDir, '/progress.log']) == 2
    delete([rootDir, outDir, '/progress.log'])
end
if exist([rootDir, outDir, '/distComp.log']) == 2
    delete([rootDir, outDir, '/distComp.log'])
end
dlmwrite ([rootDir, outDir, '/progress.log'], 1, 'precision', '%d');
dlmwrite ([rootDir, outDir, '/distComp.log'], 0, 'precision', '%d');

fprintf ('\n-------------------------\n');
fprintf (' set up finished \n');
fprintf ('-------------------------\n');

catch exeption
    status = 0;
    return
end
