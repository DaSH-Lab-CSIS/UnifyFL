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

from transformers import AutoModelForSequenceClassification 



from evaluate import load as load_metric
from transformers import AdamW







import random

import torch
from datasets import load_dataset
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, DataCollatorWithPadding


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CHECKPOINT = "distilbert-base-uncased"

class IMDbModel(nn.Module):
    def __init__(self, num_classes=200) -> None:
        super(IMDbModel, self).__init__()
        self.bert = AutoModelForSequenceClassification.from_pretrained(CHECKPOINT, num_labels=2).to(DEVICE)

    def train_model(self, trainloader, epochs):
        optimizer = AdamW(self.bert.parameters(), lr=5e-5)
        self.bert.train()
        for _ in range(epochs):
            for batch in trainloader:
                batch = {k: v.to(DEVICE) for k, v in batch.items()}
                outputs = self.bert(**batch)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

    def test_model(self, testloader):
        metric = load_metric("accuracy")
        loss = 0
        self.bert.eval()
        for batch in testloader:
            batch = {k: v.to(DEVICE) for k, v in batch.items()}
            with torch.no_grad():
                outputs = self.bert(**batch)
            logits = outputs.logits
            loss += outputs.loss.item()
            predictions = torch.argmax(logits, dim=-1)
            metric.add_batch(predictions=predictions, references=batch["labels"])
        loss /= len(testloader.dataset)
        accuracy = metric.compute()["accuracy"]
        return loss, accuracy
    

   
    # @staticmethod
    # def load_data():
    #     cur = os.environ.get("TRAIN_SET") or ""
    #     trainset = load_from_disk(f"./data/imagenet/train{cur}").with_transform(
    #         apply_transforms
    #     )
    #     testset = load_from_disk("./data/imagenet/test").with_transform(
    #         apply_transforms
    #     )
    #     return DataLoader(trainset, batch_size=64, shuffle=True), DataLoader(
    #         testset, batch_size=64
    #     )

    # @staticmethod
    # def get_testset():
    #     testset = load_from_disk("./data/imagenet/test").with_transform(
    #         apply_transforms
    #     )
    #     return testset
    
    @staticmethod
    def load_data():
        """Load IMDB data (training and eval)"""
        # raw_datasets = load_dataset("imdb")
        cur = os.environ.get("TRAIN_SET") or ""

        raw_datasets = raw_datasets.shuffle(seed=42)

        del raw_datasets["unsupervised"]

        tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)

        def tokenize_function(examples):
            return tokenizer(examples["text"], truncation=True)

        # train_population = random.sample(range(len(raw_datasets["train"])), 100)
        # test_population = random.sample(range(len(raw_datasets["test"])), 100)

        tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
        # tokenized_datasets["train"] = tokenized_datasets["train"].select(train_population)
        # tokenized_datasets["test"] = tokenized_datasets["test"].select(test_population)
        tokenized_datasets = tokenized_datasets.remove_columns("text")
        tokenized_datasets = tokenized_datasets.rename_column("label", "labels")

        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
        trainloader = DataLoader(
            tokenized_datasets["train"],
            shuffle=True,
            batch_size=32,
            collate_fn=data_collator,
        )

        testloader = DataLoader(
            tokenized_datasets["test"], batch_size=32, collate_fn=data_collator
        )

        return trainloader, testloader


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
