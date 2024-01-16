import os
from torch.utils.data import DataLoader
import csv
import sys
import torch
import csv
from ..models.cifar import CIFAR10Model

model=CIFAR10Model.create_model()
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
testset = model.create_testset()
testloader = DataLoader(testset, batch_size=128)
for i in files:
    model.load_state_dict(torch.load(i))
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




