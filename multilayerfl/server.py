"""Flower server example."""
from collections import OrderedDict

import flwr as fl
import torch
from base.model import models

# TODO: Read config

workload = "cifar10"


model = models[workload]()

trainloader, testloader = model.load_data()

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


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
    # evaluate_metrics_aggregation_fn=weighted_average,
    min_fit_clients=1,
    min_available_clients=1,
    min_evaluate_clients=1,
)


if __name__ == "__main__":
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=2),
        strategy=strategy,
    )
# Start Flower server
