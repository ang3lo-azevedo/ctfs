import os
from key_generator import RSA_key_gen
import base64


with open('flag.txt', 'r') as f:
    flag = f.read().strip()


def serve():
    public_key = RSA_key_gen()
    print "Queres saber o segredo mais bem guardado do CSC PT?"
    print "Ora aqui vai.\n"
    print base64.b64encode(public_key.encrypt(flag, None)[0]), '\n'
    print "De certeza que consegues decifrar a mensagem.\n"
    print public_key.exportKey(), '\n'
    print "BOA SORTE!"
    

if __name__ == '__main__':
    serve()
