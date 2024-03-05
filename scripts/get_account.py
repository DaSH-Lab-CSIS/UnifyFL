# pip install web3
# Usage: python3 get_account.py <keystore_path> <password>
import binascii
import sys
from web3.auto import w3
with open(sys.argv[1]) as keyfile:
     encrypted_key = keyfile.read()
     private_key = w3.eth.account.decrypt(encrypted_key, sys.argv[2])

print(binascii.b2a_hex(private_key))
