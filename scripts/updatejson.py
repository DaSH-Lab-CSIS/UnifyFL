# To be run from home, on all the aggregators
import json, sys

registration = sys.argv[1]
name = sys.argv[2]
files = ["agg.config.json"]
import os

os.chdir(f"EkatraFL/configs/{sys.argv[3]}")
for i in files:
    with open(i, "r") as jsonFile:
        data = json.load(jsonFile)
        data["registration_contract_address"] = registration
        data[f"contract_address"] = name
    with open(i, "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)
    print(f"Updated {i} with {registration} and {name}")
