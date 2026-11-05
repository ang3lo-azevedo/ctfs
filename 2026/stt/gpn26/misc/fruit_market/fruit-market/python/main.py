from utils import gen_account, deploy_erc, transfer_erc, deploy_dex, balance_erc, give_money, w3, Web3JSONEncoder, NODE_URL
from web3 import Web3
from flask import Flask, request, redirect, Response, jsonify
from flask_socketio import SocketIO
from trader import Trader
import time
import threading
import requests
import json
import os

def setup():
    """
        Setup ERC and DEXes
    """
    creator_acct = gen_account()
    w3.eth.default_account = creator_acct.address

    CONTRACT_APPLE = deploy_erc("APPLE", "APL")
    CONTRACT_BANANA = deploy_erc("BANANA", "BAN")
    CONTRACT_CHERRY = deploy_erc("CHERRY", "CHY")

    ACCT_A = gen_account()
    ACCT_B = gen_account()
    ACCT_C = gen_account()

    dist = [
        (CONTRACT_APPLE,  [400, 250, 140]),
        (CONTRACT_BANANA, [100, 400, 200]),
        (CONTRACT_CHERRY, [100,  50, 250])
    ]
    for (c, amount) in dist:
        transfer_erc(c, ACCT_A.address, amount[0])
        transfer_erc(c, ACCT_B.address, amount[1])
        transfer_erc(c, ACCT_C.address, amount[2])

    DEX_APPLE_BANANA = deploy_dex(creator_acct, CONTRACT_APPLE, 100, CONTRACT_BANANA, 200)
    DEX_BANANA_CHERRY = deploy_dex(creator_acct, CONTRACT_BANANA, 100, CONTRACT_CHERRY, 200)
    DEX_APPLE_CHERRY = deploy_dex(creator_acct, CONTRACT_APPLE, 100, CONTRACT_CHERRY, 400)

    return {
        'accounts': [ACCT_A.address, ACCT_B.address, ACCT_C.address],
        'ercs': {
            'APL': CONTRACT_APPLE, 
            'BAN': CONTRACT_BANANA, 
            'CHY': CONTRACT_CHERRY,
        },
        'dexes': {
            'APL-BAN': DEX_APPLE_BANANA,
            'APL-CHY': DEX_APPLE_CHERRY,
            'BAN-CHY': DEX_BANANA_CHERRY
        }
    }, [ACCT_A, ACCT_B, ACCT_C]


ETH_SETUP, ETH_ACCOUNTS = setup()
TRADERS = [Trader(x, ETH_SETUP) for x in ETH_ACCOUNTS]
MANAGER = None

app = Flask(__name__, static_folder='../html', static_url_path='')
socketio = SocketIO(app, cors_allowed_origins="*")

def background_worker():
    """
        This worker lets our traders do trades, which we emit via Socket-IO.
    """
    with app.app_context():
        while True:
            for t in TRADERS:
                txs = t.next()
                if txs is not None:
                    socketio.emit('new_trade', {
                        'approve': txs[0].raw_transaction.hex(),
                        'swap': txs[1].raw_transaction.hex(),
                        'swap_hash': '0x' + txs[1].hash.hex()
                    })
        
            time.sleep(1)

background_thread = threading.Thread(target=background_worker, daemon=True)

@app.route("/setup")
def accounts():
    return ETH_SETUP

@app.route("/open")
def open():
    """
        Open the market (aka: happy trading!)
    """
    if not background_thread.is_alive():
        background_thread.start()
        return "OK"
    else:
        return "already running", 400

@app.post("/submit")
def submit():
    """
        Execute a new transaction (sent as rawtx) on-chain.
    """
    rawtx = request.form['rawtx']
    try:
        sender = w3.eth.account.recover_transaction(rawtx)
        tx_hash = w3.eth.send_raw_transaction(rawtx)
        return {"tx_hash": tx_hash.hex(), "sender": sender}, 200
    except Exception as e:
        print(e)
        return "error", 400

@app.post("/fruit-basket")
def fruit_basket():
    """
        Our employee fruit basket. Gives the specified account 10 apples.
    """
    global MANAGER
    if MANAGER is not None:
        return "already claimed, back to work!", 403
    
    addr = request.form['address']
    if not Web3.is_address(addr) or not Web3.is_checksum_address(addr):
        return "not an address", 400

    if addr in ETH_SETUP['accounts'] or addr in ETH_SETUP['dexes'].values() or addr in ETH_SETUP['ercs'].values():
        return "that's certainly not you", 400

    give_money(addr)
    transfer_erc(ETH_SETUP['ercs']['APL'], addr, 10)
    MANAGER = addr

    return "OK"


@app.get("/flag")
def flag():
    """
        Hands out the flag if the account has more than 500 APL.
    """
    global MANAGER
    if MANAGER is None:
        return "first get your free apples from our fruit basket!", 403
    
    if not Web3.is_address(MANAGER) or not Web3.is_checksum_address(MANAGER):
        return "not an address", 400
    
    if balance_erc(ETH_SETUP['ercs']['APL'], MANAGER) >= 500:
        return "Wow! Here is your flag:\n" + os.environ.get('FLAG', 'this_is_a_dummy_flag')
    else:
        return "Work harder!", 403

@app.get("/balance/<pubkey>")
@app.get("/balance", defaults={'pubkey': None})
def balance(pubkey):
    """
        Shortcut to find out how much APL/BAN/CHY an account (or the traders) have.
    """
    if pubkey is None:
        ret = {}

        for pubkey in ETH_SETUP['accounts']:
            ret[pubkey] = {
            'APL': balance_erc(ETH_SETUP['ercs']['APL'], pubkey),
            'BAN': balance_erc(ETH_SETUP['ercs']['BAN'], pubkey),
            'CHY': balance_erc(ETH_SETUP['ercs']['CHY'], pubkey),
        }
            
        return ret
    
    else:
        if not Web3.is_address(pubkey) or not Web3.is_checksum_address(pubkey):
            return "not an address", 400
        
        return {
            'APL': balance_erc(ETH_SETUP['ercs']['APL'], pubkey),
            'BAN': balance_erc(ETH_SETUP['ercs']['BAN'], pubkey),
            'CHY': balance_erc(ETH_SETUP['ercs']['CHY'], pubkey),
        }

@app.get("/")
def index():
    return redirect("/index.html")

SAFE_METHODS = frozenset({
    "eth_blockNumber", "eth_chainId", "eth_getBlockByHash", "eth_getBlockByNumber",
    "eth_getTransactionByHash", "eth_getTransactionReceipt", "eth_getTransactionCount",
    "eth_getBalance", "eth_getCode", "eth_getStorageAt", "eth_getProof", "eth_maxPriorityFeePerGas",
    "eth_call", "eth_estimateGas", "eth_gasPrice", "eth_feeHistory", "eth_getLogs",
    "net_version", "web3_clientVersion", "eth_syncing"
})

@app.post("/")
def rpc_proxy():
    """
        Proxy safe methods to Ethereum node.
    """
    def error(req_id, code, message):
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}
    
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or body.get("jsonrpc") != "2.0":
        return jsonify(error(None, -32600, "Invalid request")), 400

    method = body.get("method")
    if not isinstance(method, str) or method not in SAFE_METHODS:
        return jsonify(error(body.get("id"), -32601, "Method not permitted")), 200

    print(method)

    try:
        resp = requests.post(NODE_URL, json=body, timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json()), 200
    except requests.RequestException:
        return jsonify(error(body.get("id"), -32603, "Upstream node error")), 502

app.run(debug=False, host='0.0.0.0')