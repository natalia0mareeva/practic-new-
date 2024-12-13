#!/usr/bin/python3

import random
import sys

def main():
  try:
    A = int(sys.stdin.read())
    B = random.randint(-10,10)
    Result = A/B
  except ZeroDivisionError:
    print('Ошибка: Попытка деления на 0', file = sys.stderr)
  except ValueError:
    print('Ошибка: Неудача при преобразовании входных данных', file = sys.stderr)
  else:
    print(Result, file = sys.stdout)

if __name__ == "__main__":
  main()
