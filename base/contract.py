from web3 import Web3
from web3.eth import Contract
import json
import os


def create_reg_contract(w3: Web3, address: str) -> Contract:
    return w3.eth.contract(
        address=Web3.to_checksum_address(address),
        abi=json.load(
            open(
                str(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../blockchain/abi/Registration.json",
                    )
                )
            )
        ),
    )


def create_async_contract(w3: Web3, address: str) -> Contract:
    return w3.eth.contract(
        address=Web3.to_checksum_address(address),
        abi=json.load(
            open(
                str(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../blockchain/abi/AsyncRound.json",
                    )
                )
            )
        ),
    )


def create_sync_contract(w3: Web3, address: str) -> Contract:
    return w3.eth.contract(
        address=Web3.to_checksum_address(address),
        abi=json.load(
            open(
                str(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../../blockchain/abi/SyncRound.json",
                    )
                )
            )
        ),
    )
