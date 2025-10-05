"""Async EkatraFl server implementation."""
from collections import OrderedDict
import getpass
import json
from operator import itemgetter
import socket

from flwr.common import ndarrays_to_parameters
from unifyfl.base.policies import pick_selected_model

# from flwr.common import parameters_to_ndarrays

from datetime import datetime
import logging
import sys
import asyncio

from web3 import Web3
from time import sleep

# import wandb
from web3.middleware import geth_poa_middleware
from unifyfl.base.contract import create_reg_contract, create_async_contract
from unifyfl.base.custom_server import Server

from unifyfl.base.ipfs import load_models, save_model_ipfs

# import flwr as fl
# from flwr.server.strategy.aggregate import aggregate
from unifyfl.base.model import models
import torch
import os
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
        geth_endpoint,
        geth_account,
        registration_contract_address,
        async_contract_address,
        flwr_min_fit_clients,
        flwr_min_available_clients,
        flwr_min_evaluate_clients,
        flwr_server_address,
        ipfs_host,
        aggregation_policy,
        scoring_policy,
        k,
        experiment_id,
    ) = itemgetter(
        "workload",
        "geth_endpoint",
        "geth_account",
        "registration_contract_address",
        "contract_address",
        "flwr_min_fit_clients",
        "flwr_min_available_clients",
        "flwr_min_evaluate_clients",
        "flwr_server_address",
        "ipfs_host",
        "aggregation_policy",
        "scoring_policy",
        "k",
        "experiment_id",
    )(
        config
    )

model = models[workload]


# DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def set_weights(model, parameters):
    keys = [k for k in model.state_dict().keys() if "bn" not in k]
    params_dict = zip(keys, parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=False)


w3 = Web3(Web3.HTTPProvider(geth_endpoint))

# Add this line when changing from anvil to geth chain
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = geth_account

registration_contract = create_reg_contract(w3, registration_contract_address)
# TODO: Add registration
async_contract = create_async_contract(w3, async_contract_address)


time_start = str(datetime.now().strftime("%d-%H-%M-%S"))
os.makedirs(f"save/async/{workload}/{experiment_id}", exist_ok=True)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# def evaluate(
#     server_round: int, parameters: fl.common.NDArrays, config: Dict[str, Scalar]
# ) -> Optional[Tuple[float, Dict[str, Scalar]]]:
#     model_instance = model()
#     set_weights(model, parameters)
#     model.to(DEVICE)
#
#     loss, accuracy = model_instance.test(testloader, device=DEVICE)
#     print(loss, accuracy)
#     return loss, {"accuracy": accuracy}


class AsyncServer(Server):
    """Async server implementation.
    Warning: Server is a subclass of fl.server.Server, setting properties that
    are common to fl.server.Server might lead to unexpected behaviour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.round_ongoing = False
        self.round_id = 0
        self.model = model()
        registration_contract.functions.registerNode("trainer").transact()
        # threading.Thread(target=self.run_rounds).start()
        self.single_round()

    def single_round(self):
        # self.aggregate_models()
        self.round_ongoing = True
        self.round_id += 1
        self.model = model()
        if self.round_id >= 100:
            # wandb.finish()
            exit()
        logger.info(f"Round {self.round_id} started")
        # parameters = self.start_round()
        sleep(15)

        param_list = ndarrays_to_parameters(
            [val.cpu().numpy() for _, val in self.model.state_dict.items()]
        )
        # if parameters is None:
        #     print("Error")
        #     return
        # weights = parameters_to_ndarrays(parameters)
        self.server.parameters = param_list
        self.round_ongoing = False
        cur_time = str(datetime.now().strftime("%d-%H-%M-%S"))
        # TODO: add host to save path
        torch.save(
            self.model.state_dict(),
            f"save/async/{workload}/{experiment_id}/{self.round_id:02d}-{cur_time}-local.pt",
        )

        cid = asyncio.run(save_model_ipfs(param_list, ipfs_host))
        logger.info(f"Model saved to IPFS with CID: {cid}")
        while True:
            try:
                async_contract.functions.submitModel(cid).transact()
                break
            except:
                sleep(5)
                continue
        logger.info("Model submitted to contarct")
        logger.info(f"Round {self.round_id} ended")
        # TODO: add timer here
        self.single_round()


# Define strategy
# strategy = fl.server.strategy.FedAvg(
#     min_fit_clients=flwr_min_fit_clients,
#     min_available_clients=flwr_min_available_clients,
#     min_evaluate_clients=flwr_min_evaluate_clients,
# )


def main():
    """Start server and train model."""
    # wandb.init(
    #     project="unifyfl",
    #     config={
    #         "workload": "cifar10",
    #         "aggregation_policy": aggregation_policy,
    #         "scoring_policy": scoring_policy,
    #         "k": k,
    #     },
    #     group=experiment_id,
    #     name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-async-agg",
    # )
    # AsyncServer(server_address=flwr_server_address, strategy=strategy)


if __name__ == "__main__":
    main()
