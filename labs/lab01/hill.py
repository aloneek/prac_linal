import string, sympy as sp


alphabet = list(string.ascii_uppercase+'_!?') ### алфавит из n символов (пункт 1) 
n = len(alphabet)

def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    d, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - y1 * (a // b)
    return d, x, y 

def to_digits(message):
    return [alphabet.index(i) for i in message]

def to_word(message):
    return ''.join([alphabet[i] for x in message for i in x])

def shifr(message,matrix):
    z = matrix.shape[0]
    splitted_message_in_digits = []
    shifred_message_in_digits = []
    for x in range(len(message)//z):
        splitted_message_in_digits.append([message[i] for i in range(x*z,x*z+z)])

    for item in splitted_message_in_digits:
        shifred_message_in_digits.append((matrix*sp.Matrix(item)%n).flat())

    return shifred_message_in_digits

def deshifr(message,matrix):
    z = matrix.shape[0]
    shifred_message_in_digits = []
    deshifred_message_digits = []
    for x in range(len(message)//z):
            shifred_message_in_digits.append([message[i] for i in range(x*z,x*z+z)]) 
    
    
    for item in shifred_message_in_digits:
        deshifred_message_digits.append((matrix*sp.Matrix(item)%n).flat())
    
    return deshifred_message_digits