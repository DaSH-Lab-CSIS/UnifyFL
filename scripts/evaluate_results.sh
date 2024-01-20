#!/bin/bash

remote_ips=("10.8.1.25" "10.8.1.48" "10.8.1.44")
local_destination="/home/primus/Documents/DaSHLab/EkatraFL/results"

for remote_ip in ${remote_ips[*]};
    do
        dest_folder=$local_destination/$1/cifar10/$2/$remote_ip
        poetry run python3 scripts/evaluate_models.py $dest_folder "$2-$remote_ip"
    done