#!/usr/bin/python3

import sys
import math

def main():
  try:
    C = float(sys.stdin.read())
    if C < 0:
      raise Exception('Ошибка: Попытка взять корень отрицательного числа')
  except ValueError:
    print('Ошибка: Неудача при преобразовании входных данных, ' +
          'ранее была произведена попытка деления на 0', file = sys.stderr)
  except Exception as e:
    print(e, file = sys.stderr)
  else:
    print(math.sqrt(C), file = sys.stdout)
    
if __name__ == "__main__":
  main()  
