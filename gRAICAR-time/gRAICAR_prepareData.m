function obj = gRAICAR_prepareData (obj, sub)

if nargin < 2
	sub = 1:obj.setup.subNum;
end

% dwt on mask
szmsk = size (obj.result.mask);
%dsmpMsk = my_dwt3D (double(obj.result.mask));
%dsmpMsk (dsmpMsk < 0) = 0;
dsmpMsk = obj.result.mask;

% checking the prepared data
for sb = sub
    fprintf ('subject %d: checking data\n', sb);
	trTab = find (obj.result.trialTab(:, 2) == sb);
    trials = length (trTab);
        
    for tr = 1:trials;			
        fn = sprintf ('%s/bin_%s%d.mat', cell2mat (obj.setup.subDir(sb)), obj.setup.ICAprefix, tr);
        if exist (fn, 'file')  % if the ICA maps are already binned
            fprintf ('file %s exist, will not overwrite it\n', fn);
            try % try to load the binned file
               load (fn);
               obj.result.trialTab(trTab(tr), 3) = size (comp, 1);
            catch exception
                error ('!!!!!! failed to load file %s\n',  fn);
            end
            
            % save nii header info
            if trials == 1 % deal with format difference
                fn = sprintf ('%s/%s', cell2mat (obj.setup.subDir(sb)), obj.setup.ICAprefix);
            elseif trials > 1
                fn = sprintf ('%s%d/%s', cell2mat (obj.setup.subDir(sb)), tr, obj.setup.ICAprefix);
            end
            if sb == 1 && tr == 1
                obj.setup.niihdr = load_nifti(fn, 'hdr_only');
            end
        else    % if the ICA maps are not binned
            fprintf ('transforming trial %d of subject %d\n', tr, sb);
            tic,
            ext = getExtension (obj.setup.ICAprefix);
            if strcmp (ext, '.mat') % if the ICA file is in .mat format
                if trials == 1
                    fn = sprintf ('%s%s.mat', cell2mat (obj.setup.subDir(sb)), obj.setup.ICAprefix);
                elseif trials > 1
                    fn = sprintf ('%s%s%d.mat', cell2mat (obj.setup.subDir(sb)), obj.setup.ICAprefix, tr);
                end
                try
                    load (fn);
                catch exception2
                    error ('failed to load file %s\n',  fn);
                end
            else
                % GS: icasig needs to be comp x time
                fn = sprintf('%s/melodic_mix',cell2mat (obj.setup.subDir(sb)))
                icasig = dlmread(fn,' ');
                icasig = icasig';
%                 if trials == 1
%                     fn = sprintf ('%s/%s', cell2mat (obj.setup.subDir(sb)), obj.setup.ICAprefix);
%                 elseif trials > 1
%                     fn = sprintf ('%s%d/%s', cell2mat (obj.setup.subDir(sb)), tr, obj.setup.ICAprefix);
%                 end
%                 hdr = load_nifti(fn);
%                 nii = hdr.vol;
%                 dim = hdr.dim([2:5]);
%                 hdr.vol = [];
% 				% save nii header info
% 				if sb == 1 && tr == 1
% 					obj.setup.niihdr = hdr;
% 				end
%                 icasig = reshape (nii, dim(1)*dim(2)*dim(3), dim(4));
%                 icasig (obj.result.mask==0, :) = [];
%                 icasig = icasig';               
            end
   
			%%%%%%%%% filter data %%%%%%%
            if ~isempty (obj.setup.candidates)
                select = obj.setup.candidates{tr, sb};
                comp = icasig(select, :);
			else
				comp = icasig;
            end
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            
            clear icasig A W nii hdr;

            % bin the data
            [numComp, numVx] = size (comp);
            ncellx=ceil(numVx^(1/3));
            rm_me = [];
            for cp = 1:numComp
                comp(cp, :) = NMI_binData (comp(cp, :), numVx, ncellx);
                % GS remove components that are constant over time (NaN after
                % binarizing)
                if sum(isnan(comp(cp,:)))==numVx
                    rm_me = [rm_me cp];
                end
            end
            comp(rm_me,:) = [];
            
            fn = sprintf ('%s/bin_%s%d.mat', cell2mat (obj.setup.subDir(sb)), ...
            obj.setup.ICAprefix, tr);
            save (fn, 'comp');
			obj.result.trialTab(trTab(tr), 3) = size (comp, 1);
			fprintf ('num of IC = %d\n',size (comp, 1));
            toc,
       end
    end
end
inFn = sprintf ('%s_configFile.mat',obj.setup.outPrefix);
save (inFn, 'obj');
fprintf ('subject %d: done\n', sb);
