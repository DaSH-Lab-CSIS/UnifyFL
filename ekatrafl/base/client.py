from collections import OrderedDict

import flwr as fl
from flwr.common.typing import NDArray
import torch
from ekatrafl.base.model import models
from opacus import PrivacyEngine
import os


# #############################################################################
# 2. Federation of the pipeline with Flower
# #############################################################################

# Load model and data (simple CNN, CIFAR-10)


# Login to wandb
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class BaseClient(fl.client.NumPyClient):
    def __init__(self, model, log=False):
        self.model = model().to(DEVICE)
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
    def __init__(self, model, log=False, epochs=1):
        self.epochs = epochs
        self.trainloader, self.testloader = model.load_data()
        self.optimizer = self.model.get_optimizer()
        super().__init__(model, log)
        if os.environ.get("PRIVACY"):
            print("Privacy Enabled")
            privacy_engine = PrivacyEngine()
            self.model, self.optimizer, self.trainloader = privacy_engine.make_private(
                module=self.model,
                optimizer=self.optimizer,
                data_loader=self.trainloader,
                noise_multiplier=1.1,
                max_grad_norm=1.0,
            )

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.train_model(self.trainloader, self.epochs, self.optimizer)
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
    # logger = logging.getLogger(__name__)

    with open(sys.argv[1]) as f:
        config = json.load(f)
        (workload, flwr_server_address, epochs) = itemgetter(
            "workload", "flwr_server_address", "epochs"
        )(config)

    model = models[workload]
    fl.client.start_numpy_client(
        server_address=flwr_server_address,
        client=FlowerClient(model, log=True, epochs=epochs),
    )


if __name__ == "__main__":
    main()
# Start Flower client
