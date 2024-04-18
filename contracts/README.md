# Contracts

## Overview

The Solidity smart contracts used in the EkatraFL project that facilitate various functionalities of the orchestrator.

### 1. Registration.sol

The Registration contract manages the registration of nodes as trainers or scorers. Nodes can register themselves as trainers or scorers, and their registration status is maintained in the contract. This contract provides functions to retrieve the addresses of registered trainers and scorers.

### 2. RandomNumbers.sol

The RandomNumbers contract provides functionality to generate a random permutation of an array of addresses. This functionality is utilized in the EkatraFL project to randomly assign scorers for scoring models during each round of federated learning.

### 3. SyncRound.sol

The SyncRound contract manages synchronous rounds of federated learning. It orchestrates the training and scoring phases, allowing trainers to submit models and scorers to submit scores for evaluation. This contract ensures that only registered trainers and scorers can participate in the process.
### 4. AsyncRound.sol

The AsyncRound contract manages asynchronous rounds of federated learning. Trainers can submit their models, and registered scorers can submit scores for evaluation. It emits events for model submission, scoring initiation, and score submission.  Similar to SyncRound, it ensures that only registered trainers and scorers can participate in the process.

## ABI

The ABI subfolder contains the compiled ABI files of the contracts. These ABI files are generated using Remix Ethereum IDE or similar tools during the compilation process. They define the interface of each contract, allowing interaction with the contracts from external applications or scripts.


## Usage

To use these contracts, deploy them on a compatible blockchain platform (e.g., Ethereum).  Ensure that the RandomNumbers and Registration contracts are deployed and linked appropriately with the AsyncRound and SyncRound contracts. Trainers and scorers can then interact with the deployed contracts according to their respective roles, submitting models and scores as required.

