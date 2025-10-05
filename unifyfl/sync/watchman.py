import json
import logging
from operator import itemgetter
import os
import time

from web3 import Web3
from web3.middleware import geth_poa_middleware
import sys


from unifyfl.base.contract import create_sync_contract

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(levelname)s:     %(message)s - %(asctime)s",
)
logger = logging.getLogger(__name__)

with open(sys.argv[1]) as f:
    config = json.load(f)
    (endpoint, sync_contract_address, account, timeout) = itemgetter(
        "geth_endpoint",
        "contract_address",
        "geth_account",
        "timeout",
    )(config)

w3 = Web3(Web3.HTTPProvider(endpoint))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
w3.eth.default_account = account


sync_contract = create_sync_contract(w3, sync_contract_address)


def main():
    # timer for test bed to start
    # time.sleep(40)
    while True:
        logging.info("Starting training")
        sync_contract.functions.startTraining().transact()
        # timeout for training
        time.sleep(timeout + 20)
        logging.info("Starting scoring")
        sync_contract.functions.startScoring().transact()
        # time needed to score
        time.sleep(timeout / 4 + 10)


if __name__ == "__main__":
    main()
