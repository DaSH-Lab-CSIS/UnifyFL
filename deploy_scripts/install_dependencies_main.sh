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
    ipfs init
else
    echo ">>> IPFS already installed."
fi

# --- Install Foundry (Forge + Anvil) ---
if ! command -v forge &> /dev/null; then
    echo ">>> Installing Foundry (forge + anvil)..."
    curl -L https://foundry.paradigm.xyz | bash
    # shellcheck disable=SC1090
<<<<<<< Updated upstream
    export PATH="~/.foundry/bin:$PATH"   
=======
    export PATH="~/.foundry/bin:$PATH"
>>>>>>> Stashed changes
    foundryup
else
    echo ">>> Foundry (forge) already installed."
fi


# ========================
# Done
# ========================
echo ">>> Setup complete!"
