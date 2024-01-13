"""Sync EkatraFl server implementation."""
from collections import OrderedDict
import json
from operator import itemgetter
from time import sleep
from ekatrafl.base.policies import pick_selected_model
from flwr.common import NDArray, parameters_to_ndarrays

from datetime import datetime
import logging
import sys
import asyncio

from web3 import Web3
from web3.middleware import geth_poa_middleware
from ekatrafl.base.contract import create_reg_contract, create_sync_contract
from ekatrafl.base.custom_server import Server

from ekatrafl.base.ipfs import load_models, save_model_ipfs
import flwr as fl
from flwr.server.strategy.aggregate import aggregate
from ekatrafl.base.model import models
import torch
import os

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
        sync_contract_address,
        flwr_min_fit_clients,
        flwr_min_available_clients,
        flwr_min_evaluate_clients,
        flwr_server_address,
        ipfs_host,
        aggregation_policy,
        scoring_policy,
        k
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
        "k"
    )(
        config
    )


model = models[workload]

trainloader, testloader = model.load_data()

# DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


w3 = Web3(Web3.HTTPProvider(geth_endpoint))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = geth_account

registration_contract = create_reg_contract(w3, registration_contract_address)
# TODO: Add registration
sync_contract = create_sync_contract(w3, sync_contract_address)


time_start = str(datetime.now().strftime("%d-%H-%M-%S"))
os.makedirs(f"save/sync/{workload}/{time_start}", exist_ok=True)
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


class SyncServer(Server):
    """Sync server implementation.
    Warning: Server is a subclass of fl.server.Server, setting properties that
    are common to fl.server.Server might lead to unexpected behaviour.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.round_ongoing = False
        self.model = model()
        self.round_id = 0
        registration_contract.functions.registerNode("trainer").transact()
        # self.single_round()
        # removed threading
        self.run_rounds()

    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def run_rounds(self):
        events = set()
        last_seen_block = w3.eth.block_number
        print("started run rounds")
        # TODO: remove threading and integrate into single_round
        while True:
            for event in sync_contract.events.StartTraining().get_logs(
                fromBlock=last_seen_block
            ):
                if event not in events:
                    events.add(event)
                    last_seen_block = event["blockNumber"]
                    if not self.round_ongoing:
                        self.round_id = event["args"]["round"]
                        self.single_round()
            sleep(1)

    def aggregate_models(self):
        global_models = filter(
            lambda x: x[0] != "",
            zip(*sync_contract.functions.getLatestModelsWithScores().call()),
        )
        
        selected_models = pick_selected_model(global_models, aggregation_policy, scoring_policy, int(k))


        if len(selected_models) > 0:
            logger.info(f"Aggregating models {selected_models}")

            param_list = loop.run_until_complete(
                load_models(selected_models, ipfs_host)
            )
            models = list(map(parameters_to_ndarrays, param_list))
            # TODO: we are giving equal weightage for model aggregation
            models = list(zip(models, [1] * len(models)))
            weight_arrays = aggregate(models)

            self.set_parameters(weight_arrays)

            cur_time = str(datetime.now().strftime("%d-%H-%M-%S") + ".pt")
            # TODO: add host to save path
            torch.save(
                self.model.state_dict(),
                f"save/sync/{workload}/{time_start}/{self.round_id:02d}-{cur_time}-global.pt",
            )

    def single_round(self):
        self.aggregate_models()
        self.round_ongoing = True
        logger.info(f"Round {self.round_id} started")
        parameters = self.start_round()

        if parameters is None:
            print("Error")
            return
        weights = parameters_to_ndarrays(parameters)
        self.set_parameters(weights)
        self.round_ongoing = False
        cur_time = str(datetime.now().strftime("%d-%H-%M-%S") + ".pt")
        # TODO: add host to save path
        torch.save(
            self.model.state_dict(),
            f"save/sync/{workload}/{time_start}/{self.round_id:02d}-{cur_time}-local.pt",
        )

        cid = asyncio.run(save_model_ipfs(parameters, ipfs_host))
        logger.info(f"Model saved to IPFS with CID: {cid}")
        sync_contract.functions.submitModel(cid).transact()
        logger.info("Model submitted to contarct")
        logger.info(f"Round {self.round_id} ended")


# Define strategy
strategy = fl.server.strategy.FedAvg(
    min_fit_clients=flwr_min_fit_clients,
    min_available_clients=flwr_min_available_clients,
    min_evaluate_clients=flwr_min_evaluate_clients,
)


def main():
    """Start server and train model."""
    SyncServer(server_address=flwr_server_address, strategy=strategy)


if __name__ == "__main__":
    main()
