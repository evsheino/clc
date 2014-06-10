function [] = retrieve_cloud_watch_metrics(file_name, start_time, end_time, instance_name, metric_names)
%UNTITLED10 Summary of this function goes here
%   Detailed explanation goes here

region = 'eu-west-1';
metric_name = metric_names;
period = 60;
statistics = 'Average';
output = 'text';

command = ['"C:\Program Files\Amazon\AWSCLI\aws" --region ' region ' cloudwatch get-metric-statistics --metric-name ' metric_name ' --namespace AWS/EC2 --start-time ' start_time ' --end-time ' end_time ' --period ' int2str(period) ' --statistics ' statistics ' --output ' output '  --dimensions Name=InstanceId,Value=' instance_name ' > ' file_name];

disp(command);
system(command);

end

