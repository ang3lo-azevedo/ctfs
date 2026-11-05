from utils import balance_erc, build_swap, find_dex_name, w3
import time
import random

class Trader:
    def __init__(self, account, setup):
        self.account = account
        self.next_timestamp = None
        self.last_hash = None
        self.missed_tx = 0
        self.setup = setup

    def balance(self):
        return {
            'APL': balance_erc(self.setup['ercs']['APL'], self.account.address),
            'BAN': balance_erc(self.setup['ercs']['BAN'], self.account.address),
            'CHY': balance_erc(self.setup['ercs']['CHY'], self.account.address)
        }
    
    def has_next(self):
        if self.missed_tx >= 3:
            # traders don't like when their trades fail!
            return False
        
        return self.next_timestamp is None or time.time() >= self.next_timestamp
    
    def next(self):
        if not self.has_next():
            return None
        
        if self.last_hash is not None:
            try:
                receipt = w3.eth.get_transaction_receipt(self.last_hash)
                if receipt['status'] != 1:
                    print("TX", self.last_hash.hex(), "not successful!")
                    self.missed_tx += 1
            except:
                print("TX", self.last_hash.hex(), "not published!")
                self.missed_tx += 1

        # Ultimate Trading Strategy: 
        # Take what you have most of, and swap it with something else!
        balance = self.balance()
        trade_token = max(balance, key=balance.get)
        
        if balance[trade_token] == 0:
            return None # nothing to trade!
    
        trade_amount = max(int(balance[trade_token] * 0.5), 1)
        trade_target = random.choice(list(set(['APL', 'BAN', 'CHY']) - set([trade_token])))

        expires = random.randint(2,10)
        self.next_timestamp = time.time() + expires
        txs = build_swap(self.account, self.setup['dexes'][find_dex_name(trade_token, trade_target)], self.setup['ercs'][trade_token], trade_amount, timeout=expires)
        self.last_hash = txs[1].hash
        return txs