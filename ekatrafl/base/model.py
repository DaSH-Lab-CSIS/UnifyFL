from torch.utils.data.dataloader import DataLoader
from models.cifar import CIFAR10Model
import numpy as np


models = {"cifar10": CIFAR10Model}


def accuracy_scorer(model, dataloader: DataLoader):
    return model.test_model(dataloader)[0]


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
