#!/usr/bin/python3

import sys

def is_valid_name(name):
  return all(char.isalpha() for char in name) and name[0].isupper()

def greet_input(input_line):
  names = input_line.split()
  for name in names:
    if is_valid_name(name):
      print(f'Рад тебя видеть, {name}!')
    else:
      print(f'{name} - некорректное имя', file=sys.stderr) 
        
def main():
  while True:
    if sys.stdin.isatty():
      print('Привет! Представься:')
    try:
      user_input = sys.stdin.readline()
      if not user_input:
        break
      greet_input(user_input)
    except KeyboardInterrupt:
      print('\nПока!')
      break

if __name__ == "__main__":
    main()
