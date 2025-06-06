import asyncio
import json
import logging
import torch
import sys
from time import sleep
from operator import itemgetter
import os

# import wandb
from torch.utils.data import DataLoader, Subset
from web3 import Web3

from ekatrafl.base.contract import create_async_contract, create_reg_contract

from ekatrafl.base.ipfs import load_model_ipfs
from ekatrafl.base.model import accuracy_scorer, models, scorers, set_parameters

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
)
logger = logging.getLogger(__name__)

# wandb.login()

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

logger.info(f"Model: {model.__name__}")
logger.info(f"Scorer: {scorer.__name__}")

w3 = Web3(Web3.HTTPProvider(geth_endpoint))
if os.getenv("GETH_POA"):
    from web3.middleware import geth_poa_middleware

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
    DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"
    model = models[workload]().to(DEVICE)
    logger.info(f"Model recevied to score with CID: {cid}")
    # model.load_state_dict(await load_model_ipfs(cid, ipfs_host))
    model.load_state_dict(await load_model_ipfs(cid, ipfs_host))

    logger.info("Model pull from IPFS")
    loss, accuracy = accuracy_scorer(model, testloader)
    logger.info(f"Accuracy: {(accuracy*100):>0.2f}%")
    logger.info(f"Loss: {(loss):>0.2f}")
    async_contract.functions.submitScore(cid, int(accuracy * 1000)).transact()
    logger.info("Model scores submitted to contract")


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
    #     name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-async-scorer",
    # )
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
