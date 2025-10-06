import os
import argparse
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets import CIFAR10
import urllib.request
import zipfile
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import shutil

def save_cifar10_as_imagefolder(data_dir='./data'):
    """Download CIFAR-10 and save in ImageFolder format"""
    print("Downloading and converting CIFAR-10 to ImageFolder format...")
    return
    # Create temporary download directory
    temp_dir = os.path.join(data_dir, 'cifar10_temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Download datasets
    train_dataset = CIFAR10(root=temp_dir, train=True, download=True, transform=None)
    test_dataset = CIFAR10(root=temp_dir, train=False, download=True, transform=None)
    
    # Create ImageFolder structure
    train_dir = os.path.join(data_dir, 'cifar10', 'train')
    test_dir = os.path.join(data_dir, 'cifar10', 'test')
    
    # Create class directories
    for class_name in train_dataset.classes:
        os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
        os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)
    
    # Save training images
    print("Saving training images...")
    for idx, (img, label) in enumerate(tqdm(train_dataset, desc="Train")):
        class_name = train_dataset.classes[label]
        img_path = os.path.join(train_dir, class_name, f'{idx:05d}.png')
        img.save(img_path)
    
    # Save test images
    print("Saving test images...")
    for idx, (img, label) in enumerate(tqdm(test_dataset, desc="Test")):
        class_name = test_dataset.classes[label]
        img_path = os.path.join(test_dir, class_name, f'{idx:05d}.png')
        img.save(img_path)
    
    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    
    print(f"✓ CIFAR-10 saved in ImageFolder format!")
    print(f"  Training directory: {os.path.abspath(train_dir)}")
    print(f"  Test directory: {os.path.abspath(test_dir)}")
    print(f"  Training samples: {len(train_dataset)}")
    print(f"  Test samples: {len(test_dataset)}")
    print(f"  Classes: {train_dataset.classes}")
    
    return train_dir, test_dir

def save_tiny_imagenet_as_imagefolder(data_dir='./data'):
    """Download Tiny ImageNet and organize in standard ImageFolder format"""
    print("Downloading and organizing Tiny ImageNet...")
    
    tiny_imagenet_url = 'http://cs231n.stanford.edu/tiny-imagenet-200.zip'
    zip_path = os.path.join(data_dir, 'tiny-imagenet-200.zip')
    extract_path = os.path.join(data_dir, 'tiny-imagenet-200')
    imagefolder_path = os.path.join(data_dir, 'imagenet')
    
    # Check if already processed
    if os.path.exists(imagefolder_path):
        print(f"✓ Tiny ImageNet ImageFolder already exists at {os.path.abspath(imagefolder_path)}")
        return imagefolder_path
    
    # Download if not exists
    if not os.path.exists(extract_path):
        print("Downloading... (this may take a few minutes)")
        try:
            urllib.request.urlretrieve(tiny_imagenet_url, zip_path)
            print("✓ Download complete!")
        except Exception as e:
            print(f"✗ Error downloading: {e}")
            return None
        
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        os.remove(zip_path)
        print("✓ Extraction complete!")
    
    # Create ImageFolder structure
    train_src = os.path.join(extract_path, 'train')
    val_src = os.path.join(extract_path, 'val')
    
    train_dst = os.path.join(imagefolder_path, 'train')
    val_dst = os.path.join(imagefolder_path, 'test')
    
    # Copy training data (already in ImageFolder format)
    print("Organizing training data...")
    shutil.copytree(train_src, train_dst)
    
    # Reorganize validation data into ImageFolder format
    print("Reorganizing validation data...")
    os.makedirs(val_dst, exist_ok=True)
    
    # Read validation annotations
    val_annotations_file = os.path.join(val_src, 'val_annotations.txt')
    val_img_to_class = {}
    
    with open(val_annotations_file, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            img_name = parts[0]
            class_id = parts[1]
            val_img_to_class[img_name] = class_id
    
    # Create class directories and move images
    val_images_dir = os.path.join(val_src, 'images')
    for img_name, class_id in tqdm(val_img_to_class.items(), desc="Val"):
        class_dir = os.path.join(val_dst, class_id)
        os.makedirs(class_dir, exist_ok=True)
        
        src_img = os.path.join(val_images_dir, img_name)
        dst_img = os.path.join(class_dir, img_name)
        
        if os.path.exists(src_img):
            shutil.copy2(src_img, dst_img)
    
    print(f"✓ Tiny ImageNet saved in ImageFolder format!")
    print(f"  Training directory: {os.path.abspath(train_dst)}")
    print(f"  Test directory: {os.path.abspath(val_dst)}")
    print(f"  Training samples: 100,000 (500 per class)")
    print(f"  Test samples: 10,000 (50 per class)")
    print(f"  Classes: 200")
    print(f"  Image size: 64x64")
    
    return imagefolder_path

def main():
    parser = argparse.ArgumentParser(
        description='Download and save datasets in ImageFolder format'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['cifar10', 'tiny-imagenet', 'both'],
        default='cifar10',
        help='Dataset to download (cifar10, tiny-imagenet, or both)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='./data',
        help='Directory to save the dataset (default: ./data)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Dataset Downloader - ImageFolder Format")
    print("=" * 60)
    
    if args.dataset == 'cifar10' or args.dataset == 'both':
        print("\n[1/{}] CIFAR-10".format(2 if args.dataset == 'both' else 1))
        print("-" * 60)
        save_cifar10_as_imagefolder(args.data_dir)
    
    if args.dataset == 'tiny-imagenet' or args.dataset == 'both':
        print("\n[{}/{}] Tiny ImageNet".format(
            2 if args.dataset == 'both' else 1,
            2 if args.dataset == 'both' else 1
        ))
        print("-" * 60)
        save_tiny_imagenet_as_imagefolder(args.data_dir)
    
    print("\n" + "=" * 60)
    print("✓ All datasets saved in ImageFolder format!")
    print("\nYou can now load them with:")
    print("  from torchvision.datasets import ImageFolder")
    print("  dataset = ImageFolder('path/to/train')")
    print("=" * 60)

if __name__ == '__main__':
    main()