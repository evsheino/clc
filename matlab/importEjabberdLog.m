function [ output_args ] = importEjabberdLog(file, testprefix)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here

% Open log file
fid = fopen(file,'r');

% Prepare date format
dateFormatLog = 'yyyy-mm-dd HH:MM:SS,FFF';
dateFormatXmpp = 'yyyy-mm-dd HH:MM:SS';

% Retrieve line numbers for approximating memory allocation
% Get file size
fseek(fid, 0, 'eof');
fileSize = ftell(fid);
frewind(fid);
% Read the whole file
data = fread(fid, fileSize, 'uint8');
% Count number of line-feeds and increase by one
numLines = sum(data == 10) + 1;
frewind(fid);

% Prepare data fields
jid = '';
DateTime = zeros(numLines, 1);
Type = zeros(numLines, 1);
Offline = zeros(numLines, 1);
From = cell(numLines, 1);
To = cell(numLines, 1);
Message = cell(numLines, 1);

% Retrieve first line
tline = fgetl(fid);

i = 1;
while ischar(tline)
    if strfind(tline, 'DEBUG') == 1
        if size(tline) < 49
            tline = fgetl(fid);
            continue;
        end
        type = tline(36:49);
        if strcmp('SEND: <message', type) || strcmp('RECV: <message', type)
            
            % Parse and store message
            body = tline(42:end);
            xml = xml_parseany(body);
            
            % Message body
            if isfield(xml, 'body')
                msg = xml.body{1, 1}.CONTENT;
                if strfind(msg, strcat(testprefix, '/')) == 1
                    Message{i} = xml.body{1, 1}.CONTENT;
                else
                    tline = fgetl(fid);
                    continue;
                end
            else
                tline = fgetl(fid);
                continue;
            end
            
            % Sender
            if isfield(xml.ATTRIBUTE, 'from')
                From{i} = xml.ATTRIBUTE.from;
            else
                From{i} = jid;
            end
            
            % Check if its an offline message
            if isfield(xml, 'delay')
                datestring = strrep(xml.delay{1, 1}.ATTRIBUTE.stamp, 'T', ' ');
                datestring = strrep(datestring, 'Z', '');
                Offline(i) = datenum(datestring, dateFormatXmpp);
            else
                Offline(i) = -1;
            end
            
            % Receiver
            To{i} = xml.ATTRIBUTE.to;
            
            % Store datetime
            time = tline(10:32);
            DateTime(i) = datenum(time, dateFormatLog);
            
            % Store type
            if strcmp('SEND: <message', type)
                Type(i) = 1;
            elseif strcmp('RECV: <message', type)
                Type(i) = 2;
            end
            
            i = i + 1;
        end
    elseif strfind(tline, 'INFO') == 1
        if ~isempty(strfind(tline, 'JID set to:'))
            jid = tline(48:end);
        end
    end
    tline = fgetl(fid);
end

% Create output dataset
tmp = dataset(DateTime, Type, Offline, From, To, Message);
% Trim dataset to the actual number of rows
output_args = tmp(1:i-1, :);

% Close log file
fclose(fid);
end

