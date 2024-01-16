#!/bin/bash

remote_user="user"
remote_ips=("10.8.1.25" "10.8.1.48" "10.8.1.44")
remote_path="~/EkatraFL/save/$1/cifar10/$2/*"
local_destination="/home/primus/Documents/DaSHLab/EkatraFL/results"

for remote_ip in ${remote_ips[*]};
    do
        dest_folder=$local_destination/$1/cifar10/$2/$remote_ip
        mkdir -p $dest_folder
        scp -r -P222 "$remote_user@$remote_ip:$remote_path" $dest_folder
        python3 evaluate_models.py $dest_folder "$2-$remote_ip"
    done
