import csv
import matplotlib.pyplot as plt
import time
import json
import sys

config_file = sys.argv[1]
config = json.load(config_file)

accuracy_data = []
loss_data = []
time_setting = config["time_setting"]
type = config["type"]
max_acc = 0
max_loss = 0
min_acc = 100
min_loss = 100
MAX_ROUND = 100
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
        absolute_zero = time.mktime(time.strptime(csvFile.__next__()[1], "%d-%H-%M-%S"))
        for line in csvFile:
            round_id = int(line[0])
            if round_id > MAX_ROUND:
                # if j != 0:
                #     continue
                # else:
                #     if round_id > 75:
                continue
            accuracy = float(line[2])
            loss = float(line[3])
            curr_time = time.mktime(time.strptime(line[1], "%d-%H-%M-%S"))
            acc.append([round_id, curr_time - absolute_zero, accuracy])
            los.append([round_id, curr_time - absolute_zero, loss])
    acc.sort(key=lambda x: x[2])
    max_acc = max(max_acc, acc[-1][2])
    min_acc = min(min_acc, acc[0][2])
    acc.sort(key=lambda x: x[0])
    los.sort(key=lambda x: x[2])
    max_loss = max(max_loss, los[-1][2])
    min_loss = min(min_loss, los[0][2])
    los.sort(key=lambda x: x[0])
    accuracy_data.append(acc)
    loss_data.append(los)


fig, ax = plt.subplots()
# fig.set_size_inches(6.2, 5.4)
plt.subplots_adjust(bottom=0.13, top=0.92, left=0.12, right=0.95)
# plt.tight_layout()
# print(plt.figure().get_size_inches())
# ax.set_title(config["name"], fontsize="xx-large", fontstyle="oblique")

if config["show_rounds"]:
    loop = acc if config["is_acc"] else los
    mini = min_acc if config["is_acc"] else min_loss
    maxi = max_acc if config["is_acc"] else max_loss
    multi = 0.055 if config["is_acc"] else 0.055
    ax.plot(
        [loop[0][1], loop[0][1]],
        [mini, maxi],
        color="blue",
        linestyle="--",
        dashes=(5, 15),
        lw=0.5,
        label="Rounds ($R_n$)",
    )
    plt.text(
        0,
        maxi + multi * maxi,
        "$R_{{" + str(0) + "}}$",
        fontsize="xx-large",
    )
    for round, time, ac in loop:
        # print(round)
        if not ((round) % 20):
            # print(ac, "hi")
            das = ax.plot(
                [time, time],
                [mini, maxi],
                color="blue",
                linestyle="--",
                dashes=(5, 15),
                lw=0.5,
            )
            plt.text(
                time - 50,
                maxi + multi * maxi,
                "$R_{{" + str(round) + "}}$",
                fontsize="xx-large",
            )

    # plt.xticks(np.arange(0, 1800, 500), fontsize="large")


ax.set_xlabel(config["type"].capitalize(), fontsize="xx-large")
# ax.xticks(fontsize="large")
ax.tick_params(axis="x", labelsize="xx-large")
ax.tick_params(axis="y", labelsize="xx-large")
if config["is_acc"]:
    ax.set_ylabel("% Accuracy", fontsize="xx-large")
    if config["twin"]:
        ax2 = ax.twinx()
        ax2.set_ylabel("Loss", fontsize="xx-large")

# ax2 = ax.twinx()
else:
    ax.set_ylabel("Loss", fontsize="xx-large")
    # ax.set_ylim(0, 2.5)

for i in range(len(config["lines"])):
    # print(*accuracy_data[i], i, sep="\n")
    # print(*loss_data[i], i, sep="\n")
    if config["is_acc"]:
        if config["type"] == "round":
            ax.plot(
                [x[0] for x in accuracy_data[i]],
                [x[2] for x in accuracy_data[i]],
                label=config["lines"][i]["name"],
                linestyle="dashed" if config["lines"][i].get("dotted") else "solid",
            )
            if config["twin"]:
                ax2.plot(
                    [x[0] for x in loss_data[i]],
                    [x[2] for x in loss_data[i]],
                    label=config["lines"][i]["name"],
                    linestyle="--",
                    dashes=(5, 10),
                )
        else:
            ax.plot(
                [x[1] for x in accuracy_data[i]],
                [x[2] for x in accuracy_data[i]],
                label=config["lines"][i]["name"],
                linestyle="dashed" if config["lines"][i].get("dotted") else "solid",
            )
            if config["twin"]:
                ax2.plot(
                    [x[1] for x in loss_data[i]],
                    [x[2] for x in loss_data[i]],
                    label=config["lines"][i]["name"],
                    linestyle="--",
                    dashes=(5, 10),
                )

    else:
        if config["type"] == "round":
            ax.plot(
                [x[0] for x in loss_data[i]],
                [x[2] for x in loss_data[i]],
                label=config["lines"][i]["name"],
            )
        else:
            ax.plot(
                [x[1] for x in loss_data[i]],
                [x[2] for x in loss_data[i]],
                label=config["lines"][i]["name"],
                linestyle="dashed" if config["lines"][i].get("dotted") else "solid",
            )

# data1 = np.array(local_data[0])
# x1, y1 = data1.T
# ax.plot(x1, y1, **{"marker": "o"}, label="Local Aggregate 1")
# plt.xticks(default_x_ticks, x_values)
print(min_acc, max_acc)

# print the last record in each plot
for i in range(len(config["lines"])):
    print(accuracy_data[i][-1])


plt.grid()
if config["legend"]:
    plt.legend(fontsize="x-large")
else:
    # remove legend
    plt.legend().remove()
# fig.tight_layout()
# plt.show()
if config["twin"]:
    name = "../middleware/final_PLEASE/" + config["name"] + "_twin.png"
else:
    name = (
        "../middleware/final_PLEASE/"
        + config["name"]
        + ("_acc" if config["is_acc"] else "_loss")
        + ".png"
    )
print("Saving to", name)
plt.savefig(name)
