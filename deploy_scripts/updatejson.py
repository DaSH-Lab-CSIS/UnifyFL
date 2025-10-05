# To be run from home, on all the aggregators
import os
import json
import sys


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
os.chdir("..")
print(os.getcwd())
registration = sys.argv[1]
name = sys.argv[2]
if len(sys.argv) > 6:
    aggregation_policy = sys.argv[4]
    scoring_policy = sys.argv[5]
    k = sys.argv[6]
    experiment_id = sys.argv[7]
else:
    experiment_id = sys.argv[4]
files = ["agg.config.json"]

os.chdir(f"configs/{sys.argv[3]}")
for i in files:
    with open(i, "r") as jsonFile:
        data = json.load(jsonFile)
        data["registration_contract_address"] = registration
        data["contract_address"] = name
        data["experiment_id"] = experiment_id
        if len(sys.argv) > 6:
            data["aggregation_policy"] = aggregation_policy
            data["scoring_policy"] = scoring_policy
            data["k"] = k
    with open(i, "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)
    print(f"Updated {i} with {registration} and {name}")
