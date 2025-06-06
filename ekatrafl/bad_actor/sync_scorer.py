import asyncio
import getpass
import json
import logging
import math
import socket
import sys
import time
from operator import itemgetter

# import torch

# from flwr.common import parameters_to_ndarrays
# from torch.utils.data import DataLoader, Subset
from web3 import Web3
from web3.middleware import geth_poa_middleware
from ekatrafl.base.contract import create_reg_contract, create_sync_contract

# from ekatrafl.base.ipfs import load_model_ipfs
# from ekatrafl.base.model import models, scorers, set_parameters
# import wandb
import random

# wandb.login()
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
)
logger = logging.getLogger(__name__)

with open(sys.argv[1]) as f:
    config = json.load(f)
    (
        workload,
        scoring,
        geth_endpoint,
        registration_contract_address,
        sync_contract_address,
        ipfs_host,
        account,
        experiment_id,
    ) = itemgetter(
        "workload",
        "scorer",
        "geth_endpoint",
        "registration_contract_address",
        "contract_address",
        "ipfs_host",
        "geth_account",
        "experiment_id",
    )(
        config
    )
    # model = models[workload]
    # scorer = scorers[scoring]

# logger.info(f"Model: {model.__name__}")
# logger.info(f"Scorer: {scorer.__name__}")

w3 = Web3(Web3.HTTPProvider(geth_endpoint))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = account


# nn_model = models[workload]()
# print(nn_model)


# def score_function(models, testloader: DataLoader):
#     if scoring == "accuracy":
#         q = []
#         for model_dict in models:
#             weights = parameters_to_ndarrays(model_dict)
#             set_parameters(nn_model, weights)
#             q.append(scorer(nn_model, testloader))
#         return q
#     elif scoring == "multi_krum":
#         return scorer(models)


# testset = model.get_testset()
# testloader = DataLoader(
#     testset,
#     # Subset(testset, torch.randperm(len(testset))[: math.floor(len(testset) / 2)]),
#     batch_size=64,
# )

registration_contract = create_reg_contract(w3, registration_contract_address)
sync_contract = create_sync_contract(w3, sync_contract_address)


async def score_model(round: int, cids: str):
    for cid in cids:
        time.sleep(5)
        random_score = random.randint(0, 100)
        logger.info(f"model: {cid} -> score: {(random_score):>0.1f}")
        sync_contract.functions.submitScore(round, cid, random_score).transact()
    logger.info(f"Model scores submitted to contract")


def main():
    registration_contract.functions.registerNode("scorer").transact()
    events = set()
    last_seen_block = w3.eth.block_number
    # wandb.init(
    #     project="ekatrafl",
    #     config={
    #         "workload": "cifar10",
    #         "scorer": scoring,
    #     },
    #     group=experiment_id,
    #     name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-sync-scorer",
    # )
    while True:
        for event in sync_contract.events.StartScoring().get_logs(
            fromBlock=last_seen_block
        ):
            if event not in events:
                events.add(event)
                last_seen_block = event["blockNumber"]
                if w3.eth.default_account in event["args"]["scorers"]:
                    asyncio.run(
                        score_model(event["args"]["round"], event["args"]["models"])
                    )
        time.sleep(1)
