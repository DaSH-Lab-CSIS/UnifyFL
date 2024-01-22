from datetime import datetime
import getpass
import logging
from operator import itemgetter
import socket
from flwr.common import parameters_to_ndarrays
import torch
from ekatrafl.base.custom_server import Server
from ekatrafl.base.client import BaseClient
import flwr as fl
import sys
import json
import wandb

# Login to wandb
wandb.login()


from ekatrafl.base.model import models

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
        flwr_min_fit_clients,
        flwr_min_available_clients,
        flwr_min_evaluate_clients,
        flwr_super_address,
        flwr_sub_address,
        experiment_id,
    ) = itemgetter(
        "workload",
        "flwr_min_fit_clients",
        "flwr_min_available_clients",
        "flwr_min_evaluate_clients",
        "flwr_super_address",
        "flwr_sub_address",
        "experiment_id",
    )(
        config
    )


class ClientServer(BaseClient):
    def __init__(self, address: str = "0.0.0.0:5000") -> None:
        super().__init__(models[workload])
        strategy = fl.server.strategy.FedAvg(
            min_fit_clients=flwr_min_fit_clients,
            min_available_clients=flwr_min_available_clients,
            min_evaluate_clients=flwr_min_evaluate_clients,
        )
        self.server = Server(server_address=address, strategy=strategy)
        self.round = 0

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        # We are not setting parameters for the server????
        self.server.parameters = parameters
        parameters = self.server.start_round()
        if parameters is None:
            print("Error")
        else:
            weights = parameters_to_ndarrays(parameters)
            self.set_parameters(weights)
        cur_time = str(datetime.now().strftime("%d-%H-%M-%S"))
        torch.save(
            self.model.state_dict(),
            f"save/baseline/{workload}/{experiment_id}/{self.round}-{cur_time}-local.pt",
        )
        self.round += 1
        return self.get_parameters(config={}), len(self.trainloader.dataset), {}


def main():
    fl.client.start_numpy_client(
        server_address=flwr_super_address, client=ClientServer(flwr_sub_address)
    )

    wandb.init(
        project="ekatrafl",
        config={
            "workload": "cifar10",
        },
        group=experiment_id,
        name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-baseline-agg",
    )


if __name__ == "__main__":
    main()
