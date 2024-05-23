from typing import List, OrderedDict
from flwr.common.typing import NDArray, Parameters
import torch
from torch.utils.data.dataloader import DataLoader
from models.cifar import CIFAR10Model
from models.emnist import EMNISTModel
from models.mnist import MNISTModel
from models.imagenet import ImageNetModel
import numpy as np
from torch import nn

import flwr as fl


models = {
    "cifar10": CIFAR10Model,
    "emnist": EMNISTModel,
    "mnist": MNISTModel,
    "imagenet": ImageNetModel,
}


def accuracy_scorer(model, dataloader: DataLoader):
    return model.test_model(dataloader)


def get_weights(model: nn.Module.state_dict) -> fl.common.NDArrays:
    """Get model weights as a list of NumPy ndarrays."""
    return [val.cpu().numpy() for _, val in model.items()]


def set_parameters(model, parameters: NDArray):
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=True)



def multikrum_scorer(
    weights: List[NDArray],  # noqa: U100
) -> List[float]:
    def compute_distances(weights: List[NDArray]) -> NDArray:  # noqa: U100
        flat_w = np.array([np.concatenate(p, axis=None).ravel() for p in weights])
        distance_matrix = np.zeros((len(weights), len(weights)))
        for i, flat_w_i in enumerate(flat_w):
            for j, flat_w_j in enumerate(flat_w):
                delta = flat_w_i - flat_w_j
                norm = np.linalg.norm(delta)
                distance_matrix[i, j] = norm**2
        return distance_matrix
    distance_matrix = compute_distances(weights)
    f = len(weights) // 3 - 1      
    num_closest = max(1, len(weights) - f - 2)
    closest_indices = []
    for distance in distance_matrix:
        closest_indices.append(
            np.argsort(distance)[1 : num_closest + 1].tolist()  # noqa: E203
        )
    scores = [
        np.sum(distance_matrix[i, closest_indices[i]])
        for i in range(len(distance_matrix))
    ]
    max_score = max(scores)
    scores = [s/max_score*100 for s in scores]
    return scores

scorers = {
    "accuracy": accuracy_scorer,
    # "marginal_gain": marginal_gain_scorer,
    "multi_krum": multikrum_scorer,
}
