#!/bin/bash

remote_user="ekatrafl"
remote_ips=("10.8.1.173" "10.8.1.175" "10.8.1.174")
remote_path="~/EkatraFL/save/$1/$3/$2/*"
# local_destination="/home/primus/Documents/DaSHLab/EkatraFL/results"
local_destination=$4

for remote_ip in ${remote_ips[*]};
    do
        dest_folder=$local_destination/$1/$3/$2/$remote_ip
        mkdir -p $dest_folder
        scp -r -P222 "$remote_user@$remote_ip:$remote_path" $dest_folder
    done
