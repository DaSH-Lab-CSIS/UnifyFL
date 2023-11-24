from collections import OrderedDict

import flwr as fl
import torch

from base.model import models


# #############################################################################
# 2. Federation of the pipeline with Flower
# #############################################################################

# Load model and data (simple CNN, CIFAR-10)

# TODO Load config
workload = "cifar10"


model = models[workload]


# Define Flower client
class FlowerClient(fl.client.NumPyClient):
    def __init__(self):
        self.model = model()
        self.trainloader, self.testloader = model.load_data()
        super().__init__()

    def get_parameters(self, config):
        print("get param")
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters):
        print("set param", type(parameters))
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.train(self.trainloader, epochs=1)
        return self.get_parameters(config={}), len(self.trainloader.dataset), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, accuracy = self.model.test(self.testloader)
        return loss, len(self.testloader.dataset), {"accuracy": accuracy}


def main():
    fl.client.start_numpy_client(
        server_address="0.0.0.0:5000",
        client=FlowerClient(),
    )


if __name__ == "__main__":
    main()
# Start Flower client
