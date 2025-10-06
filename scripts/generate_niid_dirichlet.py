import os
import argparse
import random
import numpy as np
import torch
from torchvision.datasets import ImageFolder
from torchvision.transforms import Compose, Normalize, ToTensor
from torch.utils.data import DataLoader
from tqdm import trange

random.seed(42)
np.random.seed(42)


def rearrange_data_by_class(data, targets, n_class):
    new_data = []
    for i in trange(n_class, desc="Rearranging by class"):
        idx = targets == i
        new_data.append(data[idx])
    return new_data


def get_dataset(mode="train", folder='./data/cifar10'):
    trf = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    dataset = ImageFolder(f"{folder}/{mode}", transform=trf)
    n_sample = len(dataset.samples)
    SRC_N_CLASS = len(dataset.classes)

    loader = DataLoader(dataset, batch_size=n_sample, shuffle=False)

    print(f"Loading {mode} data from storage ...")
    for _, xy in enumerate(loader, 0):
        dataset.data, dataset.targets = xy

    data_by_class = rearrange_data_by_class(
        dataset.data.cpu().detach().numpy(),
        dataset.targets.cpu().detach().numpy(),
        SRC_N_CLASS,
    )
    print(
        f"{mode.upper()} SET: Total #samples: {n_sample}. Example sample: {dataset.samples[0]}"
    )
    print("  #samples per class:\n", [len(v) for v in data_by_class])

    return data_by_class, n_sample, SRC_N_CLASS


def devide_train_data(data, n_sample, SRC_CLASSES, NUM_USERS, min_sample, alpha=0.5, sampling_ratio=0.5):
    min_size = 0
    while min_size < min_sample:
        print("Trying Dirichlet split...")
        idx_batch = [{} for _ in range(NUM_USERS)]
        samples_per_user = [0 for _ in range(NUM_USERS)]
        max_samples_per_user = sampling_ratio * n_sample / NUM_USERS
        for l in SRC_CLASSES:
            idx_l = [i for i in range(len(data[l]))]
            np.random.shuffle(idx_l)
            if sampling_ratio < 1:
                samples_for_l = int(
                    min(max_samples_per_user, int(sampling_ratio * len(data[l])))
                )
                idx_l = idx_l[:samples_for_l]
            proportions = np.random.dirichlet(np.repeat(alpha, NUM_USERS))
            proportions = np.array(
                [
                    p * (n_per_user < max_samples_per_user)
                    for p, n_per_user in zip(proportions, samples_per_user)
                ]
            )
            proportions = proportions / proportions.sum()
            proportions = (np.cumsum(proportions) * len(idx_l)).astype(int)[:-1]
            for u, new_idx in enumerate(np.split(idx_l, proportions)):
                idx_batch[u][l] = new_idx.tolist()
                samples_per_user[u] += len(idx_batch[u][l])
        min_size = min(samples_per_user)

    X = [[] for _ in range(NUM_USERS)]
    y = [[] for _ in range(NUM_USERS)]
    Labels = [set() for _ in range(NUM_USERS)]
    print("Processing users...")
    for u, user_idx_batch in enumerate(idx_batch):
        for l, indices in user_idx_batch.items():
            if len(indices) == 0:
                continue
            X[u] += data[l][indices].tolist()
            y[u] += (l * np.ones(len(indices))).tolist()
            Labels[u].add(l)

    return X, y, Labels, idx_batch, samples_per_user


def divide_test_data(NUM_USERS, SRC_CLASSES, test_data, Labels, unknown_test):
    test_X = [[] for _ in range(NUM_USERS)]
    test_y = [[] for _ in range(NUM_USERS)]
    idx = {l: 0 for l in SRC_CLASSES}
    for user in trange(NUM_USERS, desc="Splitting test data"):
        if unknown_test:
            user_sampled_labels = SRC_CLASSES
        else:
            user_sampled_labels = list(Labels[user])
        for l in user_sampled_labels:
            num_samples = int(len(test_data[l]) / NUM_USERS)
            test_X[user] += test_data[l][idx[l]: idx[l] + num_samples].tolist()
            test_y[user] += (l * np.ones(num_samples)).tolist()
            idx[l] += num_samples
    return test_X, test_y


def save_client_data(output_dir, mode, client_id, x_data, y_data):
    """Save each client's data to OUTPUT/train{client_id} or OUTPUT/test{client_id} in Hugging Face format"""
    from datasets import Dataset, Features, Array3D, ClassLabel
    
    if mode == "train":
        client_dir = os.path.join(output_dir, f"train{client_id}")
    else:
        client_dir = os.path.join(output_dir, f"test{client_id}")

    os.makedirs(client_dir, exist_ok=True)

    # Convert to numpy arrays
    x_array = np.array(x_data, dtype=np.float32)
    y_array = np.array(y_data, dtype=np.int64)
    
    # Create Hugging Face dataset
    dataset_dict = {
        "image": x_array,
        "label": y_array
    }
    
    # Define features
    features = Features({
        "image": Array3D(shape=(3, 32, 32), dtype="float32"),
        "label": ClassLabel(num_classes=10)
    })
    
    dataset = Dataset.from_dict(dataset_dict, features=features)
    
    # Save in Hugging Face format
    dataset.save_to_disk(client_dir)
    print(f"Saved {mode} data for client {client_id} -> {client_dir} (HF format)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_user", type=int, default=12, help="number of local clients")
    parser.add_argument("--n_class", type=int, default=10, help="number of classes")
    parser.add_argument("--min_sample", type=int, default=10, help="Min samples per client")
    parser.add_argument("--sampling_ratio", type=float, default=0.05, help="Sampling ratio")
    parser.add_argument("--alpha", type=float, default=0.5, help="Dirichlet alpha")
    parser.add_argument("--unknown_test", type=int, default=0, help="Allow unseen test labels per user")
    parser.add_argument("--dataset", type=str, default="data/cifar10", help="source dataset")
    parser.add_argument("--output", type=str, default="data/cifar10_split", help="output folder")
    args = parser.parse_args()

    print(f"Preparing CIFAR10 for {args.n_user} clients. Output -> {args.output}")

    train_data, n_train_sample, SRC_N_CLASS = get_dataset("train", args.dataset)
    test_data, n_test_sample, SRC_N_CLASS = get_dataset("test", args.dataset)
    SRC_CLASSES = list(range(SRC_N_CLASS))

    train_X, train_y, Labels, idx_batch, samples_per_user = devide_train_data(
        train_data, n_train_sample, SRC_CLASSES, args.n_user, args.min_sample, args.alpha, args.sampling_ratio
    )
    test_X, test_y = divide_test_data(args.n_user, SRC_CLASSES, test_data, Labels, args.unknown_test)

    # Save training data for each client
    for u in range(args.n_user):
        save_client_data(args.output, "train", u, train_X[u], train_y[u])

    # Save test data for each client
    for u in range(args.n_user):
        save_client_data(args.output, "test", u, test_X[u], test_y[u])

    print("✅ Finished preparing client datasets.")


if __name__ == "__main__":
    main()