#!/usr/bin/env bash
set -euo pipefail


# ========================
# Python & Poetry Setup
# ========================

echo "Warning poetry and python will be installed for this user"
echo "Run this in a virtualenv to prevent this"

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

# Creating folders for models
mkdir upload
mkdir download
echo ">>> Setup complete!"


