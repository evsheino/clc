function [ output_args ] = retrieve_cloud_watch_metrics( start_time, end_time, file_name )
%UNTITLED10 Summary of this function goes here
%   Detailed explanation goes here

region = 'eu-west-1';
metric_name = 'CPUUtilization';
start_time = start_time;
end_time = end_time;
period = 60;
statistics = 'Average';
output = 'text';

command = ['"C:\Program Files\Amazon\AWSCLI\aws" --region ' region ' cloudwatch get-metric-statistics --metric-name ' metric_name ' --namespace AWS/EC2 --start-time ' start_time ' --end-time ' end_time ' --period ' int2str(period) ' --statistics ' statistics ' --output ' output '  --dimensions Name=InstanceId,Value=i-1025c350 > ' file_name];

disp(command);
system(command);

end

