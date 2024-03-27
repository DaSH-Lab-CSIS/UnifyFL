#!/bin/bash

remote_ips=("10.8.1.154" "10.8.1.48" "10.8.1.44")
local_destination="/home/primus/Documents/DaSHLab/EkatraFL/results"
local_destination=$4

# $1 = sync/async
# $2 = model_id
# $3 = model_name (cifar10/mnist/emnist)

for remote_ip in ${remote_ips[*]};
    do
        dest_folder=$local_destination/$1/$3/$2/$remote_ip
        poetry run python3 scripts/evaluate_models.py $dest_folder "$2-$remote_ip"
    done
