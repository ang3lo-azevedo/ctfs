from web3 import Web3
from web3.datastructures import AttributeDict
from web3.middleware import SignAndSendRawMiddlewareBuilder
from hexbytes import HexBytes
import time
import json
import requests

NODE_URL = 'http://127.0.0.1:8545'
w3 = Web3(Web3.HTTPProvider(NODE_URL))

# get compiled DEX
with open('../eth/MiniDex.json') as f:
    json_obj = json.load(f)

DEX_ABI = json_obj['abi']
DEX_BYTECODE = json_obj['bytecode']['object']

# get compiled ERC20-Fixed
with open('../eth/ERC20Fixed.json') as f:
    json_obj = json.load(f)

ERC20_ABI = json_obj['abi']
ERC20_BYTECODE = json_obj['bytecode']['object']

def give_money(address):
    requests.post(
        NODE_URL,
        json.dumps({
            "method": "anvil_setBalance",
            "params": [address, "0x100_000_000_000_000_000"], # a lot of ETH, but we are trading fruits!
            "jsonrpc": "2.0",
            "id": 0
        }),
        headers={'content-type': 'application/json'}
    )

def gen_account():
    acc = w3.eth.account.create()
    w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acc), layer=0)
    give_money(acc.address)

    return acc

def deploy_erc(name, symbol):
    c = w3.eth.contract(abi=ERC20_ABI, bytecode=ERC20_BYTECODE)
    tx_hash = c.constructor(name, symbol).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt['contractAddress']

def deploy_dex(account, token1, amount1, token2, amount2):
    c = w3.eth.contract(abi=DEX_ABI, bytecode=DEX_BYTECODE)
    tx_hash = c.constructor(token1, token2).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # fill liquidity
    approve_erc(account, token1, tx_receipt['contractAddress'], amount1)
    approve_erc(account, token2, tx_receipt['contractAddress'], amount2)

    c = w3.eth.contract(tx_receipt['contractAddress'], abi=DEX_ABI)
    c.functions.addLiquidity(amount1, amount2).transact()
    
    return tx_receipt['contractAddress']

def transfer_erc(contract, to, amount):
    c = w3.eth.contract(contract, abi=ERC20_ABI)
    c.functions.transfer(to, amount).transact()

def balance_erc(contract, addr):
    c = w3.eth.contract(contract, abi=ERC20_ABI)
    return c.functions.balanceOf(addr).call()

def approve_erc(account, token, contract, amount):
    c = w3.eth.contract(token, abi=ERC20_ABI)
    return c.functions.approve(contract, amount).transact({"from": account.address})

def build_swap(account, dex, token, amount, timeout=10):
    c_dex = w3.eth.contract(dex, abi=DEX_ABI)
    c_erc = w3.eth.contract(token, abi=ERC20_ABI)

    tx_approve = c_erc.functions.approve(dex, amount).build_transaction({"from": account.address, "nonce": w3.eth.get_transaction_count(account.address), "gas": 100_000})
    tx = c_dex.functions.swap(amount, token, int(time.time()) + timeout).build_transaction({"from": account.address, "nonce": w3.eth.get_transaction_count(account.address) + 1, "gas": 200_000})
    
    return account.sign_transaction(tx_approve), account.sign_transaction(tx)

def find_dex_name(t1_name, t2_name):
    names = sorted([t1_name, t2_name])
    return f'{names[0]}-{names[1]}'

class Web3JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        if isinstance(obj, (bytes, bytearray)):
            return "0x" + obj.hex()
        if isinstance(obj, AttributeDict):
            return dict(obj)
        return super().default(obj)
