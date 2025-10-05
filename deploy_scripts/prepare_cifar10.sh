#!/usr/bin/env bash
set -euo pipefail

# ========================
# CIFAR10 Data Preparation
# ========================

NUM_CLIENTS=12
DATA_DIR="data/cifar10"

echo ">>> Preparing CIFAR10 dataset for $NUM_CLIENTS clients..."

# Ensure Poetry environment is activated
if ! command -v poetry &> /dev/null; then
    echo ">>> Poetry not found. Please run setup_unifyfl.sh first."
    exit 1
fi

# Step 1: Download CIFAR10 dataset
echo ">>> Downloading CIFAR10 dataset..."
poetry run python scripts/download_ds.py --dataset cifar10 --output data/cifar10_raw

# Step 2: Split dataset into non-IID partitions
echo ">>> Generating non-IID splits for $NUM_CLIENTS clients..."
poetry run python scripts/generate_niid_dirichlet.py \
    --dataset data/cifar10_raw \
    --clients $NUM_CLIENTS \
    --alpha 0.5 \
    --format hf \
    --output $DATA_DIR

# Step 3: Move train/test datasets into expected directory structure
echo ">>> Organizing dataset into $DATA_DIR/train{num}..."
for i in $(seq 0 $((NUM_CLIENTS-1))); do
    mkdir -p "$DATA_DIR/train$i"
    mv "$DATA_DIR/client_$i"/* "$DATA_DIR/train$i/"
    rmdir "$DATA_DIR/client_$i"
done

# Step 4: Move test dataset (if available)
if [ -d "$DATA_DIR/test" ]; then
    echo ">>> Test dataset already present."
else
    echo ">>> Copying test dataset..."
    cp -r data/cifar10_raw/test $DATA_DIR/test
fi

echo ">>> CIFAR10 preparation complete!"
echo "Dataset is now split into $NUM_CLIENTS clients under $DATA_DIR/train{num}."
