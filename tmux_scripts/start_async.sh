#!/usr/bin/env bash
set -o xtrace
cd ..
python3 tmux_scripts/deploy_contracts.py 1 $1 $2 $3
tmuxinator start async
