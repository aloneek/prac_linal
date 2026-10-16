import sympy as sp
import random


from hill import extended_gcd, to_digits, to_word, shifr, deshifr, alphabet, n

random.seed(67) ### сид для рандома чтобы было легко проверять 

m2 = sp.Matrix([[random.randint(0,28),random.randint(0,28)],[random.randint(0,28),random.randint(0,28)]])

while m2.det()%n==0:
    m2 = sp.Matrix([[random.randint(0,28),random.randint(0,28)],[random.randint(0,28),random.randint(0,28)]])

key_m2 = m2.adjugate()*extended_gcd(m2.det(),n)[1]%n

message = 'PRETTY_GIRLS' ### original
message2 = 'STAY_WITH_ME'




shifrd_wrd_digits = shifr(to_digits(message),m2)
sfrd_msg = to_word(shifrd_wrd_digits)
print(f'зашифрованное сообщение 1: {sfrd_msg}')

message_forgotten = '?'*12 ### я 'забыл' сообщение

shifrd_wrd_digits2 = shifr(to_digits(message2),m2)
sfrd_msg_2 = to_word(shifrd_wrd_digits2)
print(f'зашифрованное сообщение 2: {sfrd_msg_2}')


print(f'что мы знаем: message1 = {message_forgotten}, message2 = {message2}')

### решение
### мы имеем лишь message2, sfrd_msg_2 (шифрованное сообщение 2), sfrd_msg (шифрованное сообщение 1), а так же их представления в числах 

### Dx=b, где D - матрица дешиврования (также известная как found_key_m2), обратная матрице m2 по модулю n, x - матрица созданная из первых двух векторов в виде столбцов зашифрованного соообщения 2, b - матрица созданная из первых двух векторов в виде столбцов расшифрованного сообщения 2 


x_matrix = sp.Matrix([shifrd_wrd_digits2[0],shifrd_wrd_digits2[1]]).T ### матрица созданная из первых двух векторов в виде столбцов зашифрованного соообщения 2
if x_matrix.det()%n == 0:
    raise ValueError(f"выберите другие блоки, эти линейно зависимы по модулю {n}")

b_matrix = sp.Matrix([to_digits(message2)[:2],to_digits(message2)[2:4]]).T ### матрица созданная из первых двух векторов в виде столбцов расшифрованного сообщения 2 
x_matrix_inv = x_matrix.adjugate()*extended_gcd(x_matrix.det(),n)[1]%n ### матрица обратная 


found_key_m2 = b_matrix*x_matrix_inv%n
K = found_key_m2.adjugate()*extended_gcd(found_key_m2.det(),n)[1]%n
print(f'найденная матрица ключ: {K}, обратная матрица: {found_key_m2}')

print(f'проверяем независимой проверкой.\nшифруем сообщение 2 с помощью полученного ключа: {to_word(shifr(to_digits(message2),K))}\nзашифрованное с помощью исходного ключа сообщение 2: {sfrd_msg_2}') ### проверка второго сообщения 

message_forgotten = to_word(deshifr(to_digits(sfrd_msg),found_key_m2))
print(f'расшифованное сообщение 1: {message_forgotten}')