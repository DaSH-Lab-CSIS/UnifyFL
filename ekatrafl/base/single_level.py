"""Single Level server implementation."""
from collections import OrderedDict
import json
from operator import itemgetter

from flwr.common import parameters_to_ndarrays, ndarrays_to_parameters

from datetime import datetime
import logging
import sys
import asyncio

from time import sleep

# import wandb
from ekatrafl.base.custom_server import Server

import flwr as fl
from ekatrafl.base.model import models
import torch
import os

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
        flwr_min_fit_clients,
        flwr_min_available_clients,
        flwr_min_evaluate_clients,
        flwr_server_address,
        aggregation_policy,
        scoring_policy,
        k,
        experiment_id,
        strategy,
    ) = itemgetter(
        "workload",
        "flwr_min_fit_clients",
        "flwr_min_available_clients",
        "flwr_min_evaluate_clients",
        "flwr_server_address",
        "aggregation_policy",
        "scoring_policy",
        "k",
        "experiment_id",
        "strategy",
    )(
        config
    )

model = models[workload]


def set_weights(model, parameters):
    keys = [k for k in model.state_dict().keys() if "bn" not in k]
    params_dict = zip(keys, parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=False)


time_start = str(datetime.now().strftime("%d-%H-%M-%S"))
os.makedirs(f"save/single/{workload}/{experiment_id}", exist_ok=True)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

if strategy == "fedyogi":
    from ekatrafl.base.strategy import FedYogiAggregate

    initial_model = model()

    aggregator = FedYogiAggregate(
        initial_parameters=ndarrays_to_parameters(
            [val.cpu().numpy() for _, val in initial_model.state_dict().items()]
        )
    )


class FLServer(Server):
    """Single Level server implementation.
    Warning: Server is a subclass of fl.server.Server, setting properties that
    are common to fl.server.Server might lead to unexpected behaviour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.round_ongoing = False
        self.round_id = 0
        self.cid = None
        self.model = model()
        # threading.Thread(target=self.run_rounds).start()
        self.single_round()

    def set_parameters(self, parameters):
        print("set param", len(parameters))
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(
            state_dict,
        )

    def single_round(self):
        self.round_id += 1
        self.round_ongoing = True
        if self.round_id >= 100:
            # wandb.finish()
            exit()
        logger.info(f"Round {self.round_id} started")
        parameters = self.start_round()

        if parameters is None:
            print("Error")
            return
        parameters = parameters[0]
        weights = parameters_to_ndarrays(parameters)
        self.set_parameters(weights)
        self.round_ongoing = False
        cur_time = str(datetime.now().strftime("%d-%H-%M-%S"))
        # TODO: add host to save path
        torch.save(
            self.model.state_dict(),
            f"save/single/{workload}/{experiment_id}/{self.round_id:02d}-{cur_time}-local.pt",
        )

        logger.info(f"Round {self.round_id} ended")
        sleep(15)
        self.single_round()


# Define strategy
if strategy == "fedavg":
    strategy = fl.server.strategy.FedAvg(
        min_fit_clients=flwr_min_fit_clients,
        min_available_clients=flwr_min_available_clients,
        min_evaluate_clients=flwr_min_evaluate_clients,
    )
elif strategy == "fedyogi":
    strategy = fl.server.strategy.FedYogi(
        initial_parameters=ndarrays_to_parameters(
            [val.cpu().numpy() for _, val in initial_model.state_dict().items()]
        ),
        min_fit_clients=flwr_min_fit_clients,
        min_available_clients=flwr_min_available_clients,
        min_evaluate_clients=flwr_min_evaluate_clients,
    )
else:  # aggregation_policy == "fedopt"
    strategy = fl.server.strategy.FedAvg(
        min_fit_clients=flwr_min_fit_clients,
        min_available_clients=flwr_min_available_clients,
        min_evaluate_clients=flwr_min_evaluate_clients,
    )


def main():
    """Start server and train model."""
    # wandb.init(
    #     project="ekatrafl",
    #     config={
    #         "workload": "cifar10",
    #         "aggregation_policy": aggregation_policy,
    #         "scoring_policy": scoring_policy,
    #         "k": k,
    #     },
    #     group=experiment_id,
    #     name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-single-agg",
    # )
    FLServer(server_address=flwr_server_address, strategy=strategy)


if __name__ == "__main__":
    main()
