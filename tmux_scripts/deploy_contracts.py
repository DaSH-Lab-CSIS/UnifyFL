# To be run from the base folder, it moves into blockchain folder to run commands.
import subprocess, sys
import spur
import os
import uuid

# mode is 1 for sync, 2 for async
mode = sys.argv[1]
aggregation_policy = sys.argv[2]
scoring_policy = sys.argv[3]
k = sys.argv[4]
experiment_id = str(uuid.uuid4())
RPC_URL = "http://10.8.1.173:8547"
PRIVATE_KEY = "0xbec97322819fee49724622e4d6f5af2d7b16d42e4230f276747b1a1750e3a61a"
# os.chdir("contracts")
c1 = f"forge create --rpc-url {RPC_URL} --private-key {PRIVATE_KEY} contracts/Registration.sol:Registration"
command1 = c1.split()
c2 = f"forge create --rpc-url {RPC_URL} --private-key {PRIVATE_KEY}  contracts/RandomNumbers.sol:RandomNumbers"
command2 = c2.split()

print(c1)
output1 = subprocess.Popen(command1, stdout=subprocess.PIPE).communicate()[-2]
print(output1.decode())
registration = output1.decode().split("\n")


registration = registration[-3].split()[-1]
print("reg", registration)

output2 = subprocess.Popen(command2, stdout=subprocess.PIPE).communicate()[-2]
random_numbers = output2.decode().split("\n")[-3].split()[-1]

if mode == "1":
    c3 = (
        f"forge create --rpc-url {RPC_URL} --private-key {PRIVATE_KEY} contracts/AsyncRound.sol:AsyncRound"
        + " --constructor-args "
        + random_numbers
        + " "
        + registration
    )
else:
    c3 = (
        f"forge create --rpc-url {RPC_URL} --private-key {PRIVATE_KEY} contracts/SyncRound.sol:SyncRound"
        + " --constructor-args "
        + random_numbers
        + " "
        + registration
    )
print(c3)
output3 = subprocess.Popen(c3.split(), stdout=subprocess.PIPE).communicate()[-2]
sync = output3.decode().split("\n")[-3].split()[-1]
print(output3.decode(), sync)
os.chdir("..")
com2 = f"python3 EkatraFL/tmux_scripts/updatejson.py {registration} {sync} {'a' if mode=='1' else ''}sync {aggregation_policy} {scoring_policy} {k} {experiment_id}"
print(com2)
print(subprocess.Popen(com2.split(), stdout=subprocess.PIPE).communicate()[0])
names = [("10.8.1.173", 22), ("10.8.1.175", 22), ("10.8.1.174", 22), ("10.8.1.17", 22)]
# if mode == "1":
#     c3 = (
#         "forge create --rpc-url {RPC_URL} --private-key 0x9b19a5202b4678b62adc4af295c791b74a04f1bced3f014772f82cd60f919989 src/SyncRound.sol:SyncRound"
#         + " --constructor-args "
#         + registration
#         + " "
#         + random_numbers
#     )
#     output3 = subprocess.Popen(c3.split(), stdout=subprocess.PIPE).communicate()[0]
#     sync = output3.decode().split("\n")[-3].split()[-1]
# elif mode == "2":
#     c3 = f"""forge create --rpc-url {RPC_URL} --private-key 0x9b19a5202b4678b62adc4af295c791b74a04f1bced3f014772f82cd60f919989 src/AsyncRound.sol:AsyncRound --constructor-args {registration} {random_numbers}"""
#     output3 = subprocess.Popen(c3.split(), stdout=subprocess.PIPE).communicate()[0]
#     sync = output3.decode().split("\n")[-3].split()[-1]
#
for i in names[1:]:
    shell = spur.SshShell(hostname=i[0], port=i[1], username="user", password="user123")
    result = shell.run("ls".split())
    # print(result.output)
    com2 = f"python3 EkatraFL/tmux_scripts/updatejson.py {registration} {sync} {'a' if mode=='1' else ''}sync {aggregation_policy} {scoring_policy} {k} {experiment_id}"
    print(com2)
    shell.run(com2.split())
    print(f"ran for {i}")
