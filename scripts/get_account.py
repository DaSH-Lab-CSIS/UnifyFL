# pip install web3
# Usage: python3 get_account.py <keystore_path> <password>
# Example: python3 get_account.py ~/bcfl-eth/node1/keystore/UTC--2020-11-08T16-29-37.000000000Z--c4a5c5b1f7f0e8f9a9d5e5b4b9c8b1b9e2b3b4b9b0b3b9b2b9b0b4 qwertyuiop


# Use in tmux_scripts/deploy_contract.py for private_key
import binascii
import sys
from web3.auto import w3

with open(sys.argv[1]) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, sys.argv[2])

print(binascii.b2a_hex(private_key))
