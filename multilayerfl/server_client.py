from flwr.common import parameters_to_ndarrays
from base.custom_server import Server
from client import FlowerClient
import flwr as fl

from server import weighted_average


class ClientServer(FlowerClient):
    def __init__(self, address: str = "0.0.0.0:5000") -> None:
        super().__init__()
        strategy = fl.server.strategy.FedAvg(
            evaluate_metrics_aggregation_fn=weighted_average,
            min_fit_clients=1,
            min_available_clients=1,
            min_evaluate_clients=1,
        )
        self.server = Server(server_address=address, strategy=strategy)

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
        return self.get_parameters(config={}), len(self.trainloader.dataset), {}


if __name__ == "__main__":
    fl.client.start_numpy_client(server_address="0.0.0.0:8080", client=ClientServer())
