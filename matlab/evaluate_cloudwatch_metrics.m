function [ output ] = evaluate_cloudwatch_metrics(instance_names, start_date, end_date)
%evaluate_cloudwatch_metrics Retrieves CloudWatch metric files for the
%specified EC2 instance ids.
%   Date in format: 2014-06-04T00:00:00

stats_dir = 'CloudWatchMetrics';

for i = 1:numel(instance_names)
    filename = strcat(stats_dir, filesep, 'CPUUtilization_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'CPUUtilization');
    stats.(genvarname(instance_names{i})).CPUUtilization = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'NetworkIn_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'NetworkIn');
    stats.(genvarname(instance_names{i})).NetworkIn = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'NetworkOut_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'NetworkOut');
    stats.(genvarname(instance_names{i})).NetworkOut = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'StatusCheckFailed_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'StatusCheckFailed');
    stats.(genvarname(instance_names{i})).StatusCheckFailed = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'DiskReadOps_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'DiskReadOps');
    stats.(genvarname(instance_names{i})).DiskReadOps = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'DiskWriteOps_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'DiskWriteOps');
    stats.(genvarname(instance_names{i})).DiskWriteOps = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'DiskWriteBytes_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'DiskWriteBytes');
    stats.(genvarname(instance_names{i})).DiskWriteBytes = import_cloudwatch_metric(filename);
    
    filename = strcat(stats_dir, filesep, 'DiskReadBytes_', instance_names{i}, '.csv');
    retrieve_cloud_watch_metrics(filename, start_date, end_date, instance_names{i}, 'DiskReadBytes');
    stats.(genvarname(instance_names{i})).DiskReadBytes = import_cloudwatch_metric(filename);
end

output = stats;

end

