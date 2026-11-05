from Crypto.Util.number import *
from pwn import xor 
from flag import FLAG


p1 = getPrime(512)
q1 = getPrime(512)
BITS = 2**512

def generate_prime(p, q, start):
    ''' Given two primes p, q, generate a third one without any need for entropy sources!'''
    i = start
    while 1:
        i += 1
        r = (pow(p, i, BITS) ^ pow(q, i, BITS)) + 1
        if isPrime(r):
            return r, i
        
p2, k = generate_prime(p1, q1, 0)
q2, l = generate_prime(p1, q1, k+1)

N1 = p1*q1
N2 = p2*q2
e = 65537

print('N1 =', N1)
print('N2 =', N2)
print('c =', pow(FLAG, e, N1))
print('And its fast too, only took', l,'iterations in total to generate two primes!')
