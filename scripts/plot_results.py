import csv
from os import sep
import matplotlib as mpl
from matplotlib import markers
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import json

config_file = open("plot.json")
config = json.load(config_file)

accuracy_data = []
loss_data = []
time_setting = config["time_setting"]
type = config["type"]
if type == "round":
    n = len(config["lines"])
    # accuracy_data = [[]] * n
    # loss_data = [[]] * n
    for j, i in enumerate(config["lines"]):
        acc = []
        los = []
        line_name = i["name"]
        file = i["file"]
        with open(file, mode="r") as file:
            csvFile = csv.reader(file)
            for line in csvFile:
                round_id = int(line[0])
                accuracy = float(line[2])
                loss = float(line[3])
                acc.append([round_id, accuracy])
                los.append([round_id, loss])
        acc.sort(key=lambda x: x[0])
        los.sort(key=lambda x: x[0])
        accuracy_data.append(acc)
        loss_data.append(los)
    # else:
    #     n = len(config["lines"])
    #     accuracy_data = [[]] * n
    #     loss_data = [[]] * n
    #     j = 0
    #     for i in config["lines"]:
    #         line_name = i["name"]
    #         file = i["file"]
    #         with open(file, mode="r") as file:
    #             csvFile = csv.reader(file)
    #             for line in csvFile:
    #                 round_id = int(line[0])
    #                 accuracy = float(line[2])
    #                 loss = float(line[3])
    #                 accuracy_data[j].append([round_id, accuracy])
    #                 loss_data[j].append([round_id, loss])
    #         j += 1

elif type == "time":
    if time_setting == "":
        # zero each plot wrt its own start time
        n = len(config["lines"])
        j = 0
        for i in config["lines"]:
            acc = []
            los = []
            line_name = i["name"]
            file = i["file"]
            with open(file, mode="r") as file:
                csvFile = csv.reader(file)
                for line in csvFile:
                    zero_value = line[1]
                    break
                absolute_zero = time.mktime(time.strptime(zero_value, "%d-%H-%M-%S"))
                for line in csvFile:
                    round_id = line[0]
                    accuracy = float(line[2])
                    loss = float(line[3])
                    curr_time = time.mktime(time.strptime(line[1], "%d-%H-%M-%S"))
                    acc.append([curr_time - absolute_zero, accuracy])
                    los.append([curr_time - absolute_zero, loss])
            j += 1
            acc.sort(key=lambda x: x[0])
            los.sort(key=lambda x: x[0])
            accuracy_data.append(acc)
            loss_data.append(los)
    else:
        # plot wrt a common start time - specfified in config file
        n = len(config["lines"])
        file_name = time_setting
        with open(file_name, mode="r") as file:
            csvFile = csv.reader(file)
            for line in csvFile:
                zero_value = line[0]
                break
        absolute_zero = time.mktime(time.strptime(zero_value, "%d-%H-%M-%S"))
        j = 0
        for i in config["lines"]:
            acc = []
            los = []
            line_name = i["name"]
            file = i["file"]
            with open(file, mode="r") as file:
                csvFile = csv.reader(file)
                for line in csvFile:
                    round_id = line[0]
                    accuracy = float(line[2])
                    loss = float(line[3])
                    curr_time = time.mktime(time.strptime(line[1], "%d-%H-%M-%S"))
                    acc.append([float(curr_time - absolute_zero), float(accuracy)])
                    los.append([float(curr_time - absolute_zero), float(loss)])
            j += 1
            acc.sort(key=lambda x: x[0])
            los.sort(key=lambda x: x[0])
            accuracy_data.append(acc)
            loss_data.append(los)


fig, ax = plt.subplots()
ax.set_title(config["name"], fontsize="x-large", fontstyle="oblique")

ax.set_ylabel("% Accuracy", fontsize="large")
ax.set_xlabel(config["type"], fontsize="large")

# ax2 = ax.twinx()
# ax2.set_ylabel("Loss", fontsize="large")
# ax2.set_ylim(0, 2.5)

for i in range(len(config["lines"])):
    print(*accuracy_data[i], i, sep="\n")
    # print(*loss_data[i], i, sep="\n")
    ax.plot(
        [x[0] for x in accuracy_data[i]],
        [x[1] for x in accuracy_data[i]],
        label=config["lines"][i]["name"] + " accuracy",
    )
    # ax2.plot(
    #     [x[0] for x in loss_data[i]],
    #     [x[1] for x in loss_data[i]],
    #     label=config["lines"][i]["name"] + " loss",
    # )

# data1 = np.array(local_data[0])
# x1, y1 = data1.T
# ax.plot(x1, y1, **{"marker": "o"}, label="Local Aggregate 1")
# plt.xticks(default_x_ticks, x_values)

plt.grid()
# plt.legend()
# fig.tight_layout()
plt.show()
plt.savefig(config["name"] + ".png")
