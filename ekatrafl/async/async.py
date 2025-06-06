"""Async EkatraFl server implementation."""
from collections import OrderedDict
import json
from operator import itemgetter

from ekatrafl.base.policies import pick_selected_model
from flwr.common import parameters_to_ndarrays, ndarrays_to_parameters

from datetime import datetime
import logging
import sys
import asyncio

from web3 import Web3
from time import sleep

# import wandb
from ekatrafl.base.contract import create_reg_contract, create_async_contract
from ekatrafl.base.custom_server import Server

from ekatrafl.base.ipfs import load_models, save_model_ipfs
import flwr as fl
from flwr.server.strategy.aggregate import aggregate
from ekatrafl.base.model import models
import torch
import os

# wandb.login()

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
)
logger = logging.getLogger(__name__)

with open(sys.argv[1]) as f:
    config = json.load(f)
    (
        workload,
        geth_endpoint,
        geth_account,
        registration_contract_address,
        async_contract_address,
        flwr_min_fit_clients,
        flwr_min_available_clients,
        flwr_min_evaluate_clients,
        flwr_server_address,
        ipfs_host,
        aggregation_policy,
        scoring_policy,
        k,
        experiment_id,
        strategy,
    ) = itemgetter(
        "workload",
        "geth_endpoint",
        "geth_account",
        "registration_contract_address",
        "contract_address",
        "flwr_min_fit_clients",
        "flwr_min_available_clients",
        "flwr_min_evaluate_clients",
        "flwr_server_address",
        "ipfs_host",
        "aggregation_policy",
        "scoring_policy",
        "k",
        "experiment_id",
        "strategy",
    )(
        config
    )

model = models[workload]


if strategy == "fedyogi":
    from ekatrafl.base.strategy import FedYogiAggregate

    initial_model = model()

    aggregator = FedYogiAggregate(
        initial_parameters=ndarrays_to_parameters(
            [val.cpu().numpy() for _, val in initial_model.state_dict().items()]
        )
    )
# DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def set_weights(model, parameters):
    keys = [k for k in model.state_dict().keys() if "bn" not in k]
    params_dict = zip(keys, parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    model.load_state_dict(state_dict, strict=False)


w3 = Web3(Web3.HTTPProvider(geth_endpoint))

# Add this line when changing from anvil to geth chain
if os.getenv("GETH_POA"):
    from web3.middleware import geth_poa_middleware

    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = geth_account

registration_contract = create_reg_contract(w3, registration_contract_address)
# TODO: Add registration
async_contract = create_async_contract(w3, async_contract_address)


time_start = str(datetime.now().strftime("%d-%H-%M-%S"))
os.makedirs(f"save/async/{workload}/{experiment_id}", exist_ok=True)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


# def evaluate(
#     server_round: int, parameters: fl.common.NDArrays, config: Dict[str, Scalar]
# ) -> Optional[Tuple[float, Dict[str, Scalar]]]:
#     model_instance = model()
#     set_weights(model, parameters)
#     model.to(DEVICE)
#
#     loss, accuracy = model_instance.test(testloader, device=DEVICE)
#     print(loss, accuracy)
#     return loss, {"accuracy": accuracy}


class AsyncServer(Server):
    """Async server implementation.
    Warning: Server is a subclass of fl.server.Server, setting properties that
    are common to fl.server.Server might lead to unexpected behaviour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.round_ongoing = False
        self.round_id = 0
        self.cid = None
        self.model = model()
        registration_contract.functions.registerNode("trainer").transact()
        # threading.Thread(target=self.run_rounds).start()
        self.single_round()

    def set_parameters(self, parameters):
        print("set param", len(parameters))
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(
            state_dict,
        )

    # run_rounds not needed as we can just start another round after previous round ends
    # def run_rounds(self):
    #     # Rounds in async start automatically after the previous round ends
    #     time.sleep(60)
    #     while True:
    #         logger.info(f"Round {self.round_id} started")
    #         self.single_round()
    #         logger.info(f"Round {self.round_id-1} ended")
    #         time.sleep(60)

    def aggregate_models(self):
        global_models = list(
            filter(
                lambda x: x[0] != "",
                zip(*async_contract.functions.getLatestModelsWithScores().call()),
            )
        )
        if (len(list(global_models))) == 0:
            print(f"no global models - {self.round_id}")
            return
        selected_models = pick_selected_model(
            global_models, aggregation_policy, scoring_policy, int(k), self.cid
        )

        if len(selected_models) > 0:
            logger.info(f"Aggregating models {selected_models}")
            # models = list(
            #     map(
            #         parameters_to_ndarrays,
            #         loop.run_until_complete(load_models(selected_models, ipfs_host)),
            #     )
            # )
            state_dicts = loop.run_until_complete(
                load_models(selected_models, ipfs_host)
            )
            param_list = list(
                map(
                    ndarrays_to_parameters,
                    [
                        [val.cpu().numpy() for _, val in state_dict.items()]
                        for state_dict in state_dicts
                    ],
                )
            )
            # for param in param_list:
            #     print(type(param), "param")
            models = list(map(parameters_to_ndarrays, param_list))
            # for model in models:
            #     print(type(model), "model")

            # TODO: we are giving equal weightage for model aggregation
            # print(models, "models")
            models = list(zip(models, [1] * len(models)))
            # print(models, "models")
            if strategy == "fedyogi":
                weight_arrays = aggregate(models)
                weight_arrays = aggregator.aggregate(weight_arrays)
            else:
                weight_arrays = aggregate(models)
            # print(weight_arrays, "weight arrays")

            self.set_parameters(weight_arrays)
            self.server.parameters = ndarrays_to_parameters(weight_arrays)

            cur_time = str(datetime.now().strftime("%d-%H-%M-%S"))
            torch.save(
                self.model.state_dict(),
                f"save/async/{workload}/{experiment_id}/{self.round_id:02d}-{cur_time}-global.pt",
            )
        else:
            print(f"not aggregating {self.round_id}")

    def single_round(self):
        self.round_id += 1
        self.aggregate_models()
        self.round_ongoing = True
        if self.round_id >= 100:
            # wandb.finish()
            exit()
        logger.info(f"Round {self.round_id} started")
        parameters = self.start_round()

        if parameters is None:
            print("Error")
            return
        parameters = parameters[0]
        weights = parameters_to_ndarrays(parameters)
        self.set_parameters(weights)
        self.round_ongoing = False
        cur_time = str(datetime.now().strftime("%d-%H-%M-%S"))
        # TODO: add host to save path
        torch.save(
            self.model.state_dict(),
            f"save/async/{workload}/{experiment_id}/{self.round_id:02d}-{cur_time}-local.pt",
        )

        cid = asyncio.run(save_model_ipfs(self.model.state_dict(), ipfs_host))
        logger.info(f"Model saved to IPFS with CID: {cid}")
        self.cid = cid
        while True:
            try:
                async_contract.functions.submitModel(cid).transact()
                break
            except:
                sleep(5)
                continue
        logger.info("Model submitted to contarct")
        logger.info(f"Round {self.round_id} ended")
        sleep(15)
        self.single_round()


# Define strategy
if strategy == "fedavg":
    strategy = fl.server.strategy.FedAvg(
        min_fit_clients=flwr_min_fit_clients,
        min_available_clients=flwr_min_available_clients,
        min_evaluate_clients=flwr_min_evaluate_clients,
    )
elif strategy == "fedyogi":
    strategy = fl.server.strategy.FedYogi(
        initial_parameters=ndarrays_to_parameters(
            [val.cpu().numpy() for _, val in initial_model.state_dict().items()]
        ),
        min_fit_clients=flwr_min_fit_clients,
        min_available_clients=flwr_min_available_clients,
        min_evaluate_clients=flwr_min_evaluate_clients,
    )
else:  # aggregation_policy == "fedopt"
    strategy = fl.server.strategy.FedAvg(
        min_fit_clients=flwr_min_fit_clients,
        min_available_clients=flwr_min_available_clients,
        min_evaluate_clients=flwr_min_evaluate_clients,
    )


def main():
    """Start server and train model."""
    # wandb.init(
    #     project="ekatrafl",
    #     config={
    #         "workload": "cifar10",
    #         "aggregation_policy": aggregation_policy,
    #         "scoring_policy": scoring_policy,
    #         "k": k,
    #     },
    #     group=experiment_id,
    #     name=f"{socket.gethostname() if socket.gethostname() != 'raspberrypi' else getpass.getuser()}-async-agg",
    # )
    AsyncServer(server_address=flwr_server_address, strategy=strategy)


if __name__ == "__main__":
    main()
