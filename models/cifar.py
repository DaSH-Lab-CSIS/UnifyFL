import warnings

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import Compose, Normalize, ToTensor
from tqdm import tqdm
import os


from datasets import load_from_disk


def apply_transforms(batch):
    transforms = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    batch["img"] = [transforms(img) for img in batch["img"]]
    return batch


# #############################################################################
# 1. Regular PyTorch pipeline: nn.Module, train, test, and DataLoader
# #############################################################################

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# DEVICE = "cpu"


class NTDLoss(nn.Module):
    """Not-true Distillation Loss.
    As described in:
    [Preservation of the Global Knowledge by Not-True Distillation in Federated Learning](https://arxiv.org/pdf/2106.03097.pdf)
    """

    def __init__(self, num_classes=10, tau=3, beta=1):
        super(NTDLoss, self).__init__()
        self.CE = nn.CrossEntropyLoss()
        self.KLDiv = nn.KLDivLoss(reduction="batchmean")
        self.num_classes = num_classes
        self.tau = tau
        self.beta = beta

    def forward(self, local_logits, targets, global_logits):
        """Forward pass."""
        ce_loss = self.CE(local_logits, targets)
        local_logits = self._refine_as_not_true(local_logits, targets)
        local_probs = F.log_softmax(local_logits / self.tau, dim=1)
        with torch.no_grad():
            global_logits = self._refine_as_not_true(global_logits, targets)
            global_probs = torch.softmax(global_logits / self.tau, dim=1)

        ntd_loss = (self.tau**2) * self.KLDiv(local_probs, global_probs)

        loss = ce_loss + self.beta * ntd_loss

        return loss

    def _refine_as_not_true(
        self,
        logits,
        targets,
    ):
        nt_positions = torch.arange(0, self.num_classes).to(logits.device)
        nt_positions = nt_positions.repeat(logits.size(0), 1)
        nt_positions = nt_positions[nt_positions[:, :] != targets.view(-1, 1)]
        nt_positions = nt_positions.view(-1, self.num_classes - 1)

        logits = torch.gather(logits, 1, nt_positions)

        return logits


class CIFAR10Model(nn.Module):
    """Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')"""

    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

    def train_model(self, trainloader, epochs):
        """Train the model on the training set."""
        criterion = NTDLoss(num_classes=10, tau=1, beta=1)
        optimizer = torch.optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        global_net = CIFAR10Model().to(DEVICE)
        global_net.load_state_dict(self.state_dict())
        self.train()
        for _ in range(epochs):
            for batch in tqdm(trainloader):
                images, labels = batch["image"].to(DEVICE), batch["label"].to(DEVICE)
                optimizer.zero_grad()
                local_logits = self(images)
                with torch.no_grad():
                    global_logits = global_net(images)
                criterion(local_logits, labels, global_logits).backward()
                optimizer.step()

    def test_model(self, testloader):
        """Validate the model on the test set."""
        criterion = torch.nn.CrossEntropyLoss()
        correct, loss = 0, 0.0
        with torch.no_grad():
            for batch in tqdm(testloader):
                images, labels = batch["image"].to(DEVICE), batch["label"].to(DEVICE)
                outputs = self(images.to(DEVICE))
                labels = labels.to(DEVICE)
                loss += criterion(outputs, labels).item()
                correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
        accuracy = correct / len(testloader.dataset)
        loss = loss / len(testloader)
        return loss, accuracy

    @staticmethod
    def load_data():
        """Load CIFAR-10 (training and test set)."""
        # trf = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        cur = os.environ.get("TRAIN_SET") or ""
        # trainset = ImageFolder(f"./data/cifar10/train{cur}", transform=trf)
        # testset = ImageFolder(f"./data/cifar10/train{cur}", transform=trf)
        trainset = (
            load_from_disk(f"./data/cifar10/train{cur}")
            .with_transform(apply_transforms)
            .with_format("torch")
        )
        testset = (
            load_from_disk(f"./data/cifar10/train{cur}")
            .with_transform(apply_transforms)
            .with_format("torch")
        )
        return DataLoader(trainset, batch_size=32, shuffle=True), DataLoader(testset)

    @staticmethod
    def get_testset():
        """Load CIFAR-10 test set."""
        # trf = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        # testset = ImageFolder("./data/cifar10/test", transform=trf)
        testset = (
            load_from_disk("./data/cifar10/test")
            .with_transform(apply_transforms)
            .with_format("torch")
        )
        return testset


def main():
    DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # DEVICE = "cpu"
    print("Centralized PyTorch training")
    print("Load data")
    (
        trainloader,
        testloader,
    ) = CIFAR10Model.load_data()
    net = CIFAR10Model().to(DEVICE)
    net.eval()
    print("Start training")
    net.train_model(trainloader=trainloader, epochs=2)
    print("Evaluate model")
    loss, accuracy = net.test_model(testloader=testloader)
    print("Loss: ", loss)
    print("Accuracy: ", accuracy)


if __name__ == "__main__":
    main()
