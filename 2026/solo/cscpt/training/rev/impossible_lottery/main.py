#!/bin/python3

import os, random
from bitstring import BitArray

secret = os.urandom(8)
flag = os.environ['flag']

class Generator:
  def __init__(self, s):
    self.secret = secret
    self.round = 0

  def next(self):
    next = [((self.secret[i] >> self.round) & 1) for i in range(8)]
    next = BitArray(next[self.round:] + next[:self.round]).uint
    self.round += 1
    return next

def main():
  g = Generator(secret)

  lucky = random.randint(0,255)

  print(f"Your lucky number is {lucky}.\n\nAnd the lottery is....\n")

  for i in range(8):
      print(f"Draw number {g.round + 1}: {g.next() ^ lucky}")

  guess = input("What is the original secret (hex-encoded)? ")

  if guess == secret.hex():
      print(f"You win: {flag}")
  else:
      print(f"Not this time")


if __name__ == "__main__":
    main()
