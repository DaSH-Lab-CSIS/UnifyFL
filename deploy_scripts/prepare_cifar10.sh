#!/usr/bin/env bash
set -euo pipefail

# ========================
# CIFAR10 Data Preparation
# ========================

NUM_CLIENTS=12
DATA_DIR="data/cifar10_new"

echo ">>> Preparing CIFAR10 dataset for $NUM_CLIENTS clients..."

# Ensure Poetry environment is activated
if ! command -v poetry &> /dev/null; then
    echo ">>> Poetry not found. Please run setup_unifyfl.sh first."
    exit 1
fi

# Step 1: Download CIFAR10 dataset
echo ">>> Downloading CIFAR10 dataset..."
poetry run python scripts/download_ds.py --dataset cifar10 

# Step 2: Split dataset into non-IID partitions
echo ">>> Generating non-IID splits for $NUM_CLIENTS clients..."
poetry run python scripts/generate_niid_dirichlet.py \
    --dataset data/cifar10 \
    --n_user $NUM_CLIENTS \
    --alpha 0.5 \
    --output $DATA_DIR

