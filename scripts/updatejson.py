# To be run from home, on all the aggregators
import os
import json
import sys

registration = sys.argv[1]
name = sys.argv[2]
aggregation_policy = sys.argv[3]
scoring_policy = sys.argv[4]
k = sys.argv[5]
files = ["agg.config.json"]

os.chdir(f"EkatraFL/configs/{sys.argv[3]}")
for i in files:
    with open(i, "r") as jsonFile:
        data = json.load(jsonFile)
        data["registration_contract_address"] = registration
        data["contract_address"] = name
        data["aggregation_policy"] = aggregation_policy
        data["scoring_policy"] = scoring_policy
        data["k"] = k
    with open(i, "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)
    print(f"Updated {i} with {registration} and {name}")
