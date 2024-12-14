#!/usr/bin/python3

import sys
import math

def add_message_to_log(message):
  with open('log.txt','a') as log:
    print(message, file=log)

def main():
  try:
    C = float(sys.stdin.read())
    add_message_to_log(f'C = {C}')
    
    Result = math.sqrt(C)
    add_message_to_log(f'C^(1/2) = {Result}')
    
  except ValueError:
    print('Ошибка: Неудача при преобразовании входных данных, ' +
          'ранее была произведена попытка деления на 0 или ' +
          'поступило отрицательное число', file = sys.stderr)
    add_message_to_log('Ошибка: Неудача при преобразовании входных данных, ' +
          'ранее была произведена попытка деления на 0 или ' +
          'поступило отрицательное число')
  else:
    print(Result, file = sys.stdout)
    
if __name__ == "__main__":
  main()  
