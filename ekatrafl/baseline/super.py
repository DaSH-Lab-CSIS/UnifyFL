"""Flower server example."""
from collections import OrderedDict
from datetime import datetime
import getpass
import socket
from typing import Dict, Optional, Tuple
import os

import flwr as fl
from flwr.common.typing import Scalar
import torch
from ekatrafl.base.model import models

import logging
from operator import itemgetter
import sys
import json

# import wandb

from models.cifar import CIFAR10Model

# Login to wandb
# wandb.login()

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
)
# TODO: Add logs in agg and super
logger = logging.getLogger(__name__)

with open(sys.argv[1]) as f:
    config = json.load(f)
    (
        workload,
        num_rounds,
        flwr_min_fit_clients,
        flwr_min_available_clients,
        flwr_min_evaluate_clients,
        flwr_server_address,
        experiment_id,
    ) = itemgetter(
        "workload",
        "num_rounds",
        "flwr_min_fit_clients",
        "flwr_min_available_clients",
        "flwr_min_evaluate_clients",
        "flwr_server_address",
        "experiment_id",
    )(
        config
    )


model = models[workload]()

_, testloader = model.load_data()

# DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def set_weights(model, parameters):
    keys = [k for k in model.state_dict().keys() if "bn" not in k]
    params_dict = zip(keys, parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=False)


os.makedirs(f"save/baseline/{workload}/{experiment_id}", exist_ok=True)


def evaluate(
    server_round: int, parameters: fl.common.NDArrays, config: Dict[str, Scalar]
) -> Optional[Tuple[float, Dict[str, Scalar]]]:
    model = CIFAR10Model()

    set_weights(model, parameters)
    # model.to(DEVICE)

    loss, accuracy = model.test_model(testloader)
    cur_time = str(datetime.now().strftime("%d-%H-%M-%S"))
    torch.save(
        model.state_dict(),
        f"save/baseline/{workload}/{experiment_id}/{server_round}-{cur_time}-global.pt",
    )
    return loss, {"accuracy": accuracy}


#


# # Define metric aggregation function
# def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
#     # Multiply accuracy of each client by number of examples used
#     accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
#     examples = [num_examples for num_examples, _ in metrics]
#
#     # Aggregate and return custom metric (weighted average)
#     return {"accuracy": sum(accuracies) / sum(examples)}


# Define strategy
strategy = fl.server.strategy.FedAvg(
    min_fit_clients=flwr_min_fit_clients,
    min_available_clients=flwr_min_available_clients,
    min_evaluate_clients=flwr_min_evaluate_clients,
    evaluate_fn=evaluate,
)


def main():
    fl.server.start_server(
        server_address=flwr_server_address,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
    )

    # wandb.init(
    #     project="ekatrafl",
    #     config={
    #         "workload": "cifar10",
    #     },
    #     group=experiment_id,
    #     name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-super-agg",
    # )


# Start Flower server

if __name__ == "__main__":
    main()
