function [output] = evaluate_clc_logs(userN, host, logdir, testPrefix)

usernames = cell(userN, 1);
conversationnames = cell(userN/2, 1);
for i = 1:userN
    usernames{i} = strcat('user', int2str(i), '@', host);
end

conversationN = 1;
for i = 1:2:numel(usernames)
    % Generate variable names
    conversationname = genvarname(strcat('Conversation', int2str(conversationN)));
    conversationnames{conversationN} = conversationname;
    lognameone = genvarname(strcat('LogUser', int2str(i)));
    lognametwo = genvarname(strcat('LogUser', int2str(i+1)));
    
    % Import xmpp client log data
    filenameone = strcat(logdir, filesep, usernames(i), '_to_', usernames(i+1), '.log');
    filenametwo = strcat(logdir, filesep, usernames(i+1), '_to_', usernames(i), '.log');
    logdataone = importEjabberdLog(filenameone{1,1}, testPrefix);
    logdatatwo = importEjabberdLog(filenametwo{1,1}, testPrefix);
    
    % Merge client logs
    % Filter outgoing messages
    outgoingone = logdataone(logdataone.Type==1, :);
    outgoingtwo = logdatatwo(logdatatwo.Type==1, :);
    
    % Prepare new dattaset columns
    rowsNum = size(outgoingone, 1) + size(outgoingtwo, 1);
    DateTimeSent = zeros(rowsNum, 1);
    DateTimeReceived = zeros(rowsNum, 1);
    TimeDifference = zeros(rowsNum, 1);
    Offline = zeros(rowsNum, 1);
    From = cell(rowsNum, 1);
    To = cell(rowsNum, 1);
    Message = cell(rowsNum, 1);
    
    % Loop over client one's sent messages and search for corresponding
    % received in the messages of client two
    for j = 1:size(outgoingone, 1)
        DateTimeSent(j) = outgoingone.DateTime(j, 1);
        Offline(j) = outgoingone.Offline(j, 1);
        From{j} = outgoingone.From{j, 1};
        To{j} = outgoingone.To{j, 1};
        Message{j} = outgoingone.Message{j, 1};
        received = logdatatwo(logdatatwo.Type==2 & strcmp(logdatatwo.From, From{j}) & strcmp(logdatatwo.Message, Message{j}), :);
        if(size(received, 1) == 1)
            DateTimeReceived(j) = received.DateTime(1, 1);
            TimeDifference(j) = etime(datevec(DateTimeReceived(j)), datevec(DateTimeSent(j)));
            %TimeDifference(j) = (DateTimeReceived(j)-DateTimeSent(j)) * datenum(1);
        else
            throw(MException('MergigMessages:Error', 'Finding corresponding message failed.'));
        end
    end
    
    % Loop over client two's sent messages and search for corresponding
    % received in the messages of client one
    for k = 1:size(outgoingtwo, 1)
        DateTimeSent(k+j) = outgoingtwo.DateTime(k, 1);
        Offline(k+j) = outgoingtwo.Offline(k, 1);
        From{k+j} = outgoingtwo.From{k, 1};
        To{k+j} = outgoingtwo.To{k, 1};
        Message{k+j} = outgoingtwo.Message{k, 1};
        received = logdataone(logdataone.Type==2 & strcmp(logdataone.From, From{k+j}) & strcmp(logdataone.Message, Message{k+j}), :);
        if(size(received, 1) == 1)
            DateTimeReceived(k+j) = received.DateTime(1, 1);
            TimeDifference(k+j) = etime(datevec(DateTimeReceived(k+j)), datevec(DateTimeSent(k+j)));
            %TimeDifference(k+j) = (DateTimeReceived(k+j)-DateTimeSent(k+j)) * datenum(1);
        else
            throw(MException('MergigMessages:Error', 'Finding corresponding message failed.'));
        end
    end
    
    %outgoingtwo = logdatatwo(logdatatwo.Type==1, :);
    merged = dataset(DateTimeSent, DateTimeReceived, TimeDifference, From, To, Offline, Message);
    merged = sortrows(merged,'DateTimeSent');
    
    % Write to result struct
    eval(['output.' conversationname '.' lognameone '= logdataone;']);
    eval(['output.' conversationname '.' lognametwo '= logdatatwo;']);
    eval(['output.' conversationname '.Merged = merged;']);
    
    conversationN = conversationN + 1;
end


% Concatenate all merged datasets from all conversations
allmerged = dataset();
for i = 1:numel(conversationnames)
    eval(['allmerged = cat(1, allmerged, output.' conversationnames{i} '.Merged);']);
end
output.TotalMerged = allmerged;

end