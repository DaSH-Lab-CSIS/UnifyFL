import warnings

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import Compose, Normalize, ToTensor
from tqdm import tqdm


# #############################################################################
# 1. Regular PyTorch pipeline: nn.Module, train, test, and DataLoader
# #############################################################################

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# DEVICE = "cpu"



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
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        print("training")
        for _ in range(epochs):
            for images, labels in tqdm(trainloader):
                optimizer.zero_grad()
                criterion(self(images.to(DEVICE)), labels.to(DEVICE)).backward()
                optimizer.step()
        print("Done")

    def test_model(self, testloader):
        """Validate the model on the test set."""
        criterion = torch.nn.CrossEntropyLoss()
        correct, loss = 0, 0.0
        with torch.no_grad():
            for images, labels in tqdm(testloader):
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
        trf = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        cur = os.environ.get('TRAIN_SET') or ""
        trainset = ImageFolder(f"./data/cifar10/train{cur}", transform=trf)
        testset = ImageFolder(f"./data/cifar10/train{cur}", transform=trf)
        return DataLoader(trainset, batch_size=32, shuffle=True), DataLoader(testset)

    @staticmethod
    def get_testset():
        """Load CIFAR-10 test set."""
        trf = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        testset = ImageFolder("./data/cifar10/test", transform=trf)
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
