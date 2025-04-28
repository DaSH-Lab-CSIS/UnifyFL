# Dependencies
- [go-ethereum](https://geth.ethereum.org/) or [anvil](https://book.getfoundry.sh/anvil/)
- [IPFS](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions) v17 
- [forge](https://book.getfoundry.sh/forge/)

# Python Dependencies
- Python 3.10
- Poetry 1.4 - Install project dependencies with `poetry install`

# Deploy the smart contracts
- `python tmux_scripts/deploy_contracts.py`

# Update configs 
- In `configs` directory, update local IPs and experiment parameters: including IPFS, goeth IPS, and smart contract ids
- Clients need to be configured with Aggregator server IPs, model info, and epochs

# Running the experiments
## Run the Aggregator Server
### Async
- `poetry run async-agg configs/async.json`
### Sync
- `poetry run sync-agg configs/async.json`

## Run the Scorer Server
### Async
- `poetry run async-scorer configs/async.json`
### Sync
- `poetry run sync-scorer configs/async.json`

## Run the Clients / Parties
- `poetry run party configs/party.json`
