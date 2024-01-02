"""Flower server example."""
from collections import OrderedDict

import flwr as fl
import torch
from ekatrafl.base.model import models

import logging
from operator import itemgetter
import sys
import json


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
    ) = itemgetter(
        "workload",
        "num_rounds",
        "flwr_min_fit_clients",
        "flwr_min_available_clients",
        "flwr_min_evaluate_clients",
        "flwr_server_address",
    )(
        config
    )


model = models[workload]()

trainloader, testloader = model.load_data()

# DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def set_weights(model, parameters):
    keys = [k for k in model.state_dict().keys() if "bn" not in k]
    params_dict = zip(keys, parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=False)


# def evaluate(
#     server_round: int, parameters: fl.common.NDArrays, config: Dict[str, Scalar]
# ) -> Optional[Tuple[float, Dict[str, Scalar]]]:
#     model = cifar.Net()
#
#     set_weights(model, parameters)
#     model.to(DEVICE)
#
#     loss, accuracy = cifar.test(model, testloader, device=DEVICE)
#     print(loss, accuracy)
#     return loss, {"accuracy": accuracy}
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
)


def main():
    fl.server.start_server(
        server_address=flwr_server_address,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
    )


# Start Flower server

if __name__ == "__main__":
    main()
