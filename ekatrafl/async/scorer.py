import asyncio
import getpass
import json
import logging
import math
from socket import socket
import sys
from time import sleep
from operator import itemgetter
from flwr.common import parameters_to_ndarrays
import torch
import wandb
from torch.utils.data import DataLoader, Subset
from web3 import Web3

from web3.middleware import geth_poa_middleware
from ekatrafl.base.contract import create_async_contract, create_reg_contract

from ekatrafl.base.ipfs import load_model_ipfs
from ekatrafl.base.model import accuracy_scorer, models, scorers, set_parameters

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
)
logger = logging.getLogger(__name__)

wandb.login()

with open(sys.argv[1]) as f:
    config = json.load(f)
    (
        workload,
        scoring,
        geth_endpoint,
        registration_contract_address,
        async_contract_address,
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

model = models[workload]
scorer = scorers[scoring]

wandb.login()
logger.info(f"Model: {model.__name__}")
logger.info(f"Scorer: {scorer.__name__}")

w3 = Web3(Web3.HTTPProvider(geth_endpoint))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = account

testset = model.get_testset()
testloader = DataLoader(
    testset,
    # Subset(testset, torch.randperm(len(testset))[: math.floor(len(testset) / 2)]),
    batch_size=64,
)

registration_contract = create_reg_contract(w3, registration_contract_address)
async_contract = create_async_contract(w3, async_contract_address)


async def score_model(trainer: str, cid: str):
    model = models[workload]()
    logger.info(f"Model recevied to score with CID: {cid}")
    # model.load_state_dict(await load_model_ipfs(cid, ipfs_host))
    parameters = await load_model_ipfs(cid, ipfs_host)
    weights = parameters_to_ndarrays(parameters)
    set_parameters(model, weights)
    logger.info("Model pull from IPFS")
    loss, accuracy = accuracy_scorer(model, testloader)
    logger.info(f"Accuracy: {(accuracy*100):>0.2f}%")
    logger.info(f"Loss: {(loss):>0.2f}")
    async_contract.functions.submitScore(cid, int(accuracy)).transact()
    logger.info(f"Model scores submitted to contract")


def main():
    registration_contract.functions.registerNode("scorer").transact()
    events = set()
    last_seen_block = w3.eth.block_number
    wandb.init(
        project="ekatrafl",
        config={
            "workload": "cifar10",
            "scorer": scoring,
        },
        group=experiment_id,
        name=f"{socket.gethostname() if socket.hostname() != 'raspberrypi' else getpass.getuser()}-async-scorer",
    )
    while True:
        for event in async_contract.events.StartScoring().get_logs(
            fromBlock=last_seen_block
        ):
            if event not in events:
                events.add(event)
                last_seen_block = event["blockNumber"]
                if w3.eth.default_account in event["args"]["scorers"]:
                    print(event["args"])
                    asyncio.run(
                        score_model(event["args"]["trainer"], event["args"]["model"])
                    )
        sleep(1)


if __name__ == "__main__":
    main()
