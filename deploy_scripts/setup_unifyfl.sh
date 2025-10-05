#!/usr/bin/env bash
set -euo pipefail

# ========================
# Install Dependencies
# ========================

echo ">>> Installing dependencies for UnifyFL experiments..."
echo ">>> Will work on systems with apt-get installed"

# --- Install IPFS v0.17 (if not already installed) ---
if ! command -v ipfs &> /dev/null; then
    echo ">>> Installing IPFS..."
    wget https://dist.ipfs.tech/kubo/v0.17.0/kubo_v0.17.0_linux-amd64.tar.gz -O /tmp/ipfs.tar.gz
    tar -xvzf /tmp/ipfs.tar.gz -C /tmp
    sudo bash /tmp/kubo/install.sh
    rm -rf /tmp/ipfs*
else
    echo ">>> IPFS already installed."
fi

# --- Install Foundry (Forge + Anvil) ---
if ! command -v forge &> /dev/null; then
    echo ">>> Installing Foundry (forge + anvil)..."
    curl -L https://foundry.paradigm.xyz | bash
    # shellcheck disable=SC1090
    source ~/.foundry/bin
    foundryup
else
    echo ">>> Foundry (forge) already installed."
fi

# ========================
# Python & Poetry Setup
# ========================

# --- Check Python 3.10 ---
if ! python3.10 --version &> /dev/null; then
    echo ">>> Installing Python 3.10..."
    sudo apt-get update
    sudo apt-get install -y python3.10 python3.10-venv python3.10-dev
else
    echo ">>> Python 3.10 already installed."
fi

# --- Install Poetry v1.4 ---
if ! command -v poetry &> /dev/null; then
    echo ">>> Installing Poetry 1.4..."
    curl -sSL https://install.python-poetry.org | python3.10 - --version 1.4.0
    # shellcheck disable=SC1090
    export PATH="$HOME/.local/bin:$PATH"
else
    echo ">>> Poetry already installed."
fi

# ========================
# Install Python Project Dependencies
# ========================

echo ">>> Installing project dependencies with Poetry..."
poetry install

# ========================
# Done
# ========================
echo ">>> Setup complete!"
echo "Next steps:"
echo "1. Run 'anvil' to start the blockchain testnet."
echo "2. Copy a private key from anvil output into tmux_scripts/deploy_contracts.py."
echo "3. Deploy contracts with:"
echo "   python tmux_scripts/deploy_contracts.py 0 pick_top_k assign_score_mean 1"
