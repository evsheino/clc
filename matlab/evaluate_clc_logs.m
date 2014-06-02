function [output] = evaluate_clc_logs(userN, host, logdir, testPrefix)

usernames = cell(userN, 1);
for i = 1:userN
    usernames{i} = strcat('user', int2str(i), '@', host);
end

conversationN = 1;
for i = 1:2:numel(usernames)
    % Generate variable names
    conversationname = genvarname(strcat('Conversation', int2str(conversationN)));
    lognameone = genvarname(strcat('LogUser', int2str(i)));
    lognametwo = genvarname(strcat('LogUser', int2str(i+1)));
    
    % Import xmpp client log data
    filenameone = strcat(logdir, filesep, usernames(i), '_to_', usernames(i+1), '.log');
    filenametwo = strcat(logdir, filesep, usernames(i+1), '_to_', usernames(i), '.log');
    logdataone = importEjabberdLog(filenameone{1,1}, testPrefix);
    logdatatwo = importEjabberdLog(filenametwo{1,1}, testPrefix);
    
    % Merge client logs
    
    merged = 'test';
    
    % Write to result struct
    eval(['output.' conversationname '.' lognameone '= logdataone;']);
    eval(['output.' conversationname '.' lognametwo '= logdatatwo;']);
    eval(['output.' conversationname '.Merged = merged;']);
    
    conversationN = conversationN + 1;
end

end