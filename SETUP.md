# Dependencies
- [IPFS](https://docs.ipfs.tech/install/command-line/#install-official-binary-distributions) v17 
- [forge](https://book.getfoundry.sh/forge/), this installs anvil as well

# Python Dependencies
- Python 3.10
- Poetry 1.4 - Install project dependencies with `poetry install`

# Run the blockchain
- Run the command `anvil`
- Copy a private key from the terminal output to `tmux_scripts/deploy_contracts.py`
# Deploy the smart contracts
- `python tmux_scripts/deploy_contracts.py 0 pick_top_k assign_score_mean 1`
- This copies the deployed smart contract ids to the respective config file, this needs to be rerun before every new run for each experiment
- First parameter 0 => async 1=> sync
- Second parameter - pick_top_k etc: refer to `unifyfl/base/policies.py` - Recommended pick_top_k , pick_all
- Third parameter - assign_score_mean, etc: refer to `unifyfl/base/policies.py` - Recommended assign_score_mean
- Fourth parameter - k - Only used if some policy that is dependent on k - Always for the script to work


# Download and split data for training
- Use scripts `scripts/download_ds.py` and `scripts/generate_niid_dirichlet.py` - read in script documentation for config params
- mv data to `data/cifar10/train{num}` or `data/imagenet/train{num}` depending on dataset - move test dataset as well for scorers to use.
- Use the `hf` format option in the second script to format the dataset to the hugging face format, which UnifyFL uses.

# Update configs 
- Copy account id to `configs/async/agg.config.json` and `configs/sync/agg.config.json`
- Clients need to be configured with Aggregator server IPs, model info, and epochs
- Default parameter is the cifar10 dataset, with 5 epochs.

# Running the experiments
- These commands need be run in parallel, on separate shells, ideally use a terminal multiplexor such as tmux to run them at the same time
- The config is configured by default to run with 1 client, edit the relevant config `configs/(a)sync/agg.config.json` file to run multiple clients at once.
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
- `TRAIN_SET=$NUM poetry run party configs/party.json`
- Set it to a number based on the client num
