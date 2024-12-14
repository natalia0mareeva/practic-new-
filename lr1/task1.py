#!/usr/bin/python3

import random
import sys


def add_message_to_log(message):
  with open('log.txt','a') as log:
    print(message, file=log)
  

def main():
  A = random.randint(-10, 10)
  add_message_to_log(f'\n\nA = {A}')
  
  print(A, file = sys.stdout)
  

if __name__ == "__main__":
  main()
