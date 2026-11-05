from Crypto.Cipher import AES
import base64
import json
import random, os


with open('flag', 'r') as f:
    flag = f.read().strip()


class AESCipher(object):
    def __init__(self, key): 
        self.BLOCK_SIZE = 16
        self.key = key

    def encrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_ECB)

        ptext = self._pad(raw)
        return cipher.encrypt(ptext)

    def decrypt(self, raw):
        cipher = AES.new(self.key, AES.MODE_ECB)

        try:
            ptext = self._unpad(cipher.decrypt(raw))
            return ptext
        except:
            return b'0'


    def _pad(self, data):
        size = self.BLOCK_SIZE - (len(data) % self.BLOCK_SIZE)
        return data + bytearray([size] * size)

    def _unpad(self, data):
        size = data[-1]
        assert all(map(lambda x: x == size, data[-size:]))
        return data[:-size]


c = AESCipher(os.urandom(16))


def initiate(player):
    print(f"\nWelcome {player}. Do you want to play with us?")
    print("We usually only take billionaires, but we open an exception for you")
    print("Here is some seed tokens for you to start")
    
    wallet = json.dumps({"value": 100000, "player": player}).encode()
    sig = c.encrypt(wallet)

    print(f"Here is your wallet: {wallet.decode()}")
    print(f"Here is the signature: {base64.b64encode(sig).decode()}")
    
    return wallet, sig


def play(wallet, sig, bet):
    if c.decrypt(base64.b64decode(sig)).decode() != wallet:
        print("Invalid signature")
        return None, None
    w = json.loads(wallet)
    if w['value'] < bet:
        print("Not enough tokens for that bet")
        return None, None
    elif w['value'] < 0:
        print("Invalid bet")
        return None, None
    else:
        print("Let's play!")
        if random.random() < 0.49:
            print("You lost")
            w['value'] -= bet
        else:
            print("You win")
            w['value'] += bet

        wallet = json.dumps(w).encode()
        sig = c.encrypt(wallet)

        print(f"Here is your wallet: {wallet.decode()}")
        print(f"Here is the signature: {base64.b64encode(sig).decode()}")
    
        return wallet, sig


def get_prize(wallet, sig):
    if c.decrypt(base64.b64decode(sig)).decode() != wallet:
        print("Invalid signature")
        return 0
    w = json.loads(wallet)
    if w['value'] >= 1000000000:
        print(f"Here is the flag: {flag}")
        exit(0)
    else:
        print(f"Here is this nice gift for you: https://tinyurl.com/mt5afms5")
    



def menu():
    print('''
Which option do you want to take?
(1) Bet some of your tokens
(2) Get a fancy prize
(3) Say goodbye!''')
    return int(input(">>> "))
    

def main():
    player = input("Hello sir. What is your name?\n")
    initiate(player)

    while True:
        option = menu()

        if option == 1:
            wallet = input("\nSend me your wallet\n>>> ")
            sig = input("\nSend me the signature of your wallet?\n>>> ")
            bet = int(input("\nHow many tokens do you want to bet?\n>>> "))
            play(wallet, sig, bet)
        
        elif option == 2:
            wallet = input("\nSend me your wallet\n>>> ")
            sig = input("\nSend me the signature of your wallet?\n>>> ")
            get_prize(wallet, sig)

        elif option == 3:
            exit(0)



if __name__ == "__main__":
    main()