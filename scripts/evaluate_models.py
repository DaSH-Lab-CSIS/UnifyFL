import os
from torch.utils.data import DataLoader
import csv
import torch
import csv
import sys
from models.cifar import CIFAR10Model

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model=CIFAR10Model().to(DEVICE)
local_records=[]
global_records=[]

def list_files(dir_path):
    res = []
    try:
        for file_path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file_path)):
                res.append(file_path)
    except FileNotFoundError:
        print(f"The directory {dir_path} does not exist")
    except PermissionError:
        print(f"Permission denied to access the directory {dir_path}")
    except OSError as e:
        print(f"An OS error occurred: {e}")
    return res

files = sorted(list_files(sys.argv[1]))
testset = model.get_testset()
testloader = DataLoader(testset, batch_size=32)
for i in files:
    model.load_state_dict(torch.load(f"{sys.argv[1]}/{i}"))
    accuracy, loss = model.test_model(testloader)
    if i.split("-")[-1]=="local.pt":
        local_records.append([i[0],"-".join(i[0:5]),accuracy,loss])
    else:
        global_records.append([i[0],"-".join(i[0:5]),accuracy,loss])

file1=sys.argv[2]+"_local.csv"
file2=sys.argv[2]+"_global.csv"
with open(file1, 'a+') as csvfile:  
    csvwriter = csv.writer(csvfile)  
    csvwriter.writerows(local_records)
with open(file2, 'a+') as csvfile:  
    csvwriter = csv.writer(csvfile)  
    csvwriter.writerows(global_records) 




