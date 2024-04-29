import warnings

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from torchvision.transforms import Compose, Normalize, ToTensor, Lambda
from tqdm import tqdm
import os


from datasets import load_from_disk


def apply_transforms(batch):
    tfs = Compose(
        [
            ToTensor(),
            Lambda(lambda x: x.repeat(3, 1, 1) if x.size(0) == 1 else x),
        ]
    )
    batch["image"] = [tfs(img) for img in batch["image"]]
    return batch


# #############################################################################
# 1. Regular PyTorch pipeline: nn.Module, train, test, and DataLoader
# #############################################################################

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# DEVICE = "cpu"


class ImageNetModel(nn.Module):
    def __init__(self, num_classes=200) -> None:
        super(ImageNetModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.conv4 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1)
        self.conv5 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
        self.conv6 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)
        self.conv7 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)
        self.conv8 = nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1)
        self.conv9 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv10 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv11 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv12 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.conv13 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1)
        self.fc = nn.Linear(2048, 2048)
        self.fc1 = nn.Linear(2048, 512)
        self.fc2 = nn.Linear(512, num_classes)

        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(
            F.batch_norm(
                self.conv1(x), running_mean=None, running_var=None, training=True
            )
        )
        x = self.pool(
            F.relu(
                F.batch_norm(
                    self.conv2(x), running_mean=None, running_var=None, training=True
                )
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv3(x), running_mean=None, running_var=None, training=True
            )
        )
        x = self.pool(
            F.relu(
                F.batch_norm(
                    self.conv4(x), running_mean=None, running_var=None, training=True
                )
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv5(x), running_mean=None, running_var=None, training=True
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv6(x), running_mean=None, running_var=None, training=True
            )
        )
        x = self.pool(
            F.relu(
                F.batch_norm(
                    self.conv7(x), running_mean=None, running_var=None, training=True
                )
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv8(x), running_mean=None, running_var=None, training=True
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv9(x), running_mean=None, running_var=None, training=True
            )
        )
        x = self.pool(
            F.relu(
                F.batch_norm(
                    self.conv10(x), running_mean=None, running_var=None, training=True
                )
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv11(x), running_mean=None, running_var=None, training=True
            )
        )
        x = F.relu(
            F.batch_norm(
                self.conv12(x), running_mean=None, running_var=None, training=True
            )
        )
        x = self.pool(
            F.relu(
                F.batch_norm(
                    self.conv13(x), running_mean=None, running_var=None, training=True
                )
            )
        )
        x = x.view(-1, 2048)
        x = F.relu(self.fc(F.dropout(x, 0.5)))
        x = F.relu(self.fc1(F.dropout(x, 0.5)))
        x = self.fc2(x)

        return x

    def train_model(self, trainloader, epochs):
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        self.train()
        for _ in range(epochs):
            for batch in tqdm(trainloader):
                images, labels = batch["image"].to(DEVICE).float(), batch["label"].to(
                    DEVICE
                )
                optimizer.zero_grad()
                criterion(self(images), labels).backward()
                optimizer.step()

    def test_model(self, testloader):
        criterion = torch.nn.CrossEntropyLoss()
        correct, loss = 0, 0.0
        total = 0
        with torch.no_grad():
            for batch in tqdm(testloader):
                images, labels = (
                    batch["image"].to(DEVICE).float(),
                    batch["label"].to(DEVICE),
                )
                outputs = self(images)
                loss += criterion(outputs, labels).item()
                total += labels.size(0)
                correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
        accuracy = correct / total
        loss = loss / len(testloader)
        return loss, accuracy

    @staticmethod
    def load_data():
        cur = os.environ.get("TRAIN_SET") or ""
        trainset = load_from_disk(f"./data/imagenet/train{cur}").with_transform(
            apply_transforms
        )
        testset = load_from_disk("./data/imagenet/test").with_transform(
            apply_transforms
        )
        return DataLoader(trainset, batch_size=128, shuffle=True), DataLoader(testset)

    @staticmethod
    def get_testset():
        testset = load_from_disk("./data/imagenet/test").with_transform(
            apply_transforms
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
    ) = ImageNetModel.load_data()
    net = ImageNetModel().to(DEVICE)
    net.eval()
    print("Start training")
    net.train_model(trainloader=trainloader, epochs=2)
    print("Evaluate model")
    loss, accuracy = net.test_model(testloader=testloader)
    print("Loss: ", loss)
    print("Accuracy: ", accuracy)


if __name__ == "__main__":
    main()
