from typing import OrderedDict
from flwr.common.typing import NDArray, Parameters
import torch
from torch.utils.data.dataloader import DataLoader
from models.cifar import CIFAR10Model
import numpy as np
from torch import nn

import flwr as fl


models = {"cifar10": CIFAR10Model}


def accuracy_scorer(model, dataloader: DataLoader):
    return model.test_model(dataloader)


def get_weights(model: nn.Module.state_dict) -> fl.common.NDArrays:
    """Get model weights as a list of NumPy ndarrays."""
    return [val.cpu().numpy() for _, val in model.items()]


def set_parameters(model, parameters: NDArray):
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)


def multikrum_scorer(weights):
    R = len(weights)
    f = R // 3 - 1
    closest_updates = R - f - 2

    keys = weights[0].keys()

    return [
        sum(
            sorted(
                [
                    sum(
                        [
                            np.linalg.norm(
                                weights[i][key].cpu() - weights[j][key].cpu()
                            )
                            for key in keys
                        ]
                    )
                    for j in range(R)
                    if j != i
                ]
            )[:closest_updates]
        )
        for i in range(R)
    ]


scorers = {
    "accuracy": accuracy_scorer,
    # "marginal_gain": marginal_gain_scorer,
    "multi_krum": multikrum_scorer,
}
