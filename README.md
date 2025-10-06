# UnifyFL

Official implementation of UnifyFL: Enabling Decentralised Cross-Silo Federated Learning accepted at MIDDLEWARE 2025.

> Federated Learning (FL) is a decentralized machine learning (ML) paradigm in which models are trained on private data across several devices called clients and combined at a single node called an aggregator rather than aggregating the data itself. Many organizations employ FL to have better privacy-aware ML-driven decision-making capabilities. However, organizations often operate independently rather than collaborate to enhance their federated learning (FL) capabilities due to the lack of an effective mechanism for collaboration. The challenge lies in balancing trust and resource efficiency. One approach relies on trusting a third-party aggregator to consolidate models from all organizations (multilevel FL), but this requires trusting an entity that may be biased or unreliable. Alternatively, organizations can bypass a third party by sharing their local models directly, which demands significant computational resources for validation. Both approaches reflect a fundamental trade-off between trust and resource constraints, with neither offering an ideal solution. In this work, we develop a trust-based cross-silo FL framework called UnifyFL that uses decentralized orchestration and distributed storage. UnifyFL provides flexibility to the participating organizations and presents synchronous and asynchronous modes to handle stragglers. Our evaluation on a diverse testbed shows that UnifyFL achieves a performance comparable to the ideal multilevel centralized FL while enabling trust and optimally utilizing the resources.

## Setup

This quick start guide demonstrates how to deploy UnifyFL with 3 aggregators, each running on a separate node, with federated learning (FL) clients colocated on the same nodes. Additionally, one node is configured to host both a blockchain (via Anvil) and a distributed storage service (via Kubo/IPFS). For simplicity, we use Anvil and Kubo in this guide; however, in a real-world deployment these components can be replaced with a Geth-based blockchain and an IPFS cluster for production-grade scalability.

To simplify deployment, Docker Compose is used to spin up FL clients and aggregator services quickly. We provide ready-to-use scripts for Ubuntu, but the setup is compatible with all major Linux distributions. The configuration demonstrated here runs in asynchronous mode using the pick_top_k and assign_score_mean 2 strategies.

To begin, clone the repository on all participating nodes:
```sh
cd ~
git clone https://github.com/DaSH-Lab-CSIS/UnifyFL
```

Install python 3.10 and dependencies using poetry on all the nodes.
```sh
cd UnifyFL/
bash deploy_scripts/setup_unifyfl.sh
```
- Note, all the commands mentioned in this document need to be run from this directory, unless mentioned otherwise.

Pick one of the nodes to also host blockchain and ipfs and run.
```sh
bash deploy_scripts/install_dependencies_main.sh
```
This installs anvil and ipfs.



On this node, open a terminal and run
```sh
anvil
```
Copy different account ids from available accounts of the anvil output into each nodes `config/async/agg.config.json` and `config/sync/agg.config.json` `account_id` field.

Copy one of the private keys of the anvil output into `deploy_scripts/deploy_contracts.py` and run:
```sh
python deploy_scripts/deploy_contracts.py 0 pick_top_k assign_score_mean 2
```
- This copies the deployed smart contract ids to the respective config file, this needs to be rerun before every new run for each experiment
- First parameter 0 => sync 1=> async
- Second parameter - pick_top_k etc: refer to `unifyfl/base/policies.py` - Recommended pick_top_k , pick_all
- Third parameter - assign_score_mean, etc: refer to `unifyfl/base/policies.py` - Recommended assign_score_mean
- Fourth parameter - k - Only used if some policy that is dependent on k - Always for the script to work



# Download and split data for training
- Use scripts `scripts/download_ds.py` and `scripts/generate_niid_dirichlet.py` - read in script documentation for config params
- mv data to `data/cifar10/train{num}` or `data/imagenet/train{num}` depending on dataset - move test dataset as well for scorers to use.
- Use the `hf` format option in the second script to format the dataset to the hugging face format, which UnifyFL uses.


# Update configs 
- Clients need to be configured with Aggregator server IPs, model info, and epochs
- Default parameter is the cifar10 dataset, with 5 epochs.

# Running the experiments
- Build the docker image on all three nodes
- `docker build -t unifyfl .`
- Install tmuxinator, tmux
- Run `tmuxinator local`
- Once the training has finished
- Run the plotting script:


## Citation

```
@misc{s2025unifyflenablingdecentralizedcrosssilo,
      title={UnifyFL: Enabling Decentralized Cross-Silo Federated Learning}, 
      author={Sarang S and Druva Dhakshinamoorthy and Aditya Shiva Sharma and Yuvraj Singh Bhadauria and Siddharth Chaitra Vivek and Arihant Bansal and Arnab K. Paul},
      year={2025},
      eprint={2504.18916},
      archivePrefix={arXiv},
      primaryClass={cs.DC},
      url={https://arxiv.org/abs/2504.18916}, 
}
```