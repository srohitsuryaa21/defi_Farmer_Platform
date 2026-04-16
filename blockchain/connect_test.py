import json
from web3 import Web3

# -------------------------
# Connect to Ganache
# -------------------------
GANACHE_URL = "http://127.0.0.1:7545"
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    print("Failed to connect to Ganache")
    exit()

print("Connected to Ganache")


# -------------------------
# Load Contract Address
# -------------------------
with open("blockchain/contract_address.txt", "r") as f:
    contract_address = f.read().strip()

print("Contract Address:", contract_address)


# -------------------------
# Load ABI
# -------------------------
with open("blockchain/abi/ProductTraceability.json", "r") as f:
    abi = json.load(f)


# -------------------------
# Load Contract
# -------------------------
contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

print("Contract loaded successfully")


# -------------------------
# Read productCount
# -------------------------
count = contract.functions.productCount().call()

print("Current product count on blockchain:", count)