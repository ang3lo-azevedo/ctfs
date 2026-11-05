#!/usr/bin/python3
# -*- coding: utf-8 -*-

import base64
import uuid
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import json
import os
from Crypto.Random import get_random_bytes

class AESCipher:
    def __init__(self):
        self.key = get_random_bytes(16)
        self.mode = AES.MODE_CBC
        self.block_size = 16

    def encrypt(self, msg):
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, self.mode, iv)
        ciphertext = cipher.encrypt(pad(msg, self.block_size))
        return iv + ciphertext

    def decrypt(self, ciphertext):
        assert len(ciphertext) % self.block_size == 0

        iv = ciphertext[:self.block_size]
        cipher = AES.new(self.key, self.mode, iv)
        plaintext = unpad(cipher.decrypt(ciphertext[self.block_size:]), self.block_size)
        return plaintext


def menu():
    print('''
Bem vindo ao sistema de storage autenticado do CSCPT.
Por favor introduza uma das seguintes opcoes:

store - Para guardar uma mensagem
read  - Para ler uma mensagem previamente guardada
exit  - Para sair
''')


def store():
    print("Introduza os seguintes dados:")
    username = input("nome de utilizador: ")
    mensagem = input("mensagem a guardar: ")
    comentario = input("comentarios a guardar com a mensagem: ")

    base_folder = f'{os.getcwd()}/files'
    new_folder = f"./files/{username}"

    if os.path.commonprefix((os.path.realpath(new_folder),base_folder)) != base_folder or "admin" in username:
        print("Aqui nao toleramos intrusos. Adeus.")
        exit()

    if not os.path.exists(new_folder):
        os.mkdir(new_folder)
    
    ficheiro = uuid.uuid4()
    while os.path.exists(f"{new_folder}/{ficheiro}"):
        ficheiro = uuid.uuid4()

    f = open(f"{new_folder}/{ficheiro}","w+")
    f.write(json.dumps({"msg" : mensagem, "comment": comentario}))
    f.close()
    
    sig = aes.encrypt(str(ficheiro).encode())

    result = json.dumps({"username" : username, "filename": str(ficheiro), "comment": comentario, "sig" : base64.b64encode(sig).decode()})
    
    print(f'Ficheiro criado:\n{result}')
    return result


def read():
    print("Introduza os seguintes dados para a mensagem a ler:")
    username = input("nome de utilizador: ")
    filename = input("nome do ficheiro: ")
    sig = input("assinatura: ")
    
    sig = base64.b64decode(sig.encode())

    base_folder = f'{os.getcwd()}/files'
    requested_file = f"files/{username}/{filename}"

    if os.path.commonprefix((os.path.realpath(requested_file),base_folder)) != base_folder:
        print("Aqui nao toleramos intrusos. Adeus.")
        exit()

    try:
        if aes.decrypt(sig) != filename.encode():
            print("Assinatura invalida")
            return
    except:
        return
        
    if not os.path.exists(requested_file):
        print("Ficheiro inexistente")
        return

    f = open(requested_file, "r")
    content = f.read()
    f.close()

    print(f'O conteudo do ficheiro é:\n{content}')
    
    return content


aes = AESCipher()

if not os.path.exists(f"./files/"):
    os.mkdir(f"./files/")

while True:
    menu()
    option = input(">>> ")
    if option == "store":
        result = store()
    elif option == "read":
        content = read()
    elif option == "exit":
        break
    else:
        print("Opção Inválida")
