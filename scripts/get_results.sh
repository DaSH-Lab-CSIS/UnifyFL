#!/bin/bash

remote_user="user"
remote_ips=("10.8.1.25" "10.8.1.48" "10.8.1.44")
remote_path="~/EkatraFL/save/$1/cifar10/$2"
local_destination="/home/primus"

# read -s -p "Enter password for $remote_user@$remote_ip: " password
for remote_ip in ${remote_ips[*]};
    do
        echo "user123" | scp -r -P222 "$remote_user@$remote_ip:$remote_path" "$local_destination"
    done

