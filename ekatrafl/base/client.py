from collections import OrderedDict

import flwr as fl
from flwr.common.typing import NDArray
import torch
import socket
import getpass
from ekatrafl.base.model import models


# #############################################################################
# 2. Federation of the pipeline with Flower
# #############################################################################

# Load model and data (simple CNN, CIFAR-10)


# Login to wandb


class BaseClient(fl.client.NumPyClient):
    def __init__(self, model, log=False):
        self.model = model()
        # self.trainloader, self.testloader = model.load_data()
        self.log = log
        super().__init__()

    def get_parameters(self, config):
        print("get param")
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: NDArray):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)


# Define Flower client
class FlowerClient(BaseClient):
    def __init__(self, model, log=False):
        self.trainloader, self.testloader = model.load_data()
        super().__init__(model, log)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.train_model(self.trainloader, epochs=1)
        return self.get_parameters(config={}), len(self.trainloader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, accuracy = self.model.test_model(self.testloader)
        return loss, len(self.testloader.dataset), {"accuracy": accuracy}


def main():
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
            flwr_server_address,
        ) = itemgetter(
            "workload",
            "flwr_server_address",
        )(config)

    model = models[workload]
    fl.client.start_numpy_client(
        server_address=flwr_server_address,
        client=FlowerClient(model, log=True),
    )



if __name__ == "__main__":
    main()
# Start Flower client
