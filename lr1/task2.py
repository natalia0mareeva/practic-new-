#!/usr/bin/python3

import random
import sys

def add_message_to_log(message):
  with open('log.txt','a') as log:
    print(message, file=log)
  

def main():
  try:
    A = int(sys.stdin.read())
    B = random.randint(-10,10)
    add_message_to_log(f'A = {A}, B = {B}')
    
    Result = A/B
    add_message_to_log(f'A/B = {Result}')
    
  except ZeroDivisionError:
    print('Ошибка: Попытка деления на 0', file = sys.stderr)
    add_message_to_log('Ошибка: Попытка деления на 0')
  except ValueError:
    print('Ошибка: Неудача при преобразовании входных данных', file = sys.stderr)
    add_message_to_log('Ошибка: Неудача при преобразовании входных данных')
  else:
    print(Result, file = sys.stdout)

if __name__ == "__main__":
  main()
