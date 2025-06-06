import os
import csv
from typing import List, Tuple
import torch
import csv
import sys
from torch.utils.data import DataLoader
from ekatrafl.base.model import models

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
DEVICE = "cpu"

model = models["cifar10"]().to(DEVICE)
# model = CIFAR10Model().to(DEVICE)
testset = model.get_testset()
testloader = DataLoader(testset, batch_size=64)

files = sorted(
    [f for f in os.listdir(sys.argv[1]) if os.path.isfile(os.path.join(sys.argv[1], f))]
)

local_files = sorted(
    [f for f in files if f.split("-")[-1] == "local.pt"],
    key=lambda x: int(x.split("-")[0]),
)
global_files = sorted(
    [f for f in files if f.split("-")[-1] == "global.pt"],
    key=lambda x: int(x.split("-")[0]),
)


def evaluate_model(filename: str) -> List[float]:
    model.load_state_dict(torch.load(os.path.join(sys.argv[1], filename)))
    loss, accuracy = model.test_model(testloader)
    return [accuracy * 100, loss]


with open(os.path.join(sys.argv[1], sys.argv[2] + "_local.csv"), "a+") as f:
    csvwriter = csv.writer(f)
    for file in local_files:
        csvwriter.writerow(
            [file.split("-")[0], "-".join(file.split("-")[1:5])] + evaluate_model(file)
        )

with open(os.path.join(sys.argv[1], sys.argv[2] + "_global.csv"), "a+") as f:
    csvwriter = csv.writer(f)
    for file in global_files:
        csvwriter.writerow(
            [file.split("-")[0], "-".join(file.split("-")[1:5])] + evaluate_model(file)
        )
