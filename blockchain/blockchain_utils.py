import json
from web3 import Web3

GANACHE_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))


def get_contract():
    with open("blockchain/contract_address.txt", "r") as f:
        contract_address = f.read().strip()

    with open("blockchain/abi/ProductTraceability.json", "r") as f:
        abi = json.load(f)

    return w3.eth.contract(address=contract_address, abi=abi)


def get_default_sender():
    accounts = w3.eth.accounts
    if not accounts:
        raise Exception("No Ganache accounts found")
    return accounts[0]


def get_product_count():
    contract = get_contract()
    return contract.functions.productCount().call()


def create_product_on_blockchain(crop_name, quantity, location, harvest_date, price):
    contract = get_contract()
    sender = get_default_sender()

    tx_hash = contract.functions.createProduct(
        crop_name,
        quantity,
        location,
        harvest_date,
        price
    ).transact({
        "from": sender,
        "gas": 3000000
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # After product creation, read the latest blockchain product count
    blockchain_product_id = contract.functions.productCount().call()

    return {
        "receipt": receipt,
        "blockchain_product_id": blockchain_product_id
    }


def update_product_status_on_blockchain(blockchain_product_id, new_status):
    contract = get_contract()
    sender = get_default_sender()

    tx_hash = contract.functions.updateStatus(
        blockchain_product_id,
        new_status
    ).transact({
        "from": sender,
        "gas": 3000000
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt


def get_product_from_blockchain(blockchain_product_id):
    contract = get_contract()
    return contract.functions.getProduct(blockchain_product_id).call()