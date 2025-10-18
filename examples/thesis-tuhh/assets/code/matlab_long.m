        fullfilepath = mfilename('fullpath');
        [filepath, filename, ~] = fileparts(fullfilepath);
    
        %% Begin Dialogue
        %{
        Extract Data from user-specified input. Can be either a File that is run
        (an *.m-file), variables in the Base Workspace or existing data from a
        previous run (a *.MAT-file). All variables are expected to be in Table
        format, which is the data type best suited for this work. Therefore, we
        force it. No funny business with dynamically named variables or naked
        matrices allowed.
        %}
        pass_data = questdlg({'Would you like to pass existing machine data?', ...
            'Its data would be used to compute your request.', ...
            ['Regardless, note that data is expected to be in ',...
            'Tables named ''', dflt.comp, ''' and ''', dflt.turb, '''.'], '',...
            'If you choose no, existing values are used.'}, ...
            'Machine Data Prompt', btnFF, btnWS, btnNo, btnFF);
    
        switch pass_data
            case btnFF
                prompt = {'File name containing the Tables:', ...
                    'Compressor Table name in that file:',...
                    'Turbine Table name in that file:'};
                title = 'Machine Data Input';
                dims = [1 50];
                definput = {dflt.filename.data, dflt.comp, dflt.turb};
                machine_data_file = inputdlg(prompt, title, dims, definput);
                if isempty(machine_data_file)
                    fprintf('[%s] You left the dialogue and function.\n',...
                        datestr(now));
                    return
                end
                run(machine_data_file{1});%spills file contents into funcWS
            case btnWS
                prompt = {'Base Workspace Compressor Table name:',...
                        'Base Workspace Turbine Table name:'};
                title = 'Machine Data Input';
                dims = [1 50];
                definput = {dflt.comp, dflt.turb};
                machine_data_ws = inputdlg(prompt, title, dims, definput);
                if isempty(machine_data_ws)
                    fprintf('[%s] You left the dialogue and function.\n',...
                        datestr(now));
                    return
                end
            case btnNo
                boxNo = msgbox(['Looking for stats in ''', dflt.filename.stats, ...
                    '''.'], 'Using Existing Data', 'help');
                waitfor(boxNo);
                try
                    stats = load(dflt.filename.stats);
                    stats = stats.stats;
                catch ME
                    switch ME.identifier
                        case 'MATLAB:load:couldNotReadFile'
                            warning(['File ''', dflt.filename.stats, ''' not ',...
                                'found in search path. Make sure it has been ',...
                                'generated in a previous run or created ',...
                                'manually. Resorting to hard-coded data ',...
                                'for now.']);
                                a_b = 200.89;
                                x_c = 0.0012;
                                f_g = 10.0;
                        otherwise
                            rethrow(ME);
                    end
                end
            case ''
                fprintf('[%s] You left the dialogue and function.\n',datestr(now));
                return
            otherwise%Only gets here if buttons are misconfigured
                error('This option is not coded, should not get here.');
        end